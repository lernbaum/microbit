# mbrobot_plusV2.py
# Version 1.4 BD (14.10.2024)
# basiert syntaktisch auf der Variante von TigerJython

from microbit import i2c,pin0,pin1,pin2,pin13,pin14,pin15,sleep,display
import machine
import gc
import music
import neopixel
# import display

_v = 50
_axe = 0.082
_min_angle_val = 25
_max_angle_val = 131
        
def w(d1, s1, d2, s2):
    """
        - soll nicht verwendet werden
        - wird für Motorsteuerung im Hintegrund gebraucht
    """
    try:
        i2c.write(0x10, bytearray([0x00,d1, s1, d2, s2]))      
    except:
        print("Error writing to i2c bus!")
        while True:
            pass
 
def setSpeed(speed):    
    """
        - setze Fahrgeschwindigkeit in willkürlichen Einheiten
        - Standardspeed ist 50
        - speed: -255 bis 255
    """       
    global _v
    if speed > 255:
        _v = 255
    elif speed < -255:
        _v = -255
    else:
        _v = speed 


def stop():
    """
        - stoppe Roboter
        - keinen Einfluss auf LEDs
    """
    w(0, 0, 0, 0) 


def resetSpeed():
    """
        - speed auf Standardwert von 50
    """
    _v = 50          


def forward():
    """
        - setzt den Roboter in eine Vorwärtsbewegung
        - fährt solange vorwärts, bis ein anderer Befehl kommt
    """
    w(0, _v, 0, _v)


def backward():
    """
        - setzt den Roboter in eine Rückwärtsbewegung
        - fährt solange rückwärts, bis ein anderer Befehl kommt
    """
    w(1, _v, 1, _v)          

         
def left():
    """
        - versetzt den Roboter in eine Linksdrehung (Gegenuhrzeigersinn)
        - dreht solange, bis ein anderer Befehl kommt
        - rechter Motor dreht vorwärts, linker Motor dreht rückwärts
    """   
    m = 1
    w(1, int(_v * m), 0, int(_v * m))


def right():
    """
        - versetzt den Roboter in eine Rechtsdrehung (Uhrzeigersinn)
        - dreht solange, bis ein anderer Befehl kommt
        - linker Motor dreht vorwärts, rechter Motor dreht rückwärts
    """   
    m = 1
    w(0, int(_v * m), 1, int(_v * m))


def leftArc(r):
    """
        - versetzt den Roboter in eine Linkskurve (Gegenuhrzeigersinn)
        - r: Radius in m
        - fährt solange, bis ein anderer Befehl kommt
        - rechter Motor dreht schnell vorwärts, linker Motor dreht langsamer vorwärts
        - Mitte des Roboters behält ungefähr den Vorwärtsspeed bei
    """   
    v = abs(_v)
    if r < _axe:
        v1 = 0
    else:
        f = (r - _axe) / (r + _axe) * (1 - v * v / 200000)             
        v1 = int(f * v)
    if _v > 0:
        w(0, v1, 0, v)
    else:
        w(1, v, 1, v1)


def rightArc(r):
    """
        - versetzt den Roboter in eine Rechtskurve (Uhrzeigersinn)
        - r: Radius in m
        - fährt solange, bis ein anderer Befehl kommt
        - linker Motor dreht schnell vorwärts, rechter Motor dreht langsamer vorwärts
        - Mitte des Roboters behält ungefähr den Vorwärtsspeed bei
    """   
    v = abs(_v)
    if r < _axe:
        v1 = 0
    else:
        f = (r - _axe) / (r + _axe) * (1 - v * v / 200000)        
        v1 = int(f * v)
    if _v > 0:
        w(0, v, 0, v1)
    else:
        w(1, v1, 1, v)    


def getDistance():
    """
        - sendet ein Signal aus dem Ultraschallsensor (vorne) und misst Reflexionszeit
        - Rückgabewert in Zentimeter
        - Rückgabewert Ganzzahl zwischen 0 und maximal 255 Zentimeter
        - Rückgabewert von 255: kein Signal erhalten oder zu weit weg
    """   
    max_time = int(255/34300*1000000)
    trig = pin13
    echo = pin14
    trig.write_digital(1)
    trig.write_digital(0)
    micros = machine.time_pulse_us(echo, 1, max_time)
    
    if micros < 0: # error
        return 255
    
    t_echo = micros / 1000000
    return int((t_echo/2)*34300-1)


class Motor:
    def __init__(self, id):
        self._id = 2 * id
        
    def _w(self, d, s):
        try:
            i2c.write(0x10, bytearray([self._id, d, s]))
        except:
            print("Please switch on mbRobot!")
            while True:
                pass               

    def rotate(self, s):
        p = abs(s) 
        if s > 0:
            self._w(0, p)    
        elif s < 0:
            self._w(1, p) 
        else:   
            self._w(0, 0)


def setLED(state):  
    """
        - steuert beide LEDs (rot, vorne)
        - state: 0 (aus) oder 1 (an)
        - Zustand wird beibehalten, bis ein neuer LED Befehl kommt
        - gleichbedeutend mit setLEDl(state) und setLEDr(state)
    """     
    i2c.write(0x10, bytearray([0x0B, state]))
    i2c.write(0x10, bytearray([0x0C, state]))
        
 
def setLEDl(state):
    """
        - steuert die linke LED (rot, vorne)
        - state: 0 (aus) oder 1 (an)
        - Zustand wird beibehalten, bis ein neuer LED Befehl kommt
    """  
    i2c.write(0x10, bytearray([0x0B, state]))
    
  
def setLEDr(state):
    """
        - steuert die rechte LED (rot, vorne)
        - state: 0 (aus) oder 1 (an)
        - Zustand wird beibehalten, bis ein neuer LED Befehl kommt
    """ 
    i2c.write(0x10, bytearray([0x0C, state]))


def clearLED():
    """
        - löscht beide LEDs (rot, vorne)
        - gleichbedeutend mit setLED(0)
    """   
    i2c.write(0x10, bytearray([0x0B, 0]))
    i2c.write(0x10, bytearray([0x0C, 0]))

np_rgb_pixels = neopixel.NeoPixel(pin15, 4)


def setRGB(r, g, b): 
    """
        - steuert die RGB LEDs (unten)
        - steuert alle 4 LEDs gleichzeitig
        - r,g,b: Farbwerte zwischen 0 und 255
    """      
    for id in range(len(np_rgb_pixels)):
        np_rgb_pixels[id] = (r,g,b)
    
    np_rgb_pixels.show()


def setRGBl1(r, g, b):
    """
        - steuert die linke vordere RGB LED (unten)
        - r,g,b: Farbwerte zwischen 0 und 255
        - Zustand wird beibehalten, bis ein neuer RGB Befehl kommt
    """       
    np_rgb_pixels[0] = (r,g,b)
    np_rgb_pixels.show()


def setRGBl2(r, g, b):   
    """
        - steuert die linke hintere RGB LED (unten)
        - r,g,b: Farbwerte zwischen 0 und 255
        - Zustand wird beibehalten, bis ein neuer RGB Befehl kommt
    """    
    np_rgb_pixels[1] = (r,g,b)
    np_rgb_pixels.show()


def setRGBr1(r, g, b):    
    """
        - steuert die rechte vordere RGB LED (unten)
        - r,g,b: Farbwerte zwischen 0 und 255
        - Zustand wird beibehalten, bis ein neuer RGB Befehl kommt
    """   
    np_rgb_pixels[3] = (r,g,b)
    np_rgb_pixels.show()


def setRGBr2(r, g, b):
    """
        - steuert die rechte hintere RGB LED (unten)
        - r,g,b: Farbwerte zwischen 0 und 255
        - Zustand wird beibehalten, bis ein neuer RGB Befehl kommt
    """   
    np_rgb_pixels[2] = (r,g,b)
    np_rgb_pixels.show()


def clearRGB():
    """
        - löschte alle RGB LEDs (unten)
        - gleichbedeutend mit setRGB(0,0,0)
    """   
    for id in range(len(np_rgb_pixels)):
        np_rgb_pixels[id] = (0,0,0)
    np_rgb_pixels.show()
    

def setBuzzer(state):
    """
        - lässt einen Ton auf dem Buzzer abspielen
        - state: Frequenz des tons zwischen etwa 40 und 16'000
        - je höher die Frequenz, desto höher der Ton
        - Ton spielt genau 0.1 Sekunden
    """  
    music.pitch(state, 100, wait=False)
    
def ir_read_values_as_byte():
    """
        - muss nicht direkt verwendet werden
        - wird im Hintergrund gebraucht, um Daten auszulesen
    """
    i2c.write(0x10, bytearray([0x1D]))
    buf = i2c.read(0x10, 1)
    return ~buf[0]  


def show_number(value, max):
    """ 
        - lässt die LED Matrix aufleuchten
        - Die Anzahl leuchtender LEDs ist im Verhältnis von value/max
        - value: anzuzeigender Wert
        - max: im Verhältnis zum Maximum
    """      
    if value > max:
        value = max
        
    pixels = int(value/max*25)    
    display.clear()
    
    for i in range(pixels):
        x = i%5
        y = i//5
        display.set_pixel(x,y,9)


def setAlarm(on):
    """ 
        - lässt eine kurze Alarmmelodie abspielen
        - on: True zum Abspielen, False zum stoppen
    """  
    if on:
        music.play(_m, wait = False, loop = True)    
    else:
        music.stop()
        
class IR:
    R2 = 0
    R1 = 1
    M = 2
    L1 = 3
    L2 = 4 
    masks = [0x01,0x02,0x04,0x08,0x10]
   
class IRSensor:
    def __init__(self, index):
        self.index = index
        
    def read_digital(self):
        byte = ir_read_values_as_byte()
        return (byte & IR.masks[self.index]) >> self.index

try:
        
    irLeft = IRSensor(IR.L1)
    irRight = IRSensor(IR.R1)
    irL1 = IRSensor(IR.L1)
    irR1 = IRSensor(IR.R1)
    irL2 = IRSensor(IR.L2)
    irR2 = IRSensor(IR.R2)
    irM = IRSensor(IR.M)
    pin2.set_pull(pin2.NO_PULL)
    motL = Motor(0)
    motR = Motor(1)
    delay = sleep


    def init():
        try: # fails if micro:bit not inserted into maqueen
            stop()
            
            pin13.write_digital(0)  # ultrasonic trigger
            pin14.read_digital()    # ultrasonic echo
            # reset LEDs at startup    
            clearRGB()
            clearLED()
        except:
            pass
            
    init()
except:
    pass