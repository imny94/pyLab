import RPi.GPIO as GPIO
import time

def restart(Trigger,Echo):

    print "letting sensor sleep to re-stabilise"
    time.sleep(2)
    return sonar(Trigger,Echo)

def sonar(Trigger,Echo):
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
        
while 1:
    try:
        time.sleep(5)
        print sonar(23,24)
    except KeyboardInterrupt:
        print "Quit"
        GPIO.cleanup()
        break
