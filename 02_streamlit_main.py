import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


from folium import Map, TileLayer
from streamlit_folium import st_folium
import requests
import subprocess



# Set the page title and icon
st.set_page_config(page_title='Supermakert Sale', 
                   page_icon=':bar_chart:',
                   layout='wide')

# q: make the title close to the top of page
st.title(':bar_chart: Supermakert Sale')

# Use makrdown to set the title close to the top of page
st.markdown('<style>div.block-container{padding-top: 1rem;}</style>', 
            unsafe_allow_html=True)


# Read file from disk
fl = pd.read_csv('./data/Superstore.csv')
# convert the Order Date to datetime
fl['Order Date'] = pd.to_datetime(fl['Order Date'])


#######################################################
#    Use two columns to show the date selection box   #
#######################################################
col1, col2 = st.columns(2)
#   1) get the min/max of date
startDate,endDate = pd.to_datetime(fl['Order Date']).agg(['min','max'])

#   2) set the date selection box in column 1
with col1:
    start = pd.to_datetime(st.date_input('Select start date', startDate))

with col2:
    end = pd.to_datetime(st.date_input('Select end date', endDate))

#   3) update the fl use the Start/End date
fl = fl[(fl['Order Date'] >= start) & (fl['Order Date'] <= end)]


#######################################################
#            Create the sidebar selection             #
#######################################################

#   1) create the sidebar selection
st.sidebar.header('Choose the filter')

#   2) create the multi-selection box for region
region = st.sidebar.multiselect('Pick up the Region',fl['Region'].unique())

#      update the fl according to regions
if not region:
    fl_region = fl
else:
    fl_region = fl[fl['Region'].isin(region)]


#   3) create the multi-selection box for state
state = st.sidebar.multiselect('Pick up the State',fl_region['State'].unique())
#      update the fl according to states
if not state:
    fl_state = fl_region
else:
    fl_state = fl_region[fl_region['State'].isin(state)]


#   4) create the multi-selection box for city
city = st.sidebar.multiselect('Pick up the City',fl_state['City'].unique())
#      update the fl according to cities
if not city:
    fl_city = fl_state
else:
    fl_city = fl_state[fl_state['City'].isin(city)]



#######################################################
#                     Create charts                   #
#######################################################



#   1) create a column chart in col1
#   1-1)  group the filtered data by category
fl_cat = fl_city.groupby('Category')\
                .agg({'Sales':'sum'})\
                .reset_index()

with col1:
    st.subheader('Sales by Category')
    fig = px.bar(fl_cat, x='Category', y='Sales',
                 text=[f'${i:.2f}' for i in fl_cat['Sales']])
    st.plotly_chart(fig, use_container_width=True)

#   2) create a pie chart in col2
with col2:
    st.subheader('Ship Mode wise sales')
    fig = px.pie(fl_city, values='Sales', names='Ship Mode',hole=0.5)
    fig.update_traces(textposition='outside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


#######################################################
#               Show the filtered table               #
#######################################################
# col1, col2 = st.columns(2)

with col1:
    with st.expander('Category wise sales'):
        st.write(fl_cat.style.background_gradient(cmap='Blues'))
        csv_col1 = fl_cat.to_csv(index=False)
        st.download_button('Download the Category sales table',
                           csv_col1,
                           mime='text/csv',
                           help='Click here to download the filtered table as CSV')
with col2:
    with st.expander('Ship mode sales'):
        st.write(fl_city.groupby('Ship Mode')
                        .agg({'Sales':'sum'})
                        .style.background_gradient(cmap='Oranges'))
        csv_col2 = fl_city.groupby('Ship Mode').agg({'Sales':'sum'}).to_csv()
        st.download_button('Download the Ship mode sales table',
                           csv_col2,
                           mime='text/csv',
                           help='Click here to download the filtered table as CSV')



#######################################################
#       Time Series chart for the filtered data       #
#######################################################

#  1) get the year-month using the Order Date
fl_city['year_month'] = fl_city['Order Date'].dt.strftime('%Y-%m')
#  2) group the data by month
fl_month_series = fl_city.groupby('year_month').agg({'Sales':'sum'}).reset_index()   
#  3) create the line chart
st.subheader('Time Series chart for the filtered data')
fig = px.line(fl_month_series.set_index('year_month'),
              y='Sales',
              template='gridon')
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
#  4) show/download the data
with st.expander('Show the timeseries data'):
    st.write(fl_month_series.T)
    csv = fl_month_series.to_csv(index=False)
    st.download_button('Download the filtered table',
                       csv,
                       mime='text/csv',
                       help='Click here to download the filtered table as CSV')
    


#######################################################
#                  Show the tree map                  #
#######################################################


st.subheader('Tree Map for the filtered data')

#  1) create the tree map
fig = px.treemap(fl_city,
                 path=['Region','Category','Sub-Category'],
                 values='Sales',
                 color='Sub-Category',
                 template='seaborn')
st.plotly_chart(fig, use_container_width=True)


#######################################################
#              Create a scatter plot                  #
#######################################################

#  1) create the scatter plot
fig = px.scatter(fl_city,x='Sales',y='Profit',size='Quantity')
fig['layout'].update(title={'text':'Sales vs Profit'},
                     titlefont_size=20,
                     xaxis=dict(title='Sales',titlefont={'size':19}),)
st.plotly_chart(fig, use_container_width=True)



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

def start_titiler_server():
    """Generates the Prisma Client and loads it
    """
    print(f'Starting Titiler Service')
    subprocess.call(["uvicorn", "titiler.application.main:app"])
    print(f'Titiler Service Started')

    return True

# # trick to avoid stuck the streamlit app
# start_titiler_server = st.cache_data(start_titiler_server)

# # start the titiler server
# start_titiler_server()


# Add the GeoTIFF overlay
titiler_endpoint = "http://titiler.xyz" 

# the tif cloud storage url
tif_url = 'https://storage.googleapis.com/luto_tif/ammap_ecological_grazing_2030_colored.tiff'


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