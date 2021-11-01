from utils.batch.mapping_batch import *
from utils.cluster.mapping_cluster import *
from utils.routing.routes import *

def simulation_wave(y_low, y_high, origin_loc, orders_number, df_orderlines, list_wid, list_dst, list_route, list_ord):
	''' Simulate of total picking distance with n orders per wave'''
	distance_route = 0 
	# Create waves
	df_orderlines, waves_number = orderlines_mapping(df_orderlines, orders_number)
	for wave_id in range(waves_number):
		# Listing of all locations for this wave 
		list_locs, n_locs, n_lines, n_pcs = locations_listing(df_orderlines, wave_id)
		# Results
		wave_distance, list_chemin = create_picking_route(origin_loc, list_locs, y_low, y_high)
		distance_route = distance_route + wave_distance
		list_wid.append(wave_id)
		list_dst.append(wave_distance)
		list_route.append(list_chemin)
		list_ord.append(orders_number)
	return list_wid, list_dst, list_route, list_ord, distance_route

def simulate_batch(n1, n2, y_low, y_high, origin_loc, orders_number, df_orderlines):
	''' Loop with several scenarios of n orders per wave'''
	# Lists for results
	list_wid, list_dst, list_route, list_ord = [], [], [], []
	# Test several values of orders per wave
	for orders_number in range(n1, n2 + 1):
		list_wid, list_dst, list_route, list_ord, distance_route = simulation_wave(y_low, y_high, origin_loc, orders_number, 
		df_orderlines, list_wid, list_dst, list_route, list_ord)
		print("Total distance covered for {} orders/wave: {:,} m".format(orders_number, distance_route))

	# By Wave
	df_waves = pd.DataFrame({'wave': list_wid,
				'distance': list_dst,
				'routes': list_route,
				'order_per_wave': list_ord})

	# Results aggregate
	df_results = pd.DataFrame(df_waves.groupby(['order_per_wave'])['distance'].sum())
	df_results.columns = ['distance']
	return df_waves, df_results.reset_index()