# mbrobot_plusV2.py
# Version 1.5 BD (16.10.2024)
# basiert syntaktisch auf der Vorlage von TigerJython

from microbit import i2c,pin0,pin1,pin2,pin13,pin14,pin15,sleep,display
import machine
import music
import neopixel

_v = 50
_axe = 0.082
        
def w(d1, s1, d2, s2):
    """
        - helper function
        - should not be called directly
    """
    try:
        i2c.write(0x10, bytearray([0x00,d1, s1, d2, s2]))      
    except:
        print(" > Error writing to i2c bus!")
 
def setSpeed(speed):    
    """
        - set speed (arbitrary units)
        - default speed 50
        - range: -255 to 255
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
        - stop robot motion
        - doesn't affect LEDs
    """
    w(0, 0, 0, 0) 


def reset():
    """
        - stop robot motion
        - turn off LEDs
        - reset speed to default 50
    """
    resetSpeed()
    stop()
    clearRGB()
    clearLED()
    display.clear()

def resetSpeed():
    """
        - set speed to default 50
    """
    global _v
    _v = 50          


def forward():
    """
        - forward motion
        - keeps driving until another command is given
    """
    w(0, _v, 0, _v)


def backward():
    """
        - backward motion
        - keeps driving until another command is given
    """
    w(1, _v, 1, _v)          

         
def left():
    """
        - left rotation (counterclockwise)
        - keeps rotating until another command is given
        - right motor spins forward, left motor backward
    """   
    m = 1
    w(1, int(_v * m), 0, int(_v * m))


def right():
    """
        - right rotation (clockwise)
        - keeps rotating until another command is given
        - left motor spins forward, right motor backward
    """   
    m = 1
    w(0, int(_v * m), 1, int(_v * m))


def leftArc(radius):
    """
        - turns the robot to the left (counterclockwise)
        - r: radius in m
        - keeps rotating until another command is given
        - right motor spins forward fast, left motor spins forward slow
        - robot center drives at forward speed
    """   
    v = abs(_v)
    if radius < _axe:
        v1 = 0
    else:
        f = (radius - _axe) / (radius + _axe) * (1 - v * v / 200000)             
        v1 = int(f * v)
    if _v > 0:
        w(0, v1, 0, v)
    else:
        w(1, v, 1, v1)


def rightArc(radius):
    """
        - turns the robot to the right (clockwise)
        - radius in m
        - keeps rotating until another command is given
        - left motor spins forward fast, right motor spins forward slow
        - robot center drives at forward speed
    """   
    v = abs(_v)
    if radius < _axe:
        v1 = 0
    else:
        f = (radius - _axe) / (radius + _axe) * (1 - v * v / 200000)        
        v1 = int(f * v)
    if _v > 0:
        w(0, v, 0, v1)
    else:
        w(1, v1, 1, v)    


def getDistance():
    """
        - sends a signal from the ultrasonic sensor (front) and measures the reflection time
        - return value in centimeters
        - return value is an integer between 0 and a maximum of 255
        - return value of 255: no signal received or object is too far away
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
            print(" > Please switch on Maqueen.")              

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
        - controls both LEDs (red, in front)
        - state: 0 (off) or 1 (on)
        - state is maintained until a new LED command is given
        - equivalent to setLEDl(state) and setLEDr(state).
    """     
    i2c.write(0x10, bytearray([0x0B, state]))
    i2c.write(0x10, bytearray([0x0C, state]))
        
 
def setLEDl(state):
    """
        - controls the left LED (red, in front)
        - state: 0 (off) or 1 (on)
        - state is maintained until a new LED command is given
    """  
    i2c.write(0x10, bytearray([0x0B, state]))
    
  
def setLEDr(state):
    """
        - controls the right LED (red, in front)
        - state: 0 (off) or 1 (on)
        - state is maintained until a new LED command is given
    """  
    i2c.write(0x10, bytearray([0x0C, state]))


def clearLED():
    """
        - turns off both LEDs (red, in front)
        - equivalent to setLED(0)
    """  
    i2c.write(0x10, bytearray([0x0B, 0]))
    i2c.write(0x10, bytearray([0x0C, 0]))

def setRGB(r, g, b): 
    """
        - controls the RGB LEDs on the bottom
        - controls all 4 LEDs simultaneously
        - r, g, b: color values between 0 and 255
    """      
    for id in range(len(np_rgb_pixels)):
        np_rgb_pixels[id] = (r,g,b)
    
    np_rgb_pixels.show()


def setRGBl1(r, g, b):
    """
        - controls RGB LED on the bottom (left, front)
        - r, g, b: color values between 0 and 255
    """      
    np_rgb_pixels[0] = (r,g,b)
    np_rgb_pixels.show()


def setRGBl2(r, g, b):   
    """
        - controls RGB LED on the bottom (left, back)
        - r, g, b: color values between 0 and 255
    """      
    np_rgb_pixels[1] = (r,g,b)
    np_rgb_pixels.show()


def setRGBr1(r, g, b):    
    """
        - controls RGB LED on the bottom (right, front)
        - r, g, b: color values between 0 and 255
    """   
    np_rgb_pixels[3] = (r,g,b)
    np_rgb_pixels.show()


def setRGBr2(r, g, b):
    """
        - controls RGB LED on the bottom (right, back)
        - r, g, b: color values between 0 and 255
    """   
    np_rgb_pixels[2] = (r,g,b)
    np_rgb_pixels.show()


def clearRGB():
    """
        - turns off all RGB LEDs on the bottom
        - equivalent to setRGB(0,0,0)
    """   
    for id in range(len(np_rgb_pixels)):
        np_rgb_pixels[id] = (0,0,0)
    np_rgb_pixels.show()
    

def setBuzzer(frequency):
    """
        - plays a sound on the buzzer
        - frequency: frequency of the sound between 40 and 16'00 Hz
        - higher frequency means higher pitch
        - sound plays for 0.1 seconds
    """
    music.pitch(frequency, 100, wait=False)
    
def ir_read_values_as_byte():
    """
        - helper function
        - should not be called directly
    """
    i2c.write(0x10, bytearray([0x1D]))
    buf = i2c.read(0x10, 1)
    return ~buf[0]  


def show_number(value, max):
    """ 
        - turn on LED matrix on micro:bit
        - number of lit LEDs is proportional to value/max
    """      
    if value > max:
        value = max
        
    pixels = int(value/max*25)    
    display.clear()
    
    for i in range(pixels):
        x = i%5
        y = i//5
        display.set_pixel(x,y,9)


def alarm():
    """ 
        - plays a short alarm melody
    """  
    _m = music.POWER_UP
    music.play(_m, wait = False, loop = False)    

    for i in range(10):
        setLED(1)
        setRGB(255,0,0)
        delay(100)
        setLED(0)
        setRGB(0,0,0)
        delay(100)

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
    np_rgb_pixels = neopixel.NeoPixel(pin15, 4)
    delay = sleep


    def init():
        pin13.write_digital(0)  # ultrasonic trigger
        pin14.read_digital()    # ultrasonic echo
        reset()
  
    init()
    print(" > Maqueen is running...")
except:
    print(" > micro:bit not connected to Maqueen?")

