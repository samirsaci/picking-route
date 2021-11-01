import pandas as pd
import numpy as np 
import itertools
from ast import literal_eval
from utils.routing.distances import *

def create_picking_route(origin_loc, list_locs, y_low, y_high):
    '''Calculate total distance to cover for a list of locations'''
    # Total distance variable
    wave_distance = 0
    # Current location variable 
    start_loc = origin_loc
    # Store routes
    list_chemin = []
    list_chemin.append(start_loc)
    
    while len(list_locs) > 0: # Looping until all locations are picked
        # Going to next location
        list_locs, start_loc, next_loc, distance_next = next_location(start_loc, list_locs, y_low, y_high)
        # Update start_loc 
        start_loc = next_loc
        list_chemin.append(start_loc)
        # Update distance
        wave_distance = wave_distance + distance_next 

    # Final distance from last storage location to origin
    wave_distance = wave_distance + distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)

    return wave_distance, list_chemin

# Calculate total distance to cover for a list of locations
def create_picking_route_cluster(origin_loc, list_locs, y_low, y_high):
    # Total distance variable
    wave_distance = 0
    # Distance max
    distance_max = 0
    # Current location variable 
    start_loc = origin_loc
    # Store routes
    list_chemin = []
    list_chemin.append(start_loc)
    while len(list_locs) > 0: # Looping until all locations are picked
        # Going to next location
        list_locs, start_loc, next_loc, distance_next = next_location(start_loc, list_locs, y_low, y_high)
        # Update start_loc 
        start_loc = next_loc
        list_chemin.append(start_loc)
        if distance_next > distance_max:
            distance_max = distance_next
        # Update distance
        wave_distance = wave_distance + distance_next 
    # Final distance from last storage location to origin
    wave_distance = wave_distance + distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)
    return wave_distance, list_chemin, distance_max