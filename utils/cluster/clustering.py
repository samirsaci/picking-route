import numpy as np
import pandas as pd
import itertools
from ast import literal_eval
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2, whiten
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import ward, fcluster
from utils.routing.distances import *

def cluster_locations(list_coord, distance_threshold, dist_method, clust_start):
    ''' Step 1: Create clusters of locations'''
    # Create linkage matrix
    if dist_method == 'euclidian':
        Z = ward(pdist(np.stack(list_coord)))
    else:
        Z = ward(pdist(np.stack(list_coord), metric = distance_picking_cluster))
    # Single cluster array
    fclust1 = fcluster(Z, t = distance_threshold, criterion = 'distance')
    return fclust1


def clustering_mapping(df, distance_threshold, dist_method, orders_number, wave_start, clust_start, df_type): # clustering_loc
    '''Step 2: Clustering and mapping'''
    # 1. Create Clusters
    list_coord, list_OrderNumber, clust_id, df = cluster_wave(df, distance_threshold, 'custom', clust_start, df_type)
    clust_idmax = max(clust_id) # Last Cluster ID
    # 2. Mapping Order lines
    dict_map, dict_omap, df, Wave_max = lines_mapping_clst(df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start)
    return dict_map, dict_omap, df, Wave_max, clust_idmax


def cluster_wave(df, distance_threshold, dist_method, clust_start, df_type):
    '''Step 3: Create waves by clusters'''
    # Create Column for Clustering
    if df_type == 'df_mono':
        df['Coord_Cluster'] = df['Coord'] 
    # Mapping points
    df_map = pd.DataFrame(df.groupby(['OrderNumber', 'Coord_Cluster'])['SKU'].count()).reset_index() 	# Here we use Coord Cluster
    list_coord, list_OrderNumber = np.stack(df_map.Coord_Cluster.apply(lambda t: literal_eval(t)).values), df_map.OrderNumber.values
    # Cluster picking locations
    clust_id = cluster_locations(list_coord, distance_threshold, dist_method, clust_start)
    clust_id = [(i + clust_start) for i in clust_id]
    # List_coord
    list_coord = np.stack(list_coord)
    return list_coord, list_OrderNumber, clust_id, df


def lines_mapping(df, orders_number, wave_start):
    '''Step 4: Mapping Order lines mapping without clustering '''
    # Unique order numbers list
    list_orders = df.OrderNumber.unique()
    # Dictionnary for mapping
    dict_map = dict(zip(list_orders, [i for i in range(1, len(list_orders))]))
    # Order ID mapping
    df['OrderID'] = df['OrderNumber'].map(dict_map)
    # Grouping Orders by Wave of orders_number 
    df['WaveID'] = (df.OrderID%orders_number == 0).shift(1).fillna(0).cumsum() + wave_start
    # Counting number of Waves
    waves_number = df.WaveID.max() + 1
    return df, waves_number


def lines_mapping_clst(df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start):
    '''Step 4: Mapping Order lines mapping with clustering '''
    # Dictionnary for mapping by cluster
    dict_map = dict(zip(list_OrderNumber, clust_id))
    # Dataframe mapping
    df['ClusterID'] = df['OrderNumber'].map(dict_map)
    # Order by ID and mapping
    df = df.sort_values(['ClusterID','OrderNumber'], ascending = True)
    list_orders = list(df.OrderNumber.unique())
    # Dictionnary for order mapping 
    dict_omap = dict(zip(list_orders, [i for i in range(1, len(list_orders))]))
    # Order ID mapping
    df['OrderID'] = df['OrderNumber'].map(dict_omap)
    # Create Waves: Increment when reaching orders_number or changing cluster
    df['WaveID'] = wave_start + ((df.OrderID%orders_number == 0) | (df.ClusterID.diff() != 0)).shift(1).fillna(0).cumsum() 

    wave_max = df.WaveID.max()
    return dict_map, dict_omap, df, wave_max


def locations_listing(df_orderlines, wave_id):
    ''' Step 5: Listing location per Wave of orders'''

    # Filter by wave_id
    df = df_orderlines[df_orderlines.WaveID == wave_id]
    # Create coordinates listing
    list_coord = list(df['Coord'].apply(lambda t: literal_eval(t)).values) 	# Here we use Coord for distance
    list_coord.sort()
    # Get unique Unique coordinates
    list_coord = list(k for k,_ in itertools.groupby(list_coord))
    n_locs = len(list_coord)
    n_lines = len(df)
    n_pcs = df.PCS.sum()

    return list_coord, n_locs, n_lines, n_pcs