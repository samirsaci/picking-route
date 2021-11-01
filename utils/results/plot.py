import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

def plot_simulation1(df_results, lines_number):
    ''' Plot simulation of batch size'''
    fig = px.bar(data_frame=df_results,
        width=1200, 
        height=600,
        x = 'order_per_wave',
        y = 'distance',
        labels={ 
            'order_per_wave': 'Wave size (Orders/Wave)',
            'distance': 'Total Picking Walking Distance (m)'})
    fig.update_traces(marker_line_width=1,marker_line_color="black")
    st.write(fig)

def plot_simulation2(df_reswave, lines_number, distance_threshold):
    fig = px.bar(data_frame=df_reswave.reset_index(),
        width=1200, 
        height=600,
        x = 'orders_number',
        y = ['distance_method_1', 'distance_method_2', 'distance_method_3'],
        labels={ 
            'orders_number': 'Wave size (Orders/Wave)',
            'distance_method_1': 'NO CLUSTERING APPLIED',
            'distance_method_2': 'CLUSTERING ON SINGLE LINE ORDERS',
            'distance_method_3': 'CLUSTERING ON SINGLE LINE AND CENTROID FOR MULTI LINE'}, barmode = "group")
    fig.update_traces(marker_line_width=1, marker_line_color="black")
    st.write(fig)

