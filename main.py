#-*-coding:utf8;-*-
#qpy:console

#Requirements:
#Allow location permission
#if needed, install python packages with pip
#Export gpx data from open Street map (export data from Webpage)
#Note: gpx data as XML file is the entry point (or define a set format)

#Limitations
# how to warn user not looking at phone? 
# how to know which waypts have already been visited? (non-essential feature) 
# how to add logs and debugger
# how to add waypoints (non-essential feature)
# how to make user param definition from (yaml) file (non-essential feature)
# how to handle issues? What if gpx file empty or corrupted? 

#Default packages
import pip
import importlib.util
import androidhelper
from bisect import bisect_left
import math
import time
import os

#Third-party packages
third_party_package_list = ['gpxpy', 'geopy']
for package in third_party_package_list:
    is_package_present = importlib.util.find_spec(package)
    #print('Third-party package required: ' + str(package)) 
    if is_package_present is None:
        #print('The package is not installed') 
        #print('Trying to install it with pip...')
        if hasattr(pip, 'main'):
            pip.main(['install', package])
        else:
            pip._internal.main(['install', package])
        #print('...done')
    else:
        pass
        #print ('The package is already installed')
import gpxpy
from geopy.distance import distance as geo_dist

#To be modified by user
def setUserParams():
    global gpx_file_path, proximity_scale_size, min_distance_to_target, max_distance_to_target, proximity_cut_off_percentage, position_update_period
    gpx_file_path = '/storage/emulated/0/qpython/scripts3/flash-invaders-oracle/resources/space_invaders_demo_paris.gpx'
    proximity_scale_size = 10 # number of points on the proximity scale
    min_distance_to_target = 50 # min detectable distance (in m) to target
    max_distance_to_target = 1000 # max detectable distance (in m) to target
    proximity_cut_off_percentage = 25 # display waypoints whose distances are within the lowest x%
    position_update_period = 5.0 # refresh position every x seconds
    
#Main
def main():
    
    gpx_data = getGpxDataFromFile(gpx_file_path)
    waypoint_list = [] 
    for waypoint in gpx_data.waypoints:
        waypoint_list.append([waypoint.latitude, waypoint.longitude])
    #print('The list of waypoints is (wpt_lat, wpt_long): ' + str(waypoint_list))
    
    proximity_scale_list = generateProximityScale(proximity_scale_size, min_distance_to_target, max_distance_to_target) 
    #print('Proximity scale list is (ref_dist): ' + str(proximity_scale_list)) 
    cut_off_proximity_id = math.ceil(proximity_scale_size*(proximity_cut_off_percentage/100))
    cut_off_proximity_value = proximity_scale_list[cut_off_proximity_id] 
    print('The cut off distance is: ' + str(cut_off_proximity_value) + ' m') 
  
    start_time = time.time()
    
    while(True):
        
        os.system('clear')
        print('Refreshed position every ' + str(position_update_period) + ' s')
        
        current_location = getCurrentLocation()
        #current_location = [48.87, 2.35]
        print('Your current location is (user_lat, user_long): ' + str(current_location) + ' decimal degrees')
    
        waypoint_distance_list = []
        for waypoint in waypoint_list:
            waypoint_distance_list.append(calculateDistanceToTarget(current_location, waypoint))
        #print('The list of distances is (wpt_dist_in_m): '+ str(waypoint_distance_list)) 
        
        proximity_list = [] 
        for wpt_dist in waypoint_distance_list:
            proximity_value = evaluateProximity(proximity_scale_list, wpt_dist)
            proximity_list.append(proximity_value)
        #print('The proximity list is (prox_val_in_m): ' + str(proximity_list)) 
        
        proximity_display_list = []
        min_dist = proximity_list[0]
        for data in proximity_list:
            if data <= cut_off_proximity_value:
                proximity_display_list.append(data) 
            if data < min_dist:
                min_dist = data
        #print('The proximity display list is (prox_val_display) : ' + str(proximity_display_list)) 
        if proximity_display_list:
            print('The closest targets are located from you under: ' + str(proximity_display_list) + ' m') 
        else:
            print('The closest targets are located from you over: ' + str(min_dist) + ' m')

        time.sleep(position_update_period - ((time.time() - start_time) % position_update_period)) 

def getGpxDataFromFile(file_path):
    gpx_file = open(file_path, 'r') 
    gpx = gpxpy.parse(gpx_file)
    return gpx

def generateProximityScale(size, min_d, max_d):
    proximity_scale_list = [min_d + x*(max_d - min_d)/(size-1) for x in range(size)] 
    return proximity_scale_list

def getCurrentLocation():
    droid.startLocating() # access gps
    event = droid.eventWait(500).result # get event
    if event['name'] == "location":
        # print(list(event.keys()))
        # print(event)
        event_data=event['data']
        # print(list(event_data.keys()))
        # print(event_data)
        values=list(event_data.values())
        # print(values)
        latitude = values[0]['latitude']
        longitude = values[0]['longitude']
        # print('Your current latitude is:' + str(latitude)) 
        # print('Your current longitude is:' + str(longitude)) 
        # event_data_gps=event_data['gps']
    droid.stopLocating() # close gps
    return [latitude, longitude]

def calculateDistanceToTarget(origin, target):
    d = geo_dist(origin, target).m
    #print('The distance between origin and target is (in m): ' + str(d)) 
    return d

def evaluateProximity(ref_list, distance):
    """ 
    Assumes ref_list is sorted.
    Returns closest value to distance. 
    If two numbers are equally close, return the biggest value. 
    """
    pos = bisect_left(ref_list, distance) 
    if pos == 0: 
        return ref_list[0]
    if pos == len(ref_list): 
        return ref_list[-1] 
    dist_before = ref_list[pos - 1]
    dist_after = ref_list[pos] 
    if dist_after - distance <= distance - dist_before: 
        return ref_list[pos]
    else: 
        return ref_list[pos-1]
    return 0

#Entry point
if __name__=="__main__":
    setUserParams()
    global droid
    droid = androidhelper.Android() 
    main() 