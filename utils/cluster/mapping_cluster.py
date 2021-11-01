from utils.cluster.clustering import *
from utils.process.processing import *
from utils.routing.distances import *


def df_mapping(df_orderlines, orders_number, distance_threshold, mono_method, multi_method):
    ''' Mapping Order lines Dataframe using clustering'''
    # Filter mono and multi orders
    df_mono, df_multi = process_lines(df_orderlines)
    wave_start = 0
    clust_start = 0

    # Mapping for single line orders
    if mono_method == 'clustering':		
        df_type = 'df_mono' 	
        dict_map, dict_omap, df_mono, waves_number, clust_idmax = clustering_mapping(df_mono, distance_threshold, 'custom', 
            orders_number, wave_start, clust_start, df_type)
    else: 
        df_mono, waves_number = lines_mapping(df_mono, orders_number, 0)
        clust_idmax = 0 
        # => Wave_start
    wave_start = waves_number
    clust_start = clust_idmax 

    # Mapping for multi line orders
    if multi_method == 'clustering':
        df_type = 'df_multi' 	
        df_multi = centroid_mapping(df_multi)
        dict_map, dict_omap, df_multi, waves_number, clust_idmax  = clustering_mapping(df_multi, distance_threshold, 'custom', 
            orders_number, wave_start, clust_start, df_type)
    else:
        df_multi, waves_number = lines_mapping(df_multi, orders_number, wave_start)

    # Final Concatenation
    df_orderlines, waves_number = monomult_concat(df_mono, df_multi)

    return df_orderlines, waves_number