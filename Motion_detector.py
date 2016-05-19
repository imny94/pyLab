import firebase
import RPi.GPIO as GPIO
import time
import sensorMap

GPIO.setmode(GPIO.BCM)
PIR_PIN = 26 # probably can link with sensorMap to make this module general
GPIO.setup(PIR_PIN, GPIO.IN)

def sonar(sonar_sensor): #sonar_sensor should come in a list, with the form [trigger,echo]
    #This will check the distance to object in front of the motion sensor to determine if the motion is nearby
    #It should include some form of data soothing as results from the ultrasonic sensor are inherently very noisy
    #This function will then return the perceived distance any object is ahead of the sensor
    
    pass

def MOTION(PIR_PIN): # this function should trigger the checking of distance using ultrasonic sensor
    # This function will do the evaluation of the motion it detects and return the state of the station
    
    print "Motion Detected!"
    distance1 = sonar(sonar1)
    time.sleep(0.5) # this is to prevent any interference of the readings by the ultrasonic sensors
    distance2 = sonar(sonar2)

#-----------This section of the function does the evaluation of the data--------------------------------------------------------------------------------------------------------
    
    # this already assumes that motion is present
    # there should be a specified distance the object is from the sensor for it to detect the station as being occupied
    # There should be some checks on the distance readings for validity
        # i.e There should be some upper limit and lower limit for valid data
            #If data is not valid, double check readings by firing up sonar sensors again (distance longer than the room, distance shorter than 15cm)
                #this reading should be compared to the previous reading and observed for abnormalities, if there is not much difference, try again
                # If diff is not significant, something is off, need to do some troubleshooting
                # sensor will keep notify end-user and stop trying ----- To reset to original motion detection
                # if sensor does suddenly work, it will update end-user
            #There should be a distance to determine when the sonar is being blocked by something place directly in front of it
                #It will try again as above, but if it determines sensor is being blocked intentionally, (like distance shorter than a certain distance, but not to the point of the data being rejected as above)
                    #update end-user
            #If data is further than the upper limit, but still within the length of the room
                #object is too far away to be of concern
    
    sensorBlocked = 0.3
    upperLimit = 2.0
    lowerLimit = 0.15
    

print "PIR Module Test (CTRL+C to exit)"
time.sleep(2)
print "Ready"

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=MOTION)
    while 1:
        time.sleep(100)
except KeyboardInterrupt:
    print " Quit"
    GPIO.cleanup()