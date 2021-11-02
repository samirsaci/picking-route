import pandas as pd
import numpy as np
import plotly.express as px
from utils.routing.distances import (
	distance_picking,
	next_location
)
from utils.routing.routes import (
	create_picking_route
)
from utils.batch.mapping_batch import (
	orderlines_mapping,
	locations_listing
)
from utils.cluster.mapping_cluster import (
	df_mapping
)
from utils.batch.simulation_batch import (
	simulation_wave,
	simulate_batch
)
from utils.cluster.simulation_cluster import(
	loop_wave,
	simulation_cluster,
	create_dataframe,
	process_methods
)
from utils.results.plot import (
	plot_simulation1,
	plot_simulation2
)
import streamlit as st
from streamlit import caching

# Set page configuration
st.set_page_config(page_title ="Improve Warehouse Productivity using Order Batching",
                    initial_sidebar_state="expanded",
                    layout='wide',
                    page_icon="🛒")

# Set up the page
@st.cache(persist=False,
          allow_output_mutation=True,
          suppress_st_warning=True,
          show_spinner= True)
# Preparation of data
def load(filename, n):
    df_orderlines = pd.read_csv(IN + filename).head(n)
    return df_orderlines


# Alley Coordinates on y-axis
y_low, y_high = 5.5, 50
# Origin Location
origin_loc = [0, y_low]
# Distance Threshold (m)			
distance_threshold = 35			
distance_list = [1] + [i for i in range(5, 100, 5)]		
IN = 'static/in/'
# Store Results by WaveID
list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult = [], [], [], [], [], [], []
list_results = [list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult]	# Group in list
# Store Results by Simulation (Order_number)
list_ordnum , list_dstw = [], []

# Simulation 1: Order Batch
# SCOPE SIZE
st.header("**🥇 Impact of the wave size in orders (Orders/Wave) **")
st.subheader('''
        🛠️ HOW MANY ORDER LINES DO YOU WANT TO INCLUDE IN YOUR ANALYSIS?
    ''')
col1, col2 = st.beta_columns(2)
with col1:
	n = st.slider(
				'SIMULATION 1 SCOPE (THOUSDAND ORDERS)', 1, 200 , value = 5)
with col2:
	lines_number = 1000 * n 
	st.write('''🛠️{:,} \
		order lines'''.format(lines_number))
# SIMULATION PARAMETERS
st.subheader('''
        🛠️ SIMULATE ORDER PICKING BY WAVE OF N ORDERS PER WAVE WITH N IN [N_MIN, N_MAX] ''')
col_11 , col_22 = st.beta_columns(2)
with col_11:
	n1 = st.slider(
				'SIMULATION 1: N_MIN (ORDERS/WAVE)', 0, 20 , value = 1)
	n2 = st.slider(
				'SIMULATION 1: N_MAX (ORDERS/WAVE)', n1 + 1, 20 , value = int(np.max([n1+1 , 10])))
with col_22:
		st.write('''[N_MIN, N_MAX] = [{:,}, {:,}]'''.format(n1, n2))
# START CALCULATION
start_1= False
if st.checkbox('SIMULATION 1: START CALCULATION',key='show', value=False):
    start_1 = True
# Calculation
if start_1:
	df_orderlines = load('df_lines.csv', lines_number)
	df_waves, df_results = simulate_batch(n1, n2, y_low, y_high, origin_loc, lines_number, df_orderlines)
	plot_simulation1(df_results, lines_number)

# Simulation 2: Order Batch using Spatial Clustering 
# SCOPE SIZE
st.header("**🥈 Impact of the order batching method **")
st.subheader('''
        🛠️ HOW MANY ORDER LINES DO YOU WANT TO INCLUDE IN YOUR ANALYSIS?
    ''')
col1, col2 = st.beta_columns(2)
with col1:
	n_ = st.slider(
				'SIMULATION 2 SCOPE (THOUSDAND ORDERS)', 1, 200 , value = 5)
with col2:
	lines_2 = 1000 * n_ 
	st.write('''🛠️{:,} \
		order lines'''.format(lines_2))
# START CALCULATION
start_2 = False
if st.checkbox('SIMULATION 2: START CALCULATION',key='show_2', value=False):
    start_2 = True
# Calculation
if start_2:
	df_orderlines = load('df_lines.csv', lines_2)
	df_reswave, df_results = simulation_cluster(y_low, y_high, df_orderlines, list_results, n1, n2, 
			distance_threshold)
	plot_simulation2(df_reswave, lines_2, distance_threshold)