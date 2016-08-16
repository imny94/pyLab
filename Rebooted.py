import firebase
import RPi.GPIO as GPIO
import time
import sensorMap


#---------------------------------------SETTING UP STATION PARAMETERS---------------------------------------------------------------------------------------------------------------


stationNum = 1

sensorLocation = sensorMap.sensorMap()
stationData = sensorLocation['station_%d'%stationNum]  #{'Top' : {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24] } ,'Bottom' : {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24]} }

GPIO.setmode(GPIO.BCM)
PIR_PIN = stationData['motion_sensor'] # 26 # probably can link with sensorMap to make this module general
GPIO.setup(PIR_PIN, GPIO.IN)



#---------------------------------------FIREBASE ESSENTIALS-------------------------------------------------------------------------------------------------------------------------


url = "https://sizzling-torch-109.firebaseio.com/" 
token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
firebase = firebase.FirebaseApplication(url, token)

def uploadToFirebase(motion):
    print 'uploading to firebase ...'
    firebase.put('/','py_lab/station_%d'%stationNum , motion)
    print ' \n Upload Complete! \n '
    
        
#---------------------------------------SONAR BLOCK----------------------------------------------------------------------------------------------------------------------------------------


def sonar(sonar_sensor): #sonar_sensor should come in a list, with the form [trigger,echo]
    #This will check the distance to object in front of the motion sensor to determine if the motion is nearby
    Trigger,Echo = sonar_sensor
    print "Getting Sonar Readings..."
    GPIO.setmode(GPIO.BCM)
    sound_speed = 330 # in meters

    GPIO.setup(Trigger, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)

    GPIO.output(Trigger,False) # To wait for sensor to settle)
    time.sleep(2)
    
    GPIO.output(Trigger, True)
    time.sleep(0.00001)
    GPIO.output(Trigger, False)
    
    while GPIO.input(Echo)==0:
        pulse_start = time.time()
    
    while GPIO.input(Echo)==1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * (sound_speed/2.0)
    
    print distance
    return distance

        
#---------------------------------------MOTION BLOCK----------------------------------------------------------------------------------------------------------------------------------------


def MOTION(): # this function should trigger the checking of distance using ultrasonic sensor
    # This function will do the evaluation of the motion it detects and return the state of the station
    
    print "Motion Detected!"
    
    sonarPin = stationData['sonar1'] #[23,24] #toy values to make code work, final should obtain values from sensorMap
    
    print "Calling Sonar sensors 3 times, please wait for 6 seconds"
    
    rawMeasurements = ( sonar(sonarPin) ,  
                        sonar(sonarPin) , 
                        sonar(sonarPin) )
                        # This takes in 3 measurements from the 2 sonar sensors in an alternate fashion, with each sensor given 2 seconds to rest in between
                        
    
    distance = (sum(rawMeasurements)/len(rawMeasurements))
    
    print 'sonar reads distance as : %0.2f' %distance
    
    sonarState = eval_sonar(distance,sonarPin) # Returns either ('valid' , 'too_far' , 'blocked' , 'invalid_lower' , 'invalid_upper')
    
    if sonarState == 'valid': 
        stationState = "Occupied"

    else:
        if sonarState == 'too_far':  # Think through this condition again... There's a troubleshooting function get_issue(state) to determine what's the issue registered
            stationState = 'Unoccupied'
        else:
            stationState = 'Problematic'
            
    if sonarState == 'blocked' or sonarState == 'invalid_lower' or sonarState == 'invalid_upper':
        get_issue(sonarState,sonarPin)
        
        
    
    return {'state' : stationState ,
            'updateTime' : time.strftime("%H:%M:%S|%d/%m/%y") } #Should add an extra parameter to include troubleshooting info here once troubleshooting is done up
            
        
#---------------------------------------EVALUATION BLOCK--------------------------------------------------------------------------------------------------------------------------------


#There are 2 functions here to allow for the addition of a troubleshooting method if needed

def sonar_state_checker(distance):
    
    sensorBlocked = 0.3  # These values need to be fine-tuned, this are just toy values
    upperLimit = 2.0
    lowerLimit = 0.15
    occupiedUpper = 1.0
    
    if distance <= lowerLimit:
        return "invalid_lower"
    elif lowerLimit < distance <= sensorBlocked:
        return 'blocked'
    elif sensorBlocked < distance <= occupiedUpper:
        return 'valid'
    elif occupiedUpper < distance <= upperLimit:
        return 'too_far'
    elif distance > upperLimit:
        return 'invalid_upper'


def eval_sonar(distance,sonarPin):    #  EXTRA ARGUMENT HERE FOR TROUBLESHOOTING  #
    
    # This function will evaluate the state in which each sonar is in 
    
    state = sonar_state_checker(distance)
    return state
    
    #if state == 'valid' or state == 'too_far' or state == 'blocked':
    #    return state
    
#---------------------------------------TROUBLESHOOTING BLOCK-----------------------------------------------------------------------------------------------------------------------


def get_issue(state,sonarPin): #Should call some troubleshooting steps like testing the sensors in this step, but it's not here yet 
                            #but should try to make it call a troubleshooting mehod that is not defined within this thread, so this thread continues to run and not gets stuck here
    if state == 'blocked':
        print 'Sonar sensor is blocked, this is affecting seat readings...'
    elif state == 'invalid_lower':
        print 'Sonar sensor is receiving weird readings where it measures distances smaller than it\' maximum measurable distance... do something...'
    elif state == "invalid_upper":
        print "Sonar sensor is receiving weird readings where it measures distances greater than is's maximum measurable distance... do something..."
        

#---------------------------------------EXECUTIONAL BLOCK----------------------------------------------------------------------------------------------------------------------------


def elapsedTime(activated_time):
    return time.time() - activated_time

print "PIR Module Test (CTRL+C to exit)"
time.sleep(2)
print "Ready"
activated_time = time.time()


def updateTime():
    return time.strftime("%H:%M:%S|%d/%m/%y")

try:
    noMotion = {'state' : 'Unoccupied' ,
            'updateTime' : updateTime()}
    while 1:
        if GPIO.input(PIR_PIN) == GPIO.HIGH:
            detectedMotion = MOTION()
            
            if detectedMotion['state'] == 'Occupied':
                uploadToFirebase(detectedMotion)
                activated_time = time.time()
                
            #else:
            #    if elapsedTime(activated_time) >= 900:
            #        uploadToFirebase(noMotion)
                
        else:
            if elapsedTime(activated_time) >= 900: #15 minutes
                
                uploadToFirebase(noMotion)
                activated_time = time.time()
            print "no motion"
        time.sleep(1.0)
    
    #GPIO.add_event_detect(PIR_PIN_TOP, GPIO.RISING, callback=MOTION)
    #while 1:
    #    time.sleep(100)
    
except KeyboardInterrupt: #CTRL-C TO STOP
    print " Quit"
    GPIO.cleanup()
    
#--------------------------------------END-----------------------------------------------------------------------------------------------------------