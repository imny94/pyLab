from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App
import firebase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen , FadeTransition
from kivy.properties import StringProperty, DictProperty
import time

#-------------------------------GLOBAL FUNCTIONS------------------------------------------

url = "https://sizzling-torch-109.firebaseio.com/" 
token = "4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq"
firebase = firebase.FirebaseApplication(url, token)

class ServerClass(Widget):
    
    def accessFirebase(self):
        return firebase.get('/py_lab')
        
    def listAllData(self):
        data = self.accessFirebase()
        dataList = []
        for item in data.iteritems():
            dataList.append(item)
        final = ""
        for item in dataList:
            final += str(item) + "\n"
        return final
        


#-------------------------------STATION CLASS-------------------------------------------


class StationData(Widget):
    
    serverInstance = ServerClass()
    allStationData = DictProperty()
    refreshTime = StringProperty()
    
    def __init__(self, **kwargs):
        super(StationData, self).__init__(**kwargs)
        self.allStationData = self.serverInstance.accessFirebase()# {'station_1' : {'state': "Occupied", 'updateTime': " time "} , 'station_2' ....}
        self.refreshTime = time.strftime("%H:%M:%S|%d/%m/%y")
    
    def getInfo(self,stationNum):
        stationData = self.allStationData['station_%d'%stationNum]
        state = stationData['state']
        updateTime = stationData['updateTime']
        return "%s \n Last Update Time : %s" %(state,updateTime)
        
    def refresh(self):
        self.allStationData = self.serverInstance.accessFirebase()
        self.refreshTime = time.strftime("%H:%M:%S|%d/%m/%y")
        
    def getRefreshTime(self):
        return "[i]Last Refresh Time[/i] : &s" %self.refreshTime
        
stations = StationData()
print "I passed here"
print stations.getInfo(1)


#-------------------------------GUI------------------------------------------------------

class HomeScreen(Screen,StationData,ServerClass):
    stations = StationData()
    server = ServerClass()
    pass
    
class AdvancedScreen(Screen,StationData,ServerClass):
    stations = StationData()
    server = ServerClass()
    pass
    
class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file('test.kv')

class MainApp(App):
    
    def build(self):
        #stations = StationData()
        #stations.getInfo()
        #stations.refresh()
        #stations.getRefreshTime()
        return presentation
        
if __name__ == "__main__":
    MainApp().run()