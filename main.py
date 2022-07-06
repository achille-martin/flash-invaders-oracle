#Default packages
from bisect import bisect_left
import math
import time
import os
import logging as log_tool
import yaml
import threading

#Third-party packages
try:
    import gpxpy
    from geopy.distance import distance as geo_dist
    import termux
except Exception as e:
    raise Exception('An error occured while importing the third-party packages, please import the packages with requirements.txt')

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
    
    # Saving main loop start time to serve as ref for refresh updates
    loop_start_time = time.time()
    logger.debug('Main::main - the main loop start time is = ' + str(loop_start_time))
    
    # Initialising variables for threaded functions
    return_dict_threaded_func = {}
    logger.debug('Main::main - return dict for threaded functions initialised to = ' + str(return_dict_threaded_func))
    lock_dict_threaded_func = {}
    logger.debug('Main::main - lock dict for threaded functions initialised to = ' + str(lock_dict_threaded_func))

    # Initialising location function variables
    current_location = None
    logger.debug('Main::main - current location initialised to = ' + str(current_location))
    location_access_lock = threading.Lock()
    logger.debug('Main::main - location access lock initialised to = ' + str(location_access_lock.locked()))
    location_id = "location"
    logger.debug('Main::main - location identifier initialised to = ' + str(location_id))

    while(True):
        
        os.system('clear')
        
        logger.debug('Main::main - refreshing position every ' + str(position_update_period) + ' s')
        print('Refreshing position every ' + str(position_update_period) + ' s')
        
        current_location = makeThreaded(location_id, lock_dict_threaded_func, return_dict_threaded_func)(getCurrentLocation)() # non-threaded version is: current_location = getCurrentLocation()
        logger.debug('Main::main - the content of return dict for threaded functions is = ' + str(return_dict_threaded_func))
        if location_id in return_dict_threaded_func:
            current_location = return_dict_threaded_func[location_id]
        else:
            current_location = None

        logger.debug('Main::main - current location is = ' + str(current_location))
        if current_location is None:
            print('Your current location has not been determined yet. Please wait.')
            # Force refresh every 2 seconds until location is collected
            time.sleep(2)
            continue
        else:
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

        time.sleep(position_update_period - ((time.time() - loop_start_time) % position_update_period)) 

# Inspired from https://stackoverflow.com/questions/45895189/python-decorator-with-multithreading#45895455
# and from https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python 
def makeThreaded(return_id=None, lock_dict={}, return_dict={}):
    
    logger.debug('Main::makeThreaded - entering function...')
    
    # Creating default lock for no-param calls
    thread_lock = threading.Lock()
    
    # Setting return id for return dict and lock dict if required
    if return_id is not None:
        logger.debug('Main::makeThreaded - return identifier is = ' + str(return_id))
        if not return_id in return_dict:
            logger.debug('Main::makeThreaded - updating return dict with key return identifier')
            return_dict[return_id]=None
            logger.debug('Main::makeThreaded - updating lock dict with key return identifier')
            lock_dict[return_id]=threading.Lock()
        # Updating thread lock variable for clarity
        thread_lock=lock_dict[return_id]
    
    def decorator(func):
        def threadWrapper(*args, **kwargs):
            def funcWrapper(*args, **kwargs):
                with thread_lock:
                    
                    ret = func(*args, **kwargs)
                    logger.debug('Main::makeThreaded - ...ending threaded function')
                    logger.debug('Main::makeThreaded - return from threaded function is = ' + str(ret))
                    logger.debug('Main::makeThreaded - return identifier after threaded function is = ' + str(return_id))
                    
                    if return_id is not None:
                        return_dict[return_id] = ret
                        logger.debug('Main::makeThreaded - return dict content after threaded function is = ' + str(return_dict))
                    
                    logger.debug('Main::makeThreaded - ...ending function')
            
            logger.debug('Main::makeThreaded - thread lock state before threaded function is = ' + str(thread_lock.locked()))
             
            if not thread_lock.locked():
                logger.debug('Main::makeThreaded - starting threaded function...')
                thread = threading.Thread(target=funcWrapper, args=args, kwargs=kwargs)
                thread.daemon = True
                thread.start()
            else:
                logger.debug('Main::makeThreaded - ...ending function') 
            
            return funcWrapper
        return threadWrapper
    return decorator

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
    
    # Initialising gps connection attempts
    gps_connection_attempt = 1
        
    while gps_connection_attempt <= gps_connection_max_attempt:
            
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
                logger.warning('Main::getCurrentLocation - could not collect android event. Connection attempt ' 
                            + str(gps_connection_attempt)
                            + ' of '
                            + str(gps_connection_max_attempt))
                gps_connection_attempt+=1

        except Exception as e:
            logger.warning('Main::getCurrentLocation - Exception caught while trying to connect to the gps. Connection attempt ' 
                        + str(gps_connection_attempt) 
                        + ' of ' 
                        + str(gps_connection_max_attempt))
            gps_connection_attempt+=1
        
    if gps_connection_attempt >= gps_connection_max_attempt:
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
    
    current_location = [latitude, longitude]
    logger.debug('Main::getCurrentLocation - ...exiting function')
    
    return current_location

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
        logger.debug('Main::evaluateProximity - distance is closer to first index ...exiting function')
        return ref_list[0]
    if pos == len(ref_list):
        logger.debug('Main::evaluateProximity - distance is closer to last index ...exiting function')
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
    
    # Loading the params defined by the user from config file
    try:
        with open('config/user_config.yaml', 'r') as config_file:
            user_config = yaml.safe_load(config_file)
    except Exception as e:
        raise Exception(' User params could not be loaded. Please.verify your configuration.')

    # Setting the params defined by the user
    project_folder_path = user_config['path']['project_folder']
    gpx_file_path = project_folder_path + user_config['path']['gpx_file_within_project_folder']
    main_log_file_path = project_folder_path + user_config['path']['main_log_file_within_project_folder']
    min_distance_to_target = user_config['radar']['min_distance_to_target'] 
    max_distance_to_target = user_config['radar']['max_distance_to_target']
    proximity_scale_size = user_config['radar']['proximity_scale_size']
    proximity_cut_off_percentage = user_config['radar']['proximity_cut_off_percentage']
    position_update_period = user_config['location']['position_update_period']
    gps_connection_max_attempt = user_config['location']['gps_connection_max_attempt']
    logging_level = user_config['debug']['logging_level']

    # Instantiating the logger
    logger = log_tool.getLogger(__name__)
    logger.setLevel(logging_level)
    file_handler = log_tool.FileHandler(main_log_file_path, 'w+')
    formatter = log_tool.Formatter('[%(asctime)s][%(levelname)s] - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info('Main::Entrypoint - User params and logger set')
    logger.info('Main::Entrypoint - Logger set to = ' + str(logging_level_user))

    # Calling the main function
    main()
