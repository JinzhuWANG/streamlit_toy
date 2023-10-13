from glob import glob
import os

import pandas as pd
from tools import convert_1band_to_4band, get_name_from_string
from tools.cloud_storage_utils import upload_to_cloud, set_public_access




# Open the file
tifs = glob(r'./data/*.tiff')

lumaps = [f for f in tifs if 'lumap' in f]
lmmaps = [f for f in tifs if 'lmmap' in f]
ammaps = [f for f in tifs if 'ammap' in f]



# Put all tif_paths in a df
tif_df = pd.DataFrame({'path': tifs})
tif_df[['type','item','year']] = tif_df['path']\
                                    .apply(lambda x:get_name_from_string(x))\
                                    .tolist()



# conver all tif to 4-band tif (RGBA)
for tif in tifs:
    # get the file name without extension
    lu_base = os.path.basename(tif).split('.')[0]

    # check the color mode {lumap--> multicolored; others --> binary}
    if not 'lumap' in lu_base: binary_color = True

    if os.path.exists(f'./data/raster_colored/{lu_base}_colored.tiff'):
        print(f'{lu_base} had being converted... Use cached data') 
    else:
        convert_1band_to_4band(tif, binary_color=binary_color)
        print(f'{lu_base} converted successfully!')


# upload to google cloud storage
colored_tifs = glob(r'./data/raster_colored/*.tiff')
upload_to_cloud(colored_tifs)
set_public_access()