import streamlit as st
import plotly.express as px
import pandas as pd

import os
from glob import glob

import warnings
warnings.filterwarnings('ignore')

# make sure the directory is correct
if __name__ == '__main__':
    root_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(root_dir)
else:
    root_dir = './'


#######################################################
#               Reand GHG emission data               #
#######################################################

ghg_csvs = glob(f'{root_dir}/data/GHG*.csv')

# function to read the csv and remove the last row and column
def read_and_remove(file):
    df = pd.read_csv(file,header=[0,1,2],index_col=0)
    df = df.iloc[:-1,:-1]
    df.columns = pd.MultiIndex.from_tuples(df.columns.tolist())
    return df

ghg_seperate = [i for i in ghg_csvs if 'separate' in i]
ghg_seperate_df = pd.concat([read_and_remove(i) for i in ghg_seperate],axis=1)

# wide df to long
ghg_seperate_long = ghg_seperate_df.stack([0,1,2])\
                                   .reset_index()
ghg_seperate_long.columns = ['LUCC','Sector','Land Management','Source','Value']

# remove 0 values
ghg_seperate_long = ghg_seperate_long[ghg_seperate_long['Value']!=0]

# chang val to absolute values for plotting
ghg_seperate_long['Value'] = ghg_seperate_long['Value'].abs()





#   1) create the sidebar selection
st.sidebar.header('Choose the filter')


#   2) Sector
Sector = st.sidebar.multiselect('Pick up the Sector',
                                ghg_seperate_long['Sector'].unique())
#      update the df according to states
if not Sector:
    ghg_seperate_long_Sector = ghg_seperate_long
else:
    ghg_seperate_long_Sector = ghg_seperate_long[ghg_seperate_long['Sector']\
                                               .isin(Sector)]


#   2) LUCC
LUCC = st.sidebar.multiselect('Pick up the LUCC',
                              ghg_seperate_long_Sector['LUCC'].unique())

#      update the df according to regions
if not LUCC:
    ghg_seperate_long_LUCC = ghg_seperate_long_Sector
else:
    ghg_seperate_long_LUCC = ghg_seperate_long_Sector[ghg_seperate_long_Sector['LUCC']\
                                               .isin(LUCC)]


#   4) Land Management
LM = st.sidebar.multiselect('Pick up the Land Management',
                              ghg_seperate_long_Sector['Land Management'].unique())
#      update the df according to cities
if not LM:
    ghg_seperate_long_LM = ghg_seperate_long_LUCC
else:
    ghg_seperate_long_LM = ghg_seperate_long_LUCC[ghg_seperate_long_LUCC['Land Management']\
                                               .isin(LM)]


#######################################################
#                     Create charts                   #
#######################################################

col1,col2 = st.columns(2,gap='large')

# #   1) create a column chart in col1
# #   1-1)  group the filtered data by category
# ghg_seperate_long_cat = ghg_seperate_long_LM.groupby('Source')\
#                                 .agg({'Total':'sum'})\
#                                 .reset_index()

with col1:
    st.subheader('GHG emissions by Sector')
    fig = px.pie(ghg_seperate_long_LM, 
                 values='Value',
                 names='Source',
                 hole=0.5)

    fig.update_traces(textposition='inside')
    fig.update_layout(showlegend=False,
                      uniformtext_minsize=12, 
                      uniformtext_mode='hide',)
                      
    st.plotly_chart(fig, use_container_width=True)


#######################################################
#                  Show the tree map                  #
#######################################################


with col2:
    st.subheader('GHG emission in detail')

    #  1) create the tree map
    fig = px.treemap(ghg_seperate_long,
                    path=['Sector','Land Management','Source','LUCC'],
                    values='Value',
                    color='Source',
                    template='seaborn')

    st.plotly_chart(fig, use_container_width=True)