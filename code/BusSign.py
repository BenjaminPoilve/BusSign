
from weioLib.weio import *
from things.output.motor.stepper import Stepper, FULL_STEP, HALF_STEP
import urllib2, json, re

anglepos=-5
s=0


def setup():
    global s
    s = Stepper(513, 3,4,5,6)
    # Set FULL_STEP mode (360 degree)
    s.setStepperMode(FULL_STEP)
    # Set stepper motor rotation speed to 30 revolutions per second
    s.setSpeed(10)
    attach.process(myProcess)
    
def gotopos(angle):
    global s
    global anglepos
    s.step((angle-anglepos)*530/20)
    anglepos=angle
    
    
    
def myProcess():
    global anglepos
    gotopos(19)
    flag=0
    while True :
        from HTMLParser import HTMLParser  

        class MyHTMLParser(HTMLParser):
            def __init__(self):
              HTMLParser.__init__(self)
              self.data = []
            def handle_data(self, data):
              self.data.append(data)
        p = MyHTMLParser()
        f = urllib2.Request('http://wap.ratp.fr/siv/schedule?service=next&reseau=bus&referer=station&lineid=B396&stationname=les+anemones&submitAction=Valider')
        f.add_header('User-agent', 'Mozilla 5.10')
        res = urllib2.urlopen(f)
        html = res.read()
        p.feed(html)
        try:
            timeleft= p.data[26]
            print timeleft
            try:
                inttimeleft= int(re.search(r'\d+', timeleft).group())
                print inttimeleft
                gotopos(min(inttimeleft,19))
                flag=1
            except:
                if(timeleft=="A l'approche"):
                     gotopos(0)
                     print "bus a l'approche"
                     flag=1
                elif (flag==1):
                    anglepos= -5
                    gotopos(19)
                    flag=0

        except:
            print "error occured"
        
            
            
        
        p.close()
       
                
        delay(10000)
        
        
