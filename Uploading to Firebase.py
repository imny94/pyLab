import firebase
import RPi.GPIO as GPIO
import time
import sensorMap

url = "https://luminous-torch-6388.firebaseio.com/" 
token = "VWfMVhwJ9USQIEgupRTVOOshNJzAS3pDV3WaeKNv"
firebase = firebase.FirebaseApplication(url, token)

sensorLocation = sensorMap.sensorMap()
        
py_lab = {}

for seat,seatInfo in sensorLocation.iteritems():

    if seat not in py_lab:
        py_lab[seat] = {}

while True:
                
    for seatNum in range(1,len(sensorLocation) + 1):
                
                currentTime = time.strftime("%H:%M:%S|%d/%m/%y")
                GPIO_num = sensorLocation['seat_%d'%seatNum]['Pressure_mat']
                
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(GPIO_num, GPIO.IN, GPIO.PUD_DOWN)
                
                if GPIO.input(GPIO_num) == GPIO.HIGH:
                    print " \n SENSOR ACTIVATED * SENSOR ACTIVATED \n "
                    py_lab['seat_%d'%seatNum]['Pressure_Mat'] = True
                    py_lab['seat_%d'%seatNum]['Update_Time'] = currentTime
                else:
                    py_lab['seat_%d'%seatNum]['Pressure_Mat'] = False
                    py_lab['seat_%d'%seatNum]['Update_Time'] = currentTime
                
    print py_lab                    
    firebase.put('/','py_lab',py_lab)