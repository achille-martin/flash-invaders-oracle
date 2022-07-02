#Default packages
import pip
import importlib.util
from bisect import bisect_left
import math
import time
import os
import logging as log_tool

#Third-party packages
try:
    import gpxpy
    from geopy.distance import distance as geo_dist
    import termux
except Exception as e:
    raise Exception('An error occured while importing the third-party packages, please import the packages with requirements.txt')

def setUserParams():
    
    global gpx_file_path, \
           proximity_scale_size, \
           min_distance_to_target, \
           max_distance_to_target, \
           proximity_cut_off_percentage, \
           position_update_period, \
           gps_connection_max_attempt, \
           project_path, \
           logging_level_user
    
    project_path = '/storage/emulated/0/Python/projects/flash-invaders-oracle/'
    gpx_file_path = project_path + 'resources/space_invaders_demo_paris.gpx'
    proximity_scale_size = 10 # number of points on the proximity scale
    min_distance_to_target = 50 # min detectable distance (in m) to target
    max_distance_to_target = 1000 # max detectable distance (in m) to target
    proximity_cut_off_percentage = 25 # display waypoints whose distances are within the lowest x%
    position_update_period = 10.0 # refresh position every x seconds
    gps_connection_max_attempt = 5 # max number of attempts to connect to the GPS 
    logging_level_user = 'INFO' # set debugging level

def main():
    
    logger.debug('Main::main - entering function...')
    
    # Collecting gps data of known points from file
    gpx_data = getGpxDataFromFile(gpx_file_path)
    
    # Creating waypoint list
    waypoint_list = [] 
    for waypoint in gpx_data.waypoints:
        waypoint_list.append([waypoint.latitude, waypoint.longitude])
    logger.debug('Main::main - the list of waypoints is [lat in dd, lon in dd] = ' + str(waypoint_list))
    
    proximity_scale_list = generateProximityScale(proximity_scale_size, min_distance_to_target, max_distance_to_target) 
    
    cut_off_proximity_id = math.ceil(proximity_scale_size*(proximity_cut_off_percentage/100))
    cut_off_proximity_value = proximity_scale_list[cut_off_proximity_id]
    logger.debug('Main::main - the cut-off distance is (in m) = ' + str(cut_off_proximity_value))
    start_time = time.time()
    
    while(True):
        
        os.system('clear')
        
        logger.debug('Main::main - refreshing position every ' + str(position_update_period) + ' s')
        print('Refreshing position every ' + str(position_update_period) + ' s')
        current_location = getCurrentLocation()
        print('Your current location is (lat in dd, lon in dd): ' + str(current_location))
    
        waypoint_distance_list = []
        for waypoint in waypoint_list:
            waypoint_distance_list.append(calculateDistanceToTarget(current_location, waypoint))
        logger.debug('Main::main - The list of distances is (distance in m): '+ str(waypoint_distance_list))
        
        proximity_list = [] 
        for wpt_dist in waypoint_distance_list:
            proximity_value = evaluateProximity(proximity_scale_list, wpt_dist)
            proximity_list.append(proximity_value)
        logger.debug('Main::main - The proximity list is (distance in m): ' + str(proximity_list))
        
        proximity_display_list = []
        min_dist = proximity_list[0]
        for data in proximity_list:
            if data <= cut_off_proximity_value:
                proximity_display_list.append(data) 
            if data < min_dist:
                min_dist = data
        logger.debug('Main::main - The proximity display list is (distance in m) : ' + str(proximity_display_list))
        logger.debug('Main::main - The min distance (distance in m) is = ' + str(min_dist))
        if proximity_display_list:
            print('The closest targets are located within ' + str(proximity_display_list) + ' m from you')
        else:
            print('The closest targets are located over ' + str(min_dist) + ' m from you')

        time.sleep(position_update_period - ((time.time() - start_time) % position_update_period)) 

def getGpxDataFromFile(file_path):
    logger.debug('Main::getGpxDataFromFile - entering function...')
    gpx_file = open(file_path, 'r')
    logger.debug('Main::getGpxDataFromFile - gpx file opened from location: ' + str(file_path))
    gpx = gpxpy.parse(gpx_file)
    logger.debug('Main::getGpxDataFromFile - gpx data parsed: ' + str(gpx))
    logger.debug('Main::getGpxDataFromFile - ...exiting function')
    return gpx

def generateProximityScale(size, min_d, max_d):
    logger.debug('Main::generateProximityScale - entering function...')
    proximity_scale_list = [min_d + x*(max_d - min_d)/(size-1) for x in range(size)] 
    logger.debug('Main::generateProximityScale - the proximity scale list is [distance in m]: ' + str(proximity_scale_list))
    logger.debug('Main::generateProximityScale - ...exiting function')
    return proximity_scale_list

def getCurrentLocation():
    logger.debug('Main::getCurrentLocation - entering function...')
    gps_connection_attempt = 0
    while gps_connection_attempt < gps_connection_max_attempt:
        try:
            logger.debug('Main::getCurrentLocation - listening to android events via termux API')
            event = termux.API.location('gps', 'once')
            if event:
                logger.debug('Main::getCurrentLocation - collected android event at attempt ' 
                             + str(gps_connection_attempt)
                             + ' out of ' 
                             + str(gps_connection_max_attempt))
                break
            else:
                gps_connection_attempt+=1
                logger.warning('Main::getCurrentLocation - could not collect android event. Connection attempt ' 
                            + str(gps_connection_attempt)
                            + ' of '
                            + str(gps_connection_max_attempt))
        except Exception as e:
            gps_connection_attempt+=1
            logger.warning('Main::getCurrentLocation - Exception caught while trying to connect to the gps. Connection attempt ' 
                        + str(gps_connection_attempt) 
                        + ' of ' 
                        + str(gps_connection_max_attempt))
    if gps_connection_attempt == gps_connection_max_attempt:
        logger.exception('Main::getCurrentLocation - Connection to gps failed. \
                         Exception has been caught: Max number or retries to connect to GPS exceeded.')
        raise Exception('Max number of retries to connect to GPS exceeded.')
    if event:
        logger.debug('Main::getCurrentLocation - the content of the event is = ' + str(event))
        event_data=event[1]
        latitude = event_data.get('latitude')
        longitude = event_data.get('longitude')
        logger.debug('Main::getCurrentLocation - the latitude collected (in dd) is = ' + str(latitude))
        logger.debug('Main::getCurrentLocation - the longitude collected (in dd) is = ' + str(longitude))
    logger.debug('Main::getCurrentLocation - ...exiting function')
    return [latitude, longitude]

def calculateDistanceToTarget(origin, target):
    logger.debug('Main::calculateDistanceToTarget - entering function...')
    d = geo_dist(origin, target).m
    logger.debug('Main::calculateDistanceToTarget - The distance between origin and target is (distance in m) = ' + str(d))
    logger.debug('Main::calculateDistanceToTarget - ...exiting function')
    return d

def evaluateProximity(ref_list, distance):
    """ 
    Assumes ref_list is sorted.
    Returns closest value to distance. 
    If two numbers are equally close, return the biggest value. 
    """
    logger.debug('Main::evaluateProximity - entering function...')
    pos = bisect_left(ref_list, distance) 
    logger.debug('Main::evaluateProximity - the index of the closest distance in ref_list is = ' + str(pos))
    if pos == 0: 
        logger.debug('Main::evaluateProximity - Initial index is closest ...exiting function')
        return ref_list[0]
    if pos == len(ref_list): 
        logger.debug('Main::evaluateProximity - last index is closest ...exiting function')
        return ref_list[-1] 
    dist_before = ref_list[pos - 1]
    dist_after = ref_list[pos] 
    if dist_after - distance <= distance - dist_before: 
        logger.debug('Main::evaluateProximity - distance is closer to dist_after ...exiting function')
        return ref_list[pos]
    else: 
        logger.debug('Main::evaluateProximity - distance is closer to dist_before ...exiting function')
        return ref_list[pos-1]
    logger.debug('Main::evaluateProximity - ...exiting function')
    return 0

#Entry point
if __name__=="__main__":
    
    # Setting the params defined by the user
    setUserParams()

    # Instantiating the logger
    logger = log_tool.getLogger(__name__)
    logging_level = logging_level_user
    logger.setLevel(logging_level)
    file_handler = log_tool.FileHandler(project_path + 'main.log', 'w+')
    formatter = log_tool.Formatter('[%(asctime)s][%(levelname)s] - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('Main::Entrypoint - User params and logger set')
    logger.info('Main::Entrypoint - Logger set to = ' + str(logging_level_user))

    # Calling the main function
    main()
