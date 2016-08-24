from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App
import firebase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen , FadeTransition
from kivy.properties import StringProperty, DictProperty , ObjectProperty
import time

#-------------------------------GLOBAL FUNCTIONS------------------------------------------

url = "https://sizzling-torch-109.firebaseio.com/" 
token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
firebase = firebase.FirebaseApplication(url, token)

class ServerClass(Widget):
    
    allData = ObjectProperty()
    
    def accessFirebase(self):
        print "Accessing Firebase, please wait a moment..."
        return firebase.get('/py_lab')
        
    def listAllFirebaseData(self):
        data = self.accessFirebase()
        dataList = []
        for item in data.iteritems():
            dataList.append(item)
        #for key,value in data.iteritems():
        #    dataList.append(key)
        #    for key1, value1 in value.iteritems():
        #        dataList.append(key1)
        #        dataList.append(value1)
        self.allData = ""
        for item in dataList:
            self.allData += str(item) + "\n"
        return self.allData
        
    def __init__(self,**kwargs):
        super(ServerClass, self).__init__(**kwargs)
        self.listAllFirebaseData()
        


#-------------------------------STATION CLASS-------------------------------------------


class StationData(Widget):
    
    serverInstance = ServerClass()
    allStationData = DictProperty()
    refreshTime = StringProperty()
    stationDict = DictProperty()
    
    def __init__(self, **kwargs):
        super(StationData, self).__init__(**kwargs)
        self.allStationData = self.serverInstance.accessFirebase()# {'station_1' : {'state': "Occupied", 'updateTime': " time "} , 'station_2' ....}
        self.refreshTime = time.strftime("%H:%M:%S | %d/%m/%y")
        self.stationDict = {}
        
        numOfStations = 3 ### HARDCODED ------BAD ------------
        for i in range(1,numOfStations + 1):
            self.stationDict['station_%d'%i] = self.getInfo(i)
            
    
    def getInfo(self,stationNum):
        stationData = self.allStationData['station_%d'%stationNum]
        state = stationData['state']
        updateTime = stationData['updateTime']
        return "%s \n Last Update Time : %s" %(state,updateTime)
        
    def refresh(self):
        self.allStationData = self.serverInstance.accessFirebase()
        self.refreshTime = time.strftime("%H:%M:%S | %d/%m/%y")
        for stationNum in range(1,len(self.stationDict) +1 ):
            self.stationDict['station_%d'%stationNum] = self.getInfo(stationNum)
             
    def getRefreshTime(self):
        return "[i]Last Refresh Time[/i] : &s" %self.refreshTime

        
#stations = StationData(numOfStations = 3)
#print "I passed here"
#print stations.stationDict


#-------------------------------GUI------------------------------------------------------

class HomeScreen(Screen,StationData):
    stations = StationData()
    def colorscheme(self,inp): #this pulls the desired background color of the 'label' depending on state
        if 'Occupied' in inp: return [0.8,0,0,0.8]
        else: return [0,0.8,0,0.8]
    
class AdvancedScreen(Screen,StationData):
    stations = StationData()
    
class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file('test.kv')

class MainApp(App):
    
    def build(self):
        
        return presentation
        
if __name__ == "__main__":
    MainApp().run()