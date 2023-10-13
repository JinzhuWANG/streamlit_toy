import os
import requests
import streamlit as st

from tools import get_name_from_string

import pandas as pd

from folium import Map, TileLayer
from streamlit_folium import st_folium
from glob import glob

import warnings
warnings.filterwarnings('ignore')


# make sure the directory is correct
if __name__ == '__main__':
    root_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(root_dir)
else:
    root_dir = './'



# get the map paths
maps = glob(f'{root_dir}/data/raster_colored/*.tiff')

# convert map_path to a df
tif_df = pd.DataFrame({'path': maps})
tif_df[['type','item','year']] = tif_df['path']\
                                    .apply(lambda x:get_name_from_string(x))\
                                    .tolist()



#  1) create the sidebar selection
st.sidebar.header('Choose the land use maps')



#   2) map type
map_type = st.sidebar.selectbox('Pick up the Type',
                               list( tif_df['type'].unique()))
#      update the df according to states
if not map_type:
    tif_df_type = tif_df
else:
    tif_df_type = tif_df[tif_df['type'] ==map_type]


#   2) item
map_item = st.sidebar.selectbox('Pick up the Item',
                              list(tif_df_type['item'].unique()))

#      update the df according to regions
if not map_item:
    tif_df_item = tif_df_type
else:
    tif_df_item = tif_df_type[tif_df_type['item'] == map_item]


#   4) Land Management
map_year = st.sidebar.selectbox('Pick up the Year',
                            list(tif_df_item['year'].unique()))
#      update the df according to cities
if not map_year:
    tif_df_year = tif_df_item
else:
    tif_df_year = tif_df_item[tif_df_item['year'] == map_year]




#######################################################
#               Add a map to the webpage              #
#######################################################


# function to wrap the request
def submit_request(BASE_URL, endpoint, url):
    r = requests.get(
        f"{BASE_URL}/{endpoint}",
        params = {
            "url": url,
        }
    ).json()
    return r



# Add the GeoTIFF overlay
titiler_endpoint = "http://titiler.xyz" 

# the tif cloud storage url
# incase the user does not select any map, use the default map
tif_url = 'https://storage.googleapis.com/luto_tif/lmmap_2030_colored.tiff'

# get map url from google cloud storage
cloud_bucket = 'https://storage.googleapis.com/luto_tif'
map_base_name = os.path.basename(tif_df_year['path'].values[0])
tif_url = f"{cloud_bucket}/{map_base_name}"


# instantiate the map
map = Map(location=[-24.162,132.847], 
         zoom_start=5)

# base map layer
base_layer = TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(map)

base_layer.add_to(map)

# get tile data from titiler
tile_json_analytic = submit_request(titiler_endpoint, "cog/tilejson.json", tif_url)
tileset = tile_json_analytic["tiles"][0]

tile_layer = TileLayer(
    tiles= tileset,
    attr="LUTO Land Use Map",
)

tile_layer.add_to(map)


# call to render Folium map in Streamlit
st_data = st_folium(map, width=725)