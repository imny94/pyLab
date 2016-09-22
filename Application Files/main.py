import time

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (DictProperty, ListProperty, ObjectProperty, StringProperty)
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget

import firebase
import threading


#-------------------------------GLOBAL FUNCTIONS------------------------------------------

url = "https://sizzling-torch-109.firebaseio.com/" 
token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
firebase = firebase.FirebaseApplication(url, token)

class ServerClass(Widget):
    
    allDataStr = StringProperty()
    allDataList = ListProperty()
    allDataDict = DictProperty()
    
    def accessFirebase(self):
        print "Accessing Firebase, please wait a moment..."
        return firebase.get('/py_lab')    
        
    def CompileAllFirebaseData(self):
        rawdata = self.accessFirebase()
        allDataStr = "" #all data in one string
        allDataList = []
        allDataDict= {}
        for station_num in rawdata.keys():
            allDataList.append(str("%s, %s, %s"%(station_num,rawdata[station_num]['state'],rawdata[station_num]['updateTime'])))
            allDataStr += "%s, %s, %s\n"%(station_num,rawdata[station_num]['state'],rawdata[station_num]['updateTime'])
            allDataDict[str(station_num)] = str(rawdata[station_num]['state'])
        self.allDataStr = str(allDataStr.strip())
        self.allDataList = allDataList
        self.allDataDict = allDataDict
        #return self.allDataStr
            
    def closeapp(self): #gets the app to close
        App.get_running_app().stop()
    
    def colorscheme(self,inp): #this pulls the desired background color of the 'label' depending on state
        if 'Occupied' in inp: return [0.8,0,0,0.8]
        else: return [0,0.8,0,0.8]
        
    def __init__(self,**kwargs):
        super(ServerClass, self).__init__(**kwargs)
        self.CompileAllFirebaseData()        

#-------------------------------STATION CLASS-------------------------------------------

class StationData(Widget):
    
    serverInstance = ServerClass()
    refreshTime = StringProperty()
    stationDict = DictProperty()
    
    def __init__(self, **kwargs):
        super(StationData, self).__init__(**kwargs)
        self.stationDict = self.serverInstance.allDataDict# {'station_1' : {'state': "Occupied", 'updateTime': " time "} , 'station_2' ....}
        self.refreshTime = time.strftime("%H:%M:%S | %d/%m/%y")

        
    def refresh(self):
        self.serverInstance.CompileAllFirebaseData()
        self.stationDict = self.serverInstance.allDataDict
        self.refreshTime = time.strftime("%H:%M:%S | %d/%m/%y")
             
    def getRefreshTime(self):
        return "[i]Last Refresh Time[/i] : %s" %self.refreshTime #we never used this function lol

    def permaRefresh(self,dt):
        print "Refreshing~~"
        self.refresh()

#-------------------------------GUI------------------------------------------------------

class HomeScreen(Screen,StationData):
    stations = StationData()
    constantRefresh = stations.permaRefresh
    clockThread = threading.Thread(target = Clock.schedule_interval, args=((constantRefresh,5)))
    clockThread.start()
       
class AdvancedScreen(Screen,StationData):
    stations = StationData()
       
class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file('Test1.kv')

class MainApp(App):
    
    def build(self):
        return presentation
            
if __name__ == "__main__":
        runApp = MainApp().run()
        mainAppThread = threading.Thread(target = runApp)
        mainAppThread.start()


