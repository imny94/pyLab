import time

class IndvSeatStatus:
    
	def __init__(self, pressure_sensor_data): 
	    # Takes in "True" / "False" from pressure_sensor_data 
	    
	    self.pressure_sensor_data = pressure_sensor_data
	    
	    inp = {} # inp should be in the form {"Pressure_mat : True/False }
	    inp["Pressure_Mat"] = pressure_sensor_data
            self.inp = inp
	    
	def Occupied(self,inp): # inp should be in the form {"Pressure_mat : True/False }
	    
	    hasPressure = inp["Pressure_Mat"]
	    
	    return hasPressure
	                
	
	def getNextState(self): # inp should be in the form {"Pressure_mat : True/False }
	    
	    inp = self.inp
	    
	    if self.Occupied(inp) == True: 
	       nextState = "Occupied"
	            
	    else:
	       nextState = "Unoccupied"                     
                                    
            currentTime = time.strftime("%H:%M:%S|%d/%m/%y") 
                       
            data = {"Update_Time": currentTime,
                        "state": nextState }            
              
            return data 


def py_lab_data():
    import firebase
    
    py_lab = {}   
    
    url = "https://sizzling-torch-109.firebaseio.com/" 
    token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
    firebase = firebase.FirebaseApplication(url, token)
    
    py_lab_data = firebase.get('/py_lab')
    
    for seat,seat_data in py_lab_data.iteritems():
        pressure_sensor_data = seat_data['Pressure_Mat']
        seatStatus = IndvSeatStatus(pressure_sensor_data)
        py_lab[seat] = seatStatus.getNextState()
            
    return py_lab
    
def checker(py_lab):
    checker = {}
    for seat,seat_data in py_lab.iteritems():
        checker[seat] = seat_data['state']
            
    return checker