from abc import ABC
from typing import Dict, Any
import time
import re

import xarray as xr
import rioxarray
import numpy as np
import torch
from torchvision.transforms import v2
from torchvision import tv_tensors


from torch.utils.data import IterableDataset, Dataset

from ..modules.indices import ndvi, gci, hue
from ..modules.utils import dilate_img, get_rioxarray_trafo

import logging

log = logging.getLogger(__name__)


class TreeCrownDelineationBaseDataset(ABC):
    """
    In-memory remote sensing dataset for image segmentation.

    This base dataset class handles the loading and preprocessing of raster and target files for
    tree crown delineation, and image segmentation task.

    Parameters:
    - raster_files (list[str]): List of file paths to the raster images.
    - target_files (list[str]): List of file paths to the target images.
    - augmentation (Dict[str, Any]): Dictionary containing augmentation configurations.
    - ndvi_config (Dict[str, Any], optional): Configuration for NDVI, default is {'concatenate': False}.
    - dilate_outlines (int, optional): Number of pixels to dilate the outlines, default is 0.
    - overwrite_nan_with_zeros (bool, optional): Whether to overwrite NaN values with zeros, default is True.
    - in_memory (bool, optional): Whether to load the data into memory, default is False.
    - dim_ordering (str, optional): Dimension ordering, default is "CHW".
    - dtype (str, optional): Data type of the raster images, default is "float32".
    - divide_by (int, optional): Value to divide the raster data by, default is 1.
    """

    def __init__(
        self,
        raster_files: list[str],
        target_files: list[str],
        augmentation: Dict[str, Any],
        ndvi_config: Dict[str, Any] = {"concatenate": False},
        gci_config: Dict[str, Any] = {"concatenate": False},
        hue_config: Dict[str, Any] = {"concatenate": False},
        dilate_outlines: int = 0,
        overwrite_nan_with_zeros: bool = True,
        in_memory: bool = False,
        dim_ordering="CHW",
        dtype="float32",
        divide_by=1,
    ):
        """__init__

        Creates a dataset containing images and targets (masks, outlines, and distance_transforms).

        Args:
            raster_files (list[str]): List of file paths to source rasters. File names must be of the form '.../the_name_i.tif' where i is some index
            target_files (list[str]): mask_files: A tuple containing lists of file paths to different sorts of 'masks', e.g. mask, outline, distance transform.
                  The mask and raster file names must have the same index ending.
            augmentation (Dict[str, Any]): Dictionary defining augmentations. Keys correspond to torchvision transforms, values to their kwargs.
            ndvi_config (_type_, optional): Dictionary defining NDVI concatenation. Defaults to {'concatenate': False}.
            dilate_outlines (int, optional): If present, dilate outlines by give amount of pixels. Defaults to 0.
            overwrite_nan_with_zeros (bool, optional): If True, fill missing values in targets with 0. Defaults to True.
            in_memory (bool, optional): If True, load all rasters and targets into memory (works for small datasets, beware of OOM error). Defaults to True.
            dim_ordering (str, optional): Order of dimensions. Defaults to "CHW".
            dtype (str, optional): torch Datatype. Defaults to "float32".
            divide_by (int, optional): Scalar to divide the raster pixel values by. Defaults to 1.
        """

        # initial sanity checks
        assert len(raster_files) > 0, "List of given rasters is empty."

        self.raster_files = raster_files
        self.target_files = target_files
        self.divide_by = divide_by
        self.augmentation = augmentation
        self.ndvi_config = ndvi_config
        self.gci_config = gci_config
        self.hue_config = hue_config
        self.dilate_outlines = dilate_outlines
        self.in_memory = in_memory
        self.overwrite_nan = overwrite_nan_with_zeros
        self.dtype = dtype

        self.dim_ordering = dim_ordering
        if dim_ordering == "CHW":
            self.chax = 0  # channel axis of imported arrays
        elif dim_ordering == "HWC":
            self.chax = 2
        else:
            raise ValueError(
                "Dim ordering {} not supported. Choose one of 'CHW' or 'HWC'.".format(
                    dim_ordering
                )
            )
        self.lateral_ax = np.array((1, 2)) if self.chax == 0 else np.array((0, 1))

        # load all rasters and targets into memory
        if self.in_memory:
            t0 = time.time()
            log.info("Loading all data into memory")
            self.load_data()
            log.info(
                f"Finished loading data into memory in {time.time()-t0:.1f} seconds."
            )

        # add augmentation functions
        # FIXME we need to cut and rotate rasters and targets in the same way, but we should only scale the rasters and not the targets!
        raster_transforms = []
        target_transforms = []
        joint_transforms = []
        for key, val in self.augmentation.items():
            log.info(f"Adding augmentation {key} with parameter {val}")
            match key:
                case "RandomResizedCrop":
                    joint_transforms.append(v2.RandomResizedCrop(**val))
                    self.cutout_size = (val["size"], val["size"])
                case "RandomCrop":
                    joint_transforms.append(v2.RandomCrop(**val))
                    self.cutout_size = (val["size"], val["size"])
                case "Resize":
                    joint_transforms.append(v2.Resize(**val))
                    self.cutout_size = (val["size"], val["size"])
                case "RandomHorizontalFlip":
                    joint_transforms.append(v2.RandomHorizontalFlip(**val))
                case "RandomVerticalFlip":
                    joint_transforms.append(v2.RandomVerticalFlip(**val))
                case "ColorJitter":
                    raise NotImplementedError("Augmentation not implemented:", key)
                case "Normalize":  # applies only to rasters
                    raster_transforms.append(v2.Normalize(**val))
                case "Pad":
                    raster_transforms.append(v2.Pad(**val))
                case _:
                    raise ValueError(f"Augmentation not defined: {key}")
        if len(joint_transforms) == 0:
            lc = lambda x: x
            joint_transforms.append(v2.Lambda(lc))
        raster_transforms.append(v2.ToDtype(dtype=torch.float32))
        self.augment_joint = v2.Compose(joint_transforms)

        if len(target_transforms) > 0:
            self.augment_target = v2.Compose(target_transforms)
        else:
            self.augment_target = None

        self.augment_raster = v2.Compose(raster_transforms)

    def load_raster(self, file: str, used_bands: list = None):
        """Loads a raster from disk.

        Args:
            file (str): file to load
            used_bands (list): bands to use, indexing starts from 0, default 'None' loads all bands

        Returns:
            raster
        """
        raster = rioxarray.open_rasterio(
            file
        ).load()  # xarray.open_rasterio is deprecated
        # raise Error when infrared is missing
        RGBI_CHANNEL_NUMS = 4
        ACTUAL_CHANNEL_NUMS = len(raster.coords["band"].values)
        if ACTUAL_CHANNEL_NUMS != RGBI_CHANNEL_NUMS:
            raise ValueError(
                f"Only got {ACTUAL_CHANNEL_NUMS} bands ({RGBI_CHANNEL_NUMS} expected): {file}"
            )

        if self.dim_ordering == "CHW":
            raster = raster.transpose("band", "y", "x")
        elif self.dim_ordering == "HWC":
            raster = raster.transpose("y", "x", "band")

        if used_bands is not None:
            raster = raster.isel(bands=used_bands)

        # need to normalize before concatenating NDVI
        raster = raster / self.divide_by

        if self.ndvi_config["concatenate"]:
            raster = self.concatenate_ndvi_to_raster(
                raster,
                red=self.ndvi_config["red"],
                nir=self.ndvi_config["nir"],
                dim_ordering=self.dim_ordering,
                rescale=self.ndvi_config["rescale"],
            )
        if self.gci_config["concatenate"]:
            raster = self.concatenate_gci_to_raster(
                raster,
                red=self.gci_config["red"],
                green=self.gci_config["green"],
                nir=self.gci_config["nir"],
                dim_ordering=self.dim_ordering,
                rescale=self.gci_config["rescale"],
            )
        if self.hue_config["concatenate"]:
            raster = self.concatenate_hue_to_raster(
                raster,
                red=self.hue_config["red"],
                green=self.hue_config["green"],
                blue=self.hue_config["blue"],
                dim_ordering=self.dim_ordering,
                rescale=self.hue_config["rescale"],
            )

        return raster

    def load_target(self, file: str) -> xr.Dataset | xr.DataArray:
        """Load target  raster from disk.

        Args:
            file (str): path to file.

        Returns:
            xr.Dataset or xr.DataArray: Raster.
        """
        target = rioxarray.open_rasterio(file).load()

        if self.dim_ordering == "CHW":
            target = target.transpose("band", "y", "x")
        elif self.dim_ordering == "HWC":
            target = target.transpose("y", "x", "band")

        if self.overwrite_nan:
            target = target.fillna(0.0)

        return target

    def load_data(self):
        """Load and preprocess data from files into memory."""
        self.rasters = []
        for raster_file in self.raster_files:
            self.rasters.append(self.load_raster(raster_file))

        self.targets = []
        for files in zip(*self.target_files):
            targets = [self.load_target(f) for f in files]
            # "override" ensures that small differences in geotransorm are neglected
            target = xr.concat(targets, dim="band", join="override")
            # dilate masks
            if self.dilate_outlines:
                if self.dim_ordering == "CHW":
                    target[1, :, :] = dilate_img(target[1, :, :], self.dilate_outlines)
                elif self.dim_ordering == "HWC":
                    target[:, :, 1] = dilate_img(target[:, :, 1], self.dilate_outlines)

            self.targets.append(target)

    @staticmethod
    def concatenate_ndvi_to_raster(
        raster: xr.Dataset,
        red: int = 0,
        nir: int = 3,
        dim_ordering: str = "CHW",
        rescale: bool = False,
    ) -> xr.Dataset:
        """concatenate_ndvi_to_raster

        Concatenate NDVI to the raster.

        Args:
            raster (xr.Dataset): loaded raster tile
            red (int, optional): Index of red channel in raster bands. Defaults to 0.
            nir (int, optional): Index of NIR channel in raster bands. Defaults to 3.
            rescale (bool, optional): Rescale NDVI to [0, 1]. Defaults to False.

        Returns:
            xr.Dataset: _description_
        """
        if dim_ordering == "CHW":
            chax = 0
        elif dim_ordering == "HWC":
            chax = 2
        else:
            raise ValueError("Invalid dim_ordering: ", dim_ordering)

        ndvi_band = ndvi(raster, red, nir, axis=chax).expand_dims(dim="band", axis=chax)
        if rescale:
            ndvi_band = (ndvi_band + 1.0) / 2.0
        ndvi_band = ndvi_band.assign_coords({"band": [len(raster.band) + 1]})
        raster = xr.concat((raster, ndvi_band), dim="band")

        return raster

    @staticmethod
    def concatenate_gci_to_raster(
        raster: xr.Dataset,
        red: int = 0,
        green: int = 1,
        nir: int = 3,
        dim_ordering: str = "CHW",
        rescale: bool = False,
    ) -> xr.Dataset:
        """concatenate_gci_to_raster

        Concatenate GCI to the raster.

        Args:
            raster (xr.Dataset): loaded raster tile
            red (int, optional): Index of red channel in raster bands. Defaults to 0.
            green (int, optional): Index of green channel in raster bands. Defaults to 1.
            nir (int, optional): Index of NIR channel in raster bands. Defaults to 3.
            rescale (bool, optional): Rescale GCI to [0, 1]. Defaults to False.

        Returns:
            xr.Dataset: _description_
        """
        if dim_ordering == "CHW":
            chax = 0
        elif dim_ordering == "HWC":
            chax = 2
        else:
            raise ValueError("Invalid dim_ordering: ", dim_ordering)
        gci_band = gci(raster, red, green, nir, axis=chax).expand_dims(
            dim="band", axis=chax
        )
        if rescale:
            gci_band = (gci_band + 1.0) / 2.0
        gci_band = gci_band.assign_coords({"band": [len(raster.band) + 1]})
        raster = xr.concat((raster, gci_band), dim="band")
        return raster

    @staticmethod
    def concatenate_hue_to_raster(
        raster: xr.Dataset,
        red: int = 0,
        green: int = 1,
        blue: int = 2,
        dim_ordering: str = "CHW",
        rescale: bool = False,
    ) -> xr.Dataset:
        """concatenate_hue_to_raster

        Concatenate hue to the raster.

        Args:
            raster (xr.Dataset): loaded raster tile
            red (int, optional): Index of red channel in raster bands. Defaults to 0.
            green (int, optional): Index of green channel in raster bands. Defaults to 1.
            blue (int, optional): Index of blue channel in raster bands. Defaults to 2.
            rescale (bool, optional): Rescale hue to [0, 1]. Defaults to False.

        Returns:
            xr.Dataset: _description_
        """
        if dim_ordering == "CHW":
            chax = 0
        elif dim_ordering == "HWC":
            chax = 2
        else:
            raise ValueError("Invalid dim_ordering: ", dim_ordering)
        hue_band = hue(raster, red, green, blue, axis=chax).expand_dims(
            dim="band", axis=chax
        )
        if rescale:
            hue_band = (hue_band + 1.0) / 2.0
        hue_band = hue_band.assign_coords({"band": [len(raster.band) + 1]})
        raster = xr.concat((raster, hue_band), dim="band")
        return raster


class TreeCrownDelineationDataset(TreeCrownDelineationBaseDataset, IterableDataset):
    """
    Iterable TreeCrownDelineation dataset.

    Yields samples from all rasters until, statistically, each pixel has been
    covered once. If the raster edge length exceeds the sample edge length,
    this implies that multiple samples can be sampled from one raster.
    """

    def __init__(
        self,
        raster_files: list[str],
        target_files: list[str],
        augmentation: Dict[str, Any],
        ndvi_config: Dict[str, Any] = {"concatenate": False},
        gci_config: Dict[str, Any] = {"concatenate": False},
        hue_config: Dict[str, Any] = {"concatenate": False},
        dilate_outlines: int = 0,
        overwrite_nan_with_zeros: bool = True,
        in_memory: bool = True,
        dim_ordering="CHW",
        dtype="float32",
        divide_by=1,
    ):
        super().__init__(
            raster_files=raster_files,
            target_files=target_files,
            augmentation=augmentation,
            ndvi_config=ndvi_config,
            gci_config=gci_config,
            hue_config=hue_config,
            dilate_outlines=dilate_outlines,
            overwrite_nan_with_zeros=overwrite_nan_with_zeros,
            in_memory=in_memory,
            dim_ordering=dim_ordering,
            dtype=dtype,
            divide_by=divide_by,
        )

        # Check that raster ID matches target ID - only in iterable dataset used in training!
        for i, m in enumerate(target_files):
            if len(m) == 0:
                raise RuntimeError("Mask list {} is empty.".format(i))
            if len(m) != len(raster_files):
                raise RuntimeError("The length of the given lists must be equal.")
            for j, r in enumerate(raster_files):
                raster_file_index = re.search(r"(_\d+_\d+.tif)", r).group()
                if not m[j].endswith(raster_file_index):
                    print(r, m[j])
                    raise RuntimeError(
                        f"The raster and mask lists must be sorted equally."
                    )

    def __len__(self):
        """Length of the dataset.

        For this iterable dataset, we can define a length that stops the iteration.

        Here, we define the length as the total pixels divided by the cutout (sample)
        pixels. This implies that, on average, each pixel has been included once
        in a sample.

        Returns:
            int: Prescribed dataset length.
        """
        # sum of product of all raster sizes
        total_pixels = np.sum(
            [np.prod(np.array(r.shape)[self.lateral_ax]) for r in self.rasters]
        )
        # product of the shape of cutout done by the transformation
        cutout_pixels = np.prod(np.array(self.cutout_size))
        return int(total_pixels / cutout_pixels)

    def __iter__(self):
        """Iterate the dataset and yield a sample.

        A sample is a cutout of an original raster file, can include augmentations.

        Yields:
            torch.Tensor: raster
            torch.Tensor: target (mask, outline, and distance transform stacked)
        """
        i = 0
        while i < len(self):
            idx = np.random.choice(np.arange(len(self.rasters)))
            if self.in_memory:  # retrieve preloaded tiles
                raster = self.rasters[idx].data
                target = self.targets[idx].data
            else:  # load from disk
                raster = self.load_raster(self.raster_files[idx])
                target = self.load_target(self.target_files[idx])

            # Check for NaN and Inf values before proceeding
            if np.isnan(raster).any() or np.isinf(raster).any():
                log.warning(
                    f"Found NaN or Inf in raster from index {idx}, file: {self.raster_files[idx]}"
                )
                # Fix the NaNs by replacing with zeros or interpolation
                raster = np.nan_to_num(raster, nan=0.0, posinf=0.0, neginf=0.0)

            if np.isnan(target).any() or np.isinf(target).any():
                log.warning(
                    f"Found NaN or Inf in target from index {idx}, file: {self.target_files[idx]}"
                )
                # Fix the NaNs in targets
                target = np.nan_to_num(target, nan=0.0, posinf=0.0, neginf=0.0)

            raster = tv_tensors.Image(raster, dtype=torch.float32)
            target = tv_tensors.Mask(target, dtype=torch.float32)

            # Apply augmentations
            raster, target = self.augment_joint(raster, target)
            raster = self.augment_raster(raster)
            if self.augment_target is not None:
                target = self.augment_target(target)

            # Check again after augmentation
            if torch.isnan(raster).any() or torch.isinf(raster).any():
                log.warning(
                    f"Found NaN or Inf in raster after augmentation from index {idx}"
                )
                raster = torch.nan_to_num(raster, nan=0.0, posinf=0.0, neginf=0.0)

            if torch.isnan(target).any() or torch.isinf(target).any():
                log.warning(
                    f"Found NaN or Inf in target after augmentation from index {idx}"
                )
                target = torch.nan_to_num(target, nan=0.0, posinf=0.0, neginf=0.0)

            i += 1
            yield raster, target


class TreeCrownDelineationInferenceDataset(TreeCrownDelineationBaseDataset, Dataset):
    """
    Map-style ("standard") dataset for the TreeCrownDelineation data.

    This dataset is used for inference and returns complete rasters along with selected metadata.

    Parameters:
    - raster_files (list[str]): List of file paths to the raster images.
    - augmentation (Dict[str, Any]): Dictionary containing augmentation configurations.
    - ndvi_config (Dict[str, Any], optional): Configuration for NDVI, default is {'concatenate': False}.
    - dilate_outlines (int, optional): Number of pixels to dilate the outlines, default is 0.
    - overwrite_nan_with_zeros (bool, optional): Whether to overwrite NaN values with zeros, default is True.
    - in_memory (bool, optional): Whether to load the data into memory, default is False.
    - dim_ordering (str, optional): Dimension ordering, default is "CHW".
    - dtype (str, optional): Data type of the raster images, default is "float32".
    - divide_by (int, optional): Value to divide the raster data by, default is 1.
    """

    def __init__(
        self,
        raster_files: list[str],
        augmentation: Dict[str, Any],
        ndvi_config: Dict[str, Any] = {"concatenate": False},
        gci_config: Dict[str, Any] = {"concatenate": False},
        hue_config: Dict[str, Any] = {"concatenate": False},
        dilate_outlines: int = 0,
        overwrite_nan_with_zeros: bool = True,
        in_memory: bool = False,
        dim_ordering="CHW",
        dtype="float32",
        divide_by=1,
    ):
        super().__init__(
            raster_files,
            None,
            augmentation,
            ndvi_config,
            gci_config,
            hue_config,
            dilate_outlines,
            overwrite_nan_with_zeros,
            in_memory,
            dim_ordering,
            dtype,
            divide_by,
        )

    def __len__(self):
        """Returns length of the dataset: number of raster files"""
        return len(self.raster_files)

    def __getitem__(self, idx):
        """
        Get one sample into the test/predict pipeline.

        Args:
            idx (int): Index.

        Returns:
            - *raster*: Raster for making the prediction. Can be augmented.
            - Dictionary with the keys
               *trafo*:  Coordinates of current raster for post-processing.
               *raster_id*: File name to be used in post-processing.
        """
        log.info(f"Predicting on {self.raster_files[idx]}")

        if self.in_memory:
            # Use pre-loaded data from self.samples
            # raster, raster_dict = self.samples[idx]
            raise NotImplementedError(
                "In-memory loading not implemented for inference dataset."
            )
        else:
            # Load data on-the-fly
            raster = self.load_raster(self.raster_files[idx])

        output_dict = {
            "trafo": np.array(get_rioxarray_trafo(raster)),
            "raster_id": self.raster_files[idx],
        }

        raster = tv_tensors.Image(raster.data, dtype=torch.float32)
        raster = self.augment_raster(raster)

        return raster, output_dict
