def sensorMap():
    station_1 = { 'motion_sensor' : 5 , 'sonar1' : [27,22] } #sonar : [trigger,echo]
            
    station_2 = { 'motion_sensor' : 12 , 'sonar1' : [23,24] } 
                
    sensorLocation = { 'station_1' : station_1 ,
                       'station_2' : station_2 } 
            
    return sensorLocation
