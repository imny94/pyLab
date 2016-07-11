def sensorMap():
    station_1 = {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24]} #sonar : [trigger,echo]
            
    station_2 = {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24]}
            
    station_3 = {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24]}
    
    sensorLocation = {'station_1' : station_1 ,
                       'station_2' : station_2,
                       'station_3' : station_3 } 
            
    return sensorLocation
