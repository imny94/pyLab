import firebase as fb
import RPi.GPIO as GPIO
import time
import sensorMap
import multiprocessing
import numpy


class Station():
    
#---------------------------------------SETTING UP STATION PARAMETERS---------------------------------------------------------------------------------------------------------------


    def __init__(self,stationNum):
        
        self.stationNum = stationNum
        
        self.name = "station%d" %stationNum
        
        sensorLocation = sensorMap.sensorMap()
        self.stationData = sensorLocation['station_%d'%stationNum]  #{'Top' : {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24] } ,'Bottom' : {'motion_sensor' : 26 , 'sonar1' : [23,24] , 'sonar2' : [23,24]} }
        
        GPIO.setmode(GPIO.BCM)
        self.PIR_PIN = self.stationData['motion_sensor'] # 26 # probably can link with sensorMap to make this module general
        GPIO.setup(self.PIR_PIN, GPIO.IN)
        self.sonarPin = self.stationData['sonar1']
        



#---------------------------------------FIREBASE ESSENTIALS-------------------------------------------------------------------------------------------------------------------------


        url = "https://sizzling-torch-109.firebaseio.com/" 
        token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
        self.firebase = fb.FirebaseApplication(url, token)
    
    def uploadToFirebase(self, motion):
        print "uploading to firebase ...'%s'"%self.currentState
        self.firebase.put('/','py_lab/station_%d'%self.stationNum , motion)
        print ' \n Upload Complete! \n '
    
        
#---------------------------------------SONAR BLOCK----------------------------------------------------------------------------------------------------------------------------------------


    def sonar(self): #sonar_sensor should come in a list, with the form [trigger,echo]
        #This will check the distance to object in front of the motion sensor to determine if the motion is nearby
        Trigger,Echo = self.sonarPin
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
        
        if distance > 3.0:
            print "distance measured is not physically possible, re-measuring..." 
            return self.sonar()
            
        print "station_%d reads %0.2f"%(self.stationNum,distance)
        return distance

        
#---------------------------------------MOTION BLOCK----------------------------------------------------------------------------------------------------------------------------------------


    def MOTION(self): # this function should trigger the checking of distance using ultrasonic sensor
        # This function will do the evaluation of the motion it detects and return the state of the station
        
        print "Motion Detected by station_%d" %self.stationNum
        
        print "Calling Sonar sensors 9 times, please wait for 18 seconds"
        
        rawMeasurements = ( self.sonar() ,  
                            self.sonar() , 
                            self.sonar() ,
                            self.sonar() ,  
                            self.sonar() , 
                            self.sonar() ,
                            self.sonar() ,  
                            self.sonar() , 
                            self.sonar() )
                            # This takes in 3 measurements from the 2 sonar sensors in an alternate fashion, with each sensor given 2 seconds to rest in between
                            
        
        distance = (sum(rawMeasurements)/len(rawMeasurements))
        
        print 'AVERAGED sonar for station_%d reads distance as : %0.2f' %(self.stationNum,distance)
        
        sonarState = self.eval_sonar(distance) # Returns either ('valid' , 'too_far' , 'blocked' , 'invalid_lower' , 'invalid_upper')
        
        if sonarState == 'valid': 
            stationState = "Occupied"
    
        else:
            if sonarState == 'too_far':  # Think through this condition again... There's a troubleshooting function get_issue(state) to determine what's the issue registered
                stationState = 'Unoccupied'
            else:
                stationState = 'Problematic'
                
        if sonarState == 'blocked' or sonarState == 'invalid_lower' or sonarState == 'invalid_upper':
            self.get_issue(sonarState)
            
            
        
        return {'state' : stationState ,
                'updateTime' : time.strftime("%H:%M:%S|%d/%m/%y") } #Should add an extra parameter to include troubleshooting info here once troubleshooting is done up
            
        
#---------------------------------------EVALUATION BLOCK--------------------------------------------------------------------------------------------------------------------------------


#There are 2 functions here to allow for the addition of a troubleshooting method if needed

    def sonar_state_checker(self, distance):
        
        sensorBlocked = 0.0  # These values need to be fine-tuned, this are just toy values
        upperLimit = 3.0
        lowerLimit = 0.0
        occupiedUpper = 1.3
        
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
    
    
    def eval_sonar(self, distance):    #  EXTRA ARGUMENT HERE FOR TROUBLESHOOTING  #
        
        # This function will evaluate the state in which each sonar is in 
        
        state = self.sonar_state_checker(distance)
        return state
        
        #if state == 'valid' or state == 'too_far' or state == 'blocked':
        #    return state
    
#---------------------------------------TROUBLESHOOTING BLOCK-----------------------------------------------------------------------------------------------------------------------


    def get_issue(self, state): #Should call some troubleshooting steps like testing the sensors in this step, but it's not here yet 
                                #but should try to make it call a troubleshooting mehod that is not defined within this thread, so this thread continues to run and not gets stuck here
        if state == 'blocked':
            print 'Sonar sensor is blocked, this is affecting seat readings...'
        elif state == 'invalid_lower':
            print 'Sonar sensor is receiving weird readings where it measures distances smaller than it\' maximum measurable distance... do something...'
        elif state == "invalid_upper":
            print "Sonar sensor is receiving weird readings where it measures distances greater than is's maximum measurable distance... do something..."
        

#---------------------------------------EXECUTIONAL BLOCK----------------------------------------------------------------------------------------------------------------------------


    def elapsedTime(self, activated_time):
        return time.time() - activated_time
        
    def updateTime(self):
            return time.strftime("%H:%M:%S|%d/%m/%y")
            
    def sonarOccupancyChecker(self,q):
        
        print "Running 1 minute check on Sonar for station_%d"%self.stationNum
        
        endTime = time.time() + 60.0
        tolerance = 0.5
        Sonar1Min = []
        
        while time.time() <= endTime:
            Sonar1Min.append(self.sonar())
            
        stdDev = numpy.std(Sonar1Min)
        mean = numpy.mean(Sonar1Min)
        state = self.eval_sonar(mean)
        if state == "valid":
            if -tolerance <= stdDev <= tolerance:
                q.put("OK")
            else:
                print "standard deviation is too large"
                q.put(None)
        else:
            print " state from Sonar sensor != valid"
            q.put(None)
        
        print "For station %d"%self.stationNum
        print "mean is : %0.2f" %mean
        print "Standard Deviation is : %0.2f"%stdDev
        
    def execute(self):

        print "PIR Module Test (CTRL+C to exit)"
        time.sleep(2)
        print "Ready"
        activated_time = time.time()
        counter = 1
        checking = False
        alreadyChecked = False
        motionOccurrance = 0
        minMotionOccurance = 6 #Need to calibrate
        
        
        try:
            noMotion = {'state' : 'Unoccupied' ,
                    'updateTime' : self.updateTime()}
            while 1:
                
                if checking == False:
                    
                    if GPIO.input(self.PIR_PIN) == GPIO.HIGH:
                        detectedMotion = self.MOTION()
                        counter = 0
                        
                        if detectedMotion['state'] == 'Occupied':
                            if alreadyChecked == False:
                                self.currentState = "Occupied"
                                self.uploadToFirebase(detectedMotion)
                                activated_time = time.time()
                                q = multiprocessing.Queue()
                                sonarChecker = multiprocessing.Process(target=self.sonarOccupancyChecker,args=(q,))
                                sonarChecker.start()
                                checking = True
                                checkTime = time.time()
                            else:
                                print 'Already checked, and state pressumed to be Occupied'
                            
                            
                        else:
                            #For the case where motion is detected, but the cause of the motion is not determined to be representative of Occupancy
                            if self.elapsedTime(activated_time) >= 300:
                                self.uploadToFirebase(noMotion)
                            
                    else:
                        if self.elapsedTime(activated_time) >= 300: # 5 minutes to allow for short breaks in between
                            
                            self.currentState = "Unoccupied"
                            self.uploadToFirebase(noMotion)
                            activated_time = time.time()
                            alreadyChecked = False
                        
                        if counter != 0: #This is to allow firebase to be updated whenever the program is re-started
                            self.currentState = "Unoccupied"
                            self.uploadToFirebase(noMotion)
                            counter = 0
                        
                        print "no motion"
                        
                else:
                    if self.elapsedTime(checkTime) <= 60: # Collects the number of times the motion sensor is activated for 1 minute
                        print "countdown : %0.2f"%(self.elapsedTime(checkTime))
                        if GPIO.input(self.PIR_PIN) == GPIO.HIGH:
                            motionOccurrance += 1
                            print "No. of times motion detected : ", motionOccurrance 
                            time.sleep(1.0)
                    else:
                        if motionOccurrance < minMotionOccurance: # Checks if there is enough motion within the 1 minute, if insufficient, state reverts to "Unoccupied"
                                  
                            self.currentState = "Unoccupied"
                            self.uploadToFirebase(noMotion)
                            activated_time = time.time()
                            
                        else:
                            sonarDistCheck = q.get()
                            print "sonarDistCheck value is : ", sonarDistCheck
                            if sonarDistCheck != "OK": #If sonar distance does not check off, but the min motion checks off, the state reverts to "Unoccupied"
                                self.currentState = "TemporaryUnoccupied"
                                activated_time = time.time()
                                tempTime = time.strftime("%H:%M:%S|%d/%m/%y")
                                print "*****   Entering Temporary State for 2 mins... *****"
                            
                        #If there is enough motion and the sonar distance checks off, nothing will be done and the state stays as "Occupied" as per usual    
                            
                        checking = False
                        print "current state is : %s" %self.currentState
                        if self.currentState == "Occupied":
                            alreadyChecked = True
                        motionOccurrance = 0
                        sonarChecker.terminate()
                        
                if self.currentState == "TemporaryUnoccupied":
                    print " In temp State Since : %s"%(tempTime)
                    if self.elapsedTime(activated_time) >= 120:  
                        #This is to account for the fact that the data obtained normally exceeds the tolerance set 
                        #for the standard deviation in the "confirmation" check done to determine occupancy after the station first registers the station as being occupied.
                        #This will thus prevent the switching of states from "Occupied" to "Unoccupied" in firebase due to a 2 min buffer time given
                        #Also, should there really be somebody there, 2 mins should be a good enough buffer time to trigger the motion sensor again, 
                        #which should set the whole checking algorithm running again
                        self.currentState = "Unoccupied"
                        self.uploadToFirebase(noMotion)
                        
                    
                time.sleep(1.0)
            
            #GPIO.add_event_detect(PIR_PIN_TOP, GPIO.RISING, callback=MOTION)
            #while 1:
            #    time.sleep(100)
            
        except KeyboardInterrupt: #CTRL-C TO STOP
            print " Quit"
            GPIO.cleanup()
    
#--------------------------------------END-----------------------------------------------------------------------------------------------------------

def startProcessesFor(stationInstance):
    p = multiprocessing.Process(target=stationInstance.execute)
    p.start()
    print "Process started for %s" %stationInstance.name
    return p
    

station1 = Station(1)
station2 = Station(2)

if __name__ == '__main__':
##    p1 = startProcessesFor(station1)
    p2 = startProcessesFor(station2)
    
def dataCollection(stationClass,sampleNumber):
    dataList = []
    endTime = time.time() + 120.0
    while time.time() <= endTime:
        dataList.append(stationClass.sonar())
    stationClass.firebase.put('/', 'sampleSonar%d'%sampleNumber , dataList)
    print dataList
