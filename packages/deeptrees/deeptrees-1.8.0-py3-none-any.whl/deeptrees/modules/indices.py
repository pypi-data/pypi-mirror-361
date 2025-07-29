import numpy as np
import xarray as xr


def ndvi_xarray(img, red, nir):
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) from a given image.

    NDVI is calculated using the formula: (NIR - Red) / (NIR + Red + 1E-10).
    The input image bands are implicitly converted to Float32 for the calculation.

    Parameters:
    img (xarray.DataArray): The input image as an xarray DataArray.
    red (int or str): The band index or name corresponding to the red band.
    nir (int or str): The band index or name corresponding to the near-infrared (NIR) band.

    Returns:
    xarray.DataArray: The NDVI values as an xarray DataArray.
    """
    """Calculates the NDVI from a given image. Implicitly converts to Float32."""
    redl = img.sel(band=red).astype('float32')
    nirl = img.sel(band=nir).astype('float32')
    return (nirl - redl) / (nirl + redl + 1E-10)


def ndvi(raster, red_idx=0, nir_idx=3, axis=0):
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    NDVI = (NIR - RED) / (NIR + RED)
    """
    # Check if input is an xarray DataArray or Dataset
    is_xarray = hasattr(raster, 'values')
    
    # Select bands
    if axis == 0:
        if is_xarray:
            red = raster[red_idx].values
            nir = raster[nir_idx].values
        else:
            red = raster[red_idx]
            nir = raster[nir_idx]
    elif axis == 2:
        if is_xarray:
            red = raster[:, :, red_idx].values
            nir = raster[:, :, nir_idx].values
        else:
            red = raster[:, :, red_idx]
            nir = raster[:, :, nir_idx]
    
    # Calculate NDVI with numpy operations to avoid xarray indexing issues
    # This avoids division by zero by using np.divide with a "where" condition
    denominator = nir + red
    numerator = nir - red
    
    # Use numpy's divide function with "where" parameter to handle division by zero
    result = np.divide(numerator, denominator, out=np.zeros_like(denominator), where=denominator!=0)
    
    # Replace any NaNs or Infs that might have been created
    result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Return as xarray DataArray if input was xarray
    if is_xarray and hasattr(raster, 'coords'):
        # If working with an xarray DataArray, use the same coordinates
        import xarray as xr
        # Create a new DataArray with the same coordinates as the input
        # This depends on the structure of your input raster
        if axis == 0:
            # Create a copy of coordinates from one band
            coords = {k: v for k, v in raster[0].coords.items()}
            result = xr.DataArray(result, coords=coords, dims=raster[0].dims)
        elif axis == 2:
            # Create a copy of coordinates but without the band dimension
            coords = {k: v for k, v in raster.coords.items() if k != 'band'}
            result = xr.DataArray(result, coords=coords, dims=('y', 'x'))
    
    return result

def gci(raster, red_idx=0, green_idx=1, nir_idx=3, axis=0):
    """
    Calculate Green Chlorophyll Index (GCI).
    GCI = (NIR / GREEN) - 1
    """
    # Check if input is an xarray DataArray or Dataset
    is_xarray = hasattr(raster, 'values')
    
    # Select bands
    if axis == 0:
        if is_xarray:
            green = raster[green_idx].values
            nir = raster[nir_idx].values
        else:
            green = raster[green_idx]
            nir = raster[nir_idx]
    elif axis == 2:
        if is_xarray:
            green = raster[:, :, green_idx].values
            nir = raster[:, :, nir_idx].values
        else:
            green = raster[:, :, green_idx]
            nir = raster[:, :, nir_idx]
    
    # Calculate GCI with numpy operations to avoid xarray indexing issues
    # Use numpy's divide with "where" condition to handle division by zero
    ratio = np.divide(nir, green, out=np.ones_like(green), where=green!=0)
    result = ratio - 1.0
    
    # Replace any NaNs or Infs
    result = np.nan_to_num(result, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Return as xarray DataArray if input was xarray
    if is_xarray and hasattr(raster, 'coords'):
        import xarray as xr
        if axis == 0:
            coords = {k: v for k, v in raster[0].coords.items()}
            result = xr.DataArray(result, coords=coords, dims=raster[0].dims)
        elif axis == 2:
            coords = {k: v for k, v in raster.coords.items() if k != 'band'}
            result = xr.DataArray(result, coords=coords, dims=('y', 'x'))
    
    return result

def hue(raster, red_idx=0, green_idx=1, blue_idx=2, axis=0):
    """
    Calculate hue from RGB.
    """
    # Check if input is an xarray DataArray or Dataset
    is_xarray = hasattr(raster, 'values')
    
    # Select bands
    if axis == 0:
        if is_xarray:
            red = raster[red_idx].values
            green = raster[green_idx].values
            blue = raster[blue_idx].values
        else:
            red = raster[red_idx]
            green = raster[green_idx]
            blue = raster[blue_idx]
    elif axis == 2:
        if is_xarray:
            red = raster[:, :, red_idx].values
            green = raster[:, :, green_idx].values
            blue = raster[:, :, blue_idx].values
        else:
            red = raster[:, :, red_idx]
            green = raster[:, :, green_idx]
            blue = raster[:, :, blue_idx]
    
    # Calculate max and min values
    max_val = np.maximum(np.maximum(red, green), blue)
    min_val = np.minimum(np.minimum(red, green), blue)
    delta = max_val - min_val
    
    # Initialize hue with zeros
    hue = np.zeros_like(red)
    
    # Safe division function to avoid warnings
    def safe_divide(a, b):
        return np.divide(a, b, out=np.zeros_like(a), where=b!=0)
    
    # Calculate hue using numpy operations without boolean indexing
    # Red is max
    mask_red = (max_val == red) & (delta > 1e-10)
    hue = np.where(mask_red, (safe_divide((green - blue), delta) % 6), hue)
    
    # Green is max
    mask_green = (max_val == green) & (delta > 1e-10)
    hue = np.where(mask_green, (safe_divide((blue - red), delta) + 2), hue)
    
    # Blue is max
    mask_blue = (max_val == blue) & (delta > 1e-10)
    hue = np.where(mask_blue, (safe_divide((red - green), delta) + 4), hue)
    
    # Scale to [0,1]
    hue /= 6.0
    
    # Replace any NaNs or Infs
    hue = np.nan_to_num(hue, nan=0.0, posinf=0.0, neginf=0.0)
    
    # Return as xarray DataArray if input was xarray
    if is_xarray and hasattr(raster, 'coords'):
        import xarray as xr
        if axis == 0:
            coords = {k: v for k, v in raster[0].coords.items()}
            hue = xr.DataArray(hue, coords=coords, dims=raster[0].dims)
        elif axis == 2:
            coords = {k: v for k, v in raster.coords.items() if k != 'band'}
            hue = xr.DataArray(hue, coords=coords, dims=('y', 'x'))
    
    return hue