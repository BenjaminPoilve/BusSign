#An IOT wall bus sign



 ![](./image/horloge.png)

We recently moved into our house with a few hacker friend. Great house, lots of space, but trouble is, we have to catch a bus to go to our school. The bus is there about every 20 minutes, so [missing it ](https://www.youtube.com/watch?v=_Tr8KRqyGJk) is major trouble. 

Turned out we had one of Uros's Weio card laying around so we decided to make something out of this [truly great thing](http://we-io.net/hardware/)!

##Concept
The basic idea is simple: display how much time is left till the next bus on the wall. What we need for that is simple:

 * An Internet connected Board with Io
 * A motor
 * An API to the bus service (which can turn out to be harder than expected)

As I sayed earlier, I used a Weio. For those of you who aren't familiar with this card, its basically an openWRT carambola router, with graphic IDE served over AP, python and javascript enabled, and lots of arduino-syntax controlled I/O. [Full disclosure, I worked with Uros last year]
 
##	Setting up the Weio
Its pretty simple:

 * First power-up the board and type `http://weio.local:8080` in your browser. You should see the setup screen:

 
 ![](./image/signup.jpg)
 
 * Once you configured it to your liking, connect it to your local network with the upper right button.
 * The Weio will now restart. To connect to it, connect to your local wifi newtork, open the terminal (on OSX) and type `nmap -sn 192.168.1.*`. (Note: If you don't have Nmap, use `brew install nmap` to install it). You will see the IP adress that the board now has in your local network. In my case: `map scan report for seed-up.home (192.168.1.53) Host is up `
 Connect to it with `http://xxx.xxx.xxx.xxx:8080`
 
 Your are done! Ready to start coding!
 
  ![](./image/start.png)
 
##	Cracking that API

As I said, you will now need to access the data of your local transport system. I don't how it is in other city the situation is basically:

 * The RATP, which is managing the transport, wants a good image, so they have an open API.
 * The API is terrible. Less than Half the information are on it
 * They have an Internal API that is great. But if you use it they will go and get you. For real, happened before.
 
I choosed to take the easy way and do some simple webpage scrapping. Robin on the other hand reversed-engineered the API. I'll put his finding in the annex.
 
I choosed to use the WAP interface because it would be easier to access and is less prone to change. For those of you who don't remember, WAP was internet on mobile beafore the smartphones, at least in France.
 
 
 The basic code looks like that
 
 ```python
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
 ```
 
 
The idea is to make a request to the Webpage, parse it using HTMLparser, which returns an array, and just count until I found were the time left was displayed. 

Not a very clean way to do this, I admit! But at least, wether your local transports have an API or not, you can use this method.


    
##	Making things move!

We choosed to use a stepper motor to move the arrow. This choice was mostly motivated by the fact that I had a stepper in my part box but no servo.. 

####BOM
 * 1 [WEIO](http://www.lextronic.fr/P35497-plate-forme-programmable-weio.html)
 * 1 [DRV8833](https://www.pololu.com/product/2130)
 * 1 [5V stepper](https://www.adafruit.com/products/858)
 * Some wires

Trouble is stepper motor are relative motors. Which means they have no idea where they started and they can loose steps.. We had to have a kind of calibration algorithm. We added a mechanical stop and everytime a bus passed, the motor will home itself by making more than one turn and getting stalled by the stop. 

The DRV8833 wiring is vey simple. It really is a great little part, usefull to have around, wether it is for steppers or DC motors.

![](./image/schematics.png)


Weio has a stepper library so the code is pretty straightforward. 

Here is the finished sketch:

 ```python
 
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
 ```        
        
 

##	Assembling

Turns out, we might be better at coding than painting than at [painting things](https://www.youtube.com/watch?v=u0iUfnqZLsU). Nevertheless we tried to! 

Everything is pretty straightForward, so I just show you the assembled thing:

![](./image/montage.JPG)





Last step is set-up the Weio to automatically start the program on power-up. Once again, Uros did its job well: just go to settings et tick *Run last project on boot*

![](./image/onboot.png)

##Conclusion

Weio really is a great platform to prototype IOT stuff. It took us about 2 hours to get everything working, and three to paint it..  All in all it was a fun afternoon project! See the demo video [here](https://www.youtube.com/watch?v=uPNw7kh0oZM&feature=youtu.be)


Want to meet us? Have a beer? Go to [our Website](seed-up.io)






####Annex
---
As i sayed before, Robin reversed-engineered the RATP API. Here are his findings:

[For you robin]


  