from utils.cluster.mapping_cluster import *
from utils.routing.routes import *


# Function 
def simulation_wave(y_low, y_high, orders_number, df_orderlines, list_results, distance_threshold, mono_method, multi_method):
    ''' Simulate the distance for a number of orders per wave'''
    # List to store values
    [list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult] = [list_results[i] for i in range(len(list_results))]

    # Variables to store total distance
    distance_route = 0
    origin_loc = [0, y_low] 	

    # Mapping of orderlines with waves number
    df_orderlines, waves_number = df_mapping(df_orderlines, orders_number, distance_threshold, mono_method, multi_method)

    # Loop
    for wave_id in range(waves_number):
        # Listing of all locations for this wave 
        list_locs, n_locs, n_lines, n_pcs = locations_listing(df_orderlines, wave_id)
        # Create picking route
        wave_distance, list_chemin, distance_max = create_picking_route_cluster(origin_loc, list_locs, y_low, y_high)
        # Total walking distance
        distance_route = distance_route + wave_distance
        # Results by wave
        monomult = mono_method + '-' + multi_method

        # Add the results 
        list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult = append_results(list_wid, list_dst, list_route, list_ord, list_lines, 
        list_pcs, list_monomult, wave_id, wave_distance, list_chemin, orders_number, n_lines, n_pcs, monomult)

    # List results
    list_results = [list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult]
    return list_results, distance_route


def loop_wave(y_low, y_high, df_orderlines, list_results, n1, n2, distance_threshold, mono_method, multi_method):
    ''' Simulate all scenarios for each number of orders per wave'''
    # Lists for records
    list_ordnum, list_dstw = [], []
    lines_number = len(df_orderlines)
    # Test several values of orders per wave
    for orders_number in range(n1, n2):
        # Scenario of orders/wave = orders_number 
        list_results, distance_route = simulation_wave(y_low, y_high, orders_number, df_orderlines, list_results,
            distance_threshold, mono_method, multi_method)
        # Append results per Wave
        list_ordnum.append(orders_number)
        list_dstw.append(distance_route)
        print("{} orders/wave: {:,} m".format(orders_number, distance_route))
    # Output list
    [list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult] = [list_results[i] for i in range(len(list_results))]
    # Output results per wave
    df_results, df_reswave = create_dataframe(list_wid, list_dst, list_route, list_ord, 
        distance_route, list_lines, list_pcs, list_monomult, list_ordnum, list_dstw)
    return list_results, df_reswave


def simulation_cluster(y_low, y_high, df_orderlines, list_results, n1, n2, distance_threshold):
    '''Simulate for three scenarios'''
    # Loop_wave: Simulation 1
    mono_method, multi_method = 'normal', 'normal'
    list_results, df_reswave1 = loop_wave(y_low, y_high, df_orderlines, list_results, n1, n2, 
        distance_threshold, mono_method, multi_method)
    # Loop_wave: Simulation 2
    mono_method, multi_method = 'clustering', 'normal'
    list_results, df_reswave2 = loop_wave(y_low, y_high, df_orderlines, list_results, n1, n2, 
        distance_threshold, mono_method, multi_method)
    # Loop_wave: Simulation 3
    mono_method, multi_method = 'clustering', 'clustering'
    list_results, df_reswave3 = loop_wave(y_low, y_high, df_orderlines, list_results, n1, n2, 
        distance_threshold, mono_method, multi_method)

    # Expand
    [list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult] = [list_results[i] for i in range(len(list_results))]
    lines_number = len(df_orderlines)

    # Results 
    df_results = pd.DataFrame({'wave_number': list_wid,
                                'distance': list_dst,
                                'chemins': list_route,
                                'order_per_wave': list_ord,
                                'lines': list_lines,
                                'pcs': list_pcs,
                                'mono_multi':list_monomult})
                                
    # Final Processing
    df_reswave = process_methods(df_reswave1, df_reswave2, df_reswave3, lines_number, distance_threshold)

    return df_reswave, df_results


def create_dataframe(list_wid, list_dst, list_route, list_ord, distance_route, list_lines, list_pcs, list_monomult, list_ordnum, list_dstw):
    ''' Create Dataframes of results'''

    # Results by Wave df
    df_results = pd.DataFrame({'wave_number': list_wid,
                                'distance': list_dst,
                                'chemin': list_route,
                                'orders_per_wave': list_ord,
                                'lines': list_lines,
                                'pcs': list_pcs,
                                'mono_multi':list_monomult})
    # Results by Wave_ID
    df_reswave = pd.DataFrame({
        'orders_number': list_ordnum,
        'distance': list_dstw 
        })

    return df_results, df_reswave

# Append Results
def append_results(list_wid, list_dst, list_route, list_ord, list_lines, 
		list_pcs, list_monomult, wave_id, wave_distance, list_chemin, orders_number, n_lines, n_pcs, monomult):

	list_wid.append(wave_id)
	list_dst.append(wave_distance)
	list_route.append(list_chemin)
	list_ord.append(orders_number)
	list_lines.append(n_lines)
	list_pcs.append(n_pcs)
	list_monomult.append(monomult)

	return list_wid, list_dst, list_route, list_ord, list_lines, list_pcs, list_monomult


def process_methods(df_reswave1, df_reswave2, df_reswave3, lines_number, distance_threshold):
    ''' Process the results of three methods'''

    # Concatenate two dataframes for plot
    df_reswave1.rename(columns={"distance": "distance_method_1"}, inplace = True)
    df_reswave2.rename(columns={"distance": "distance_method_2"}, inplace = True)
    df_reswave3.rename(columns={"distance": "distance_method_3"}, inplace = True)

    df_reswave = df_reswave1.set_index('orders_number')
    # Rename columns
    df_reswave['distance_method_2'] = df_reswave2.set_index('orders_number')['distance_method_2']
    df_reswave['distance_method_3'] = df_reswave3.set_index('orders_number')['distance_method_3']

    df_reswave.reset_index().plot.bar(x = 'orders_number', y = ['distance_method_1', 'distance_method_2', 'distance_method_3'], 
        figsize=(10, 6), color = ['black', 'red', 'blue'])

    plt.title("Picking Route Distance for {:,} Order lines / {} m distance threshold".format(lines_number, distance_threshold))
    plt.ylabel('Walking Distance (m)')
    plt.xlabel('Orders per Wave (Orders/Wave)')
    plt.savefig("static/out/{}lines_{}m_3m.png".format(lines_number, distance_threshold))
    plt.show()

    return df_reswave