import os
import re
import pandas as pd
import numpy as np
import rasterio


# Convert map to tif with name columns
def get_name_from_string(name:str):
    """Extract the name from the file name"""
    name = os.path.basename(name).split('.')[0]
    
    # First get the type and item from name
    if 'lumap' in name:
        name_type = 'Land Use Map'
        name_item = name_type
    elif 'lmmap' in name:
        name_type = 'Land Management Map'
        name_item = name_type
    elif 'ammap' in name:
        name_type = 'Agricultural Management Map'
        name_item = re.compile(r'\w_(.+)_\d').findall(name)[0]

    # then get the year from name
    name_year = re.compile(r'(\d{4})').findall(name)[0]

    return name_type, name_item, name_year


# function to write colormap to tif
def hex_color_to_numeric(hex_color):
    # Remove the '#' character (if present)
    hex_color = hex_color.lstrip('#')

    # Get the red, green, blue, and (optional) alpha components
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    if len(hex_color) == 8:  # If the color includes an alpha channel
        alpha = int(hex_color[6:8], 16) 
        return red, green, blue, alpha
    else:
        return red, green, blue, 255


# function to convert hex color to numeric
def color_hex2num(csv_path:str=f'./tools/color_map.csv'):
    lu_colors = pd.read_csv(csv_path)
    lu_colors['color_num'] = lu_colors['color_HEX']\
                                .apply(lambda x: hex_color_to_numeric(x))
    lu_colors_dict = lu_colors.set_index('lu_code')['color_num'].to_dict()  
    return lu_colors_dict


# function to convert a 1-band arrary to 4-band (RGBA) array with colormap
def convert_1band_to_4band(lu_tif:str, 
                           color_dict:dict = color_hex2num(),
                           band:int = 1,
                           binary_color:bool = False):
    """Convert a 1-band array to 4-band (RGBA) array with colormap"""

    # check if the color_dict needs to be binarizd
    if binary_color:
        color_dict = {0:(19, 222, 222, 255), 1:(220, 16, 16,255)}

    # get the file name without extension
    lu_base = os.path.basename(lu_tif).split('.')[0]

    # get the tif array and meta
    with rasterio.open(lu_tif) as src:
        lu_arr = src.read(band)
        lu_meta = src.meta
        # set the color of nodata value to transparent
        color_dict[src.meta['nodata']] = (0, 0, 0, 0)

    # update meta
    lu_meta.update(count=4,compress='lzw',dtype='uint8',nodata=0)
    # convert the 1-band array to 4-band (RGBA) array
    arr_4band = np.zeros((lu_arr.shape[0], lu_arr.shape[1], 4), 
                          dtype='uint8') 
    for k, v in color_dict.items():
        arr_4band[lu_arr == k] = v

    # convert HWC to CHW
    arr_4band = arr_4band.transpose(2, 0, 1)

    # write 4band array to tif
    with rasterio.open(f'./data/raster_colored/{lu_base}_colored.tiff', 
                    'w', 
                    **lu_meta) as dst:
        dst.write(arr_4band)





