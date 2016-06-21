import firebase
import RPi.GPIO as GPIO
import time
import sensorMap

station_1 = {'motion_sensor' : 26 , 'sonar' : [23,24]} #sonar : [trigger,echo]


url = "https://sizzling-torch-109.firebaseio.com/" 
token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
firebase = firebase.FirebaseApplication(url, token)

def uploadToFirebase(motion):
    firebase.put('/','py_lab/station_1',motion)


GPIO.setmode(GPIO.BCM)
PIR_PIN = 26 # probably can link with sensorMap to make this module general
GPIO.setup(PIR_PIN, GPIO.IN)

    
def restart(Trigger,Echo):

    print "letting sensor sleep to re-stabilise"
    time.sleep(2)
    return sonar(Trigger,Echo)

def sonar(sonar_sensor): #sonar_sensor should come in a list, with the form [trigger,echo]
    #This will check the distance to object in front of the motion sensor to determine if the motion is nearby
    #It should include some form of data soothing as results from the ultrasonic sensor are inherently very noisy
    #This function will then return the perceived distance any object is ahead of the sensor
    
    Trigger,Echo = sonar_sensor
    print "Getting Sonar Readings..."
    GPIO.setmode(GPIO.BCM)
    sound_speed = 330 # in meters

    GPIO.setup(Trigger, GPIO.OUT)
    GPIO.setup(Echo, GPIO.IN)

    GPIO.output(Trigger,False)

    counter = 0
    sonarList = []
    while counter <= 50:

        while GPIO.input(Echo) != GPIO.LOW:
            print "waiting for GPIO pin to reset to low ..."
            
        counter += 1
        GPIO.output(Trigger, True)
        time.sleep(0.00001)
        GPIO.output(Trigger, False)
        triggerTime = time.time()
        pulse_start = None

        while GPIO.input(Echo) == GPIO.LOW:
            #print "listening for echo ..."
            elapsedTime = time.time() - triggerTime
            if elapsedTime > 5.0:
                print "failed at %d iteration" %counter
                print "No echo received, re-trying"
                GPIO.cleanup()
                return restart(Trigger,Echo)
            pulse_start = time.time()

        if pulse_start == None:
            print "pulse_start is not defined"
            GPIO.cleanup()
            return restart(Trigger,Echo)
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Echo, GPIO.IN)
        while GPIO.input(Echo) == GPIO.HIGH:
            #print "Echo received"
            pulse_end = time.time()
    
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * (sound_speed/2.0)
        sonarList.append(distance)

    total = sum(sonarList)
    avg = total / 50.0
    GPIO.cleanup()
    return avg


def MOTION(PIR_PIN): # this function should trigger the checking of distance using ultrasonic sensor
    # This function will do the evaluation of the motion it detects and return the state of the station
    
    print "Motion Detected!"
    
    sonar1pin = [23,24] #toy values to make code work, final should obtain values from sensorMap
    sonar2pin = [23,24]
    
    distance1 = sonar(sonar1pin)
    time.sleep(0.5) # this is to prevent any interference of the readings by the ultrasonic sensors
    distance2 = sonar(sonar2pin)

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
                
    sonar1state = eval_sonar(distance1,sonar1pin)
    sonar2state = eval_sonar(distance2,sonar2pin)
    
    if sonar1state == 'valid' or sonar2state == 'valid':
        stationState = "Occupied"
        troubleshootingInfo = None
    else:
        stationState = 'Unoccupied'
        troubleshootingInfo = {'sonar1State' : sonar1state , 
                                'sonar2State' : sonar2state }
        
    return {'state' : stationState ,
            'troubleshootingInfo' : troubleshootingInfo ,
            'updateTime' : time.strftime("%H:%M:%S|%d/%m/%y") }
            
    
def troubleshooting(orig_distance,sonarPin):  #sonarPin = [trigger,echo]
    
    #This should return False if the problem is not solved
    #and return the new distance if the problem is deemed solved
    #This will only run through to do 2 rounds of checking at most, as there are already filters put in place in the sonar method
    
    posDiff = 0.3 # positive distance to register a difference
    history = [orig_distance]
    time.sleep(0.5) # To let sensor have some rest time
    history.append(sonar(sonarPin))
    if abs(history[1] - history[0]) <= posDiff: #no positive difference
        history.append(sonar(sonarPin))
        if abs(history[2] - history[0]) <= posDiff:
            return False
        else:
            return history[2] #return new distance
    else:
        return history[1]
            
            
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


def eval_sonar(distance,sonarPin):
    # This function will evaluate the state in which each sonar is in 
    
    state = sonar_state_checker(distance)
    if state == 'valid' or state == 'too_far' or state == 'blocked':
        return state
    else:
        troubleshooted = troubleshooting(distance,sonarPin)
        if troubleshooted == False:
            return state
        else:
            return sonar_state_checker(troubleshooted)
            
def elapsedTime(activated_time):
    return time.time() - activated_time


        
print "PIR Module Test (CTRL+C to exit)"
time.sleep(2)
print "Ready"
activated_time = time.time()
troubleshootingInfo = None

def updateTime():
    return time.strftime("%H:%M:%S|%d/%m/%y")

try:
    noMotion = {'state' : 'Unoccupied' ,
            'troubleshootingInfo' : troubleshootingInfo ,
            'updateTime' : updateTime()}
    while 1:
        if GPIO.input(PIR_PIN) == GPIO.HIGH:
            motion = MOTION(PIR_PIN)
            noMotion['troubleshootingInfo'] = motion['troubleshootingInfo']
            if motion['state'] == 'Occupied':
                uploadToFirebase(motion)
                activated_time = time.time()
            else:
                if elapsedTime(activated_time) >= 900:
                    uploadToFirebase(noMotion)
                
        else:
            if elapsedTime(activated_time) >= 900: #15 minutes
                
                uploadToFirebase(noMotion)
                activated_time = time.time()
        time.sleep(1.0)
    
    #GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=MOTION)
    #while 1:
    #    time.sleep(100)
except KeyboardInterrupt:
    print " Quit"
    GPIO.cleanup()