import firebase
import time 
url = 'https://sizzling-torch-109.firebaseio.com/'
token = '4tWC7ZSixm6Xp0HNVzyEWg3urMtxKlTnDLUwZXUq'
firebase = firebase.FirebaseApplication(url, token)

#firebase.put('/','py_lab',{'Work_Station_1': {'status': 'Occupied','timer':0}, 'Work_Station_2': {'status': 'Unoccupied','timer':0}, 'Work_Station_3': {'status': 'Occupied','timer':0}})
    
def timeformatter(seconds):
    h=seconds//3600.0
    m=(seconds%3600)//60
    s= (seconds%3600)%60
    rethms = ("%1.0fh%1.0fm%1.0fs"%(h,m,s))
    retms = ("%1.0fm%1.0fs"%(m,s))
    rets = ("%1.0fs"%s)
    if h ==0 and m ==0: return rets
    elif h == 0 and m!=0: return retms
    else: return rethms


class StopWatch:     
    def __init__(self,endTime=None,startTime = None,currentTime = time.time(),status = False):
        self.endTime = endTime
        self.startTime = startTime
        self.currentTime = currentTime
        self.status = status
    def start(self):
        self.startTime = time.time()
        self.status = True
    def stop(self):
        self.endTime = time.time()
        self.status = False
    def reset(self):
        self.endTime = None
        self.startTime = None
        self.status = False    
    def getStartTime(self): return self.startTime
    def getEndTime(self): return self.endTime
    def getElapsedTime(self):
        if self.endTime == None and self.startTime == None: return 0
        if self.endTime == None and self.startTime != None: return float(round((time.time() - self.startTime),0))
        else: return float(round((self.endTime - self.startTime),0))   
sw1 = StopWatch()
sw2 = StopWatch()
sw3 = StopWatch()
watchlist = [sw1,sw2,sw3]

def changestatus(workstationnumber,value):
    labstatus = firebase.get('/py_lab')
    if labstatus['Work_Station_%s'%workstationnumber]['status'] == value: return firebase.put('/','py_lab/Work_Station_%s'%workstationnumber,labstatus['Work_Station_%s'%workstationnumber])
    else:
        firebase.put('/','py_lab/Work_Station_%s/status'%workstationnumber,'Checking Vacancy\nTimer: ')
        s = watchlist[workstationnumber-1] #workstation1 is sw1, workstation2 is sw2, etc
        if s.status == True: pass
        if s.status == False: s.start()
        while s.getElapsedTime() <= 60.0:
            firebase.put('/','py_lab/Work_Station_%s/timer'%workstationnumber,str(timeformatter(float(s.getElapsedTime()))))
            if s.getElapsedTime() > 60.0:
                s.stop()
                s.reset()
                firebase.put('/','py_lab/Work_Station_%s',{'status':value, 'timer':0})
                break
        pass

    