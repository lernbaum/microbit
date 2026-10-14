# robot.py
# Version 2.0 BD (13.10.2026)

from microbit import i2c,pin13,pin14,pin15,sleep,display
import machine
from utime import sleep_us
import music
import neopixel


__mot = bytearray([0,0,0,0,0]) # (0, dirl, sl, dirr, sr)

__mappingv21 = [2,1,3,0,4]
__mappingv20 = [2,3,1,4,0]
__mapping = None

def __haltOnI2CDisconnect():
    print(" > Maqueen connection to microbit lost. Beware of faulty connections. Stopping program.")
    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, 9)

    exit(1)

def __i2cWrite(addr, data):
    try:
        i2c.write(addr, data)
    except OSError as e:
        if e.args and e.args[0] == 19:
            __haltOnI2CDisconnect()
        raise

def __i2cRead(addr, n):
    try:
        return i2c.read(addr, n)
    except OSError as e:
        if e.args and e.args[0] == 19:
            __haltOnI2CDisconnect()
        raise

def __checkVersion():
    if __mapping is None:
        raise Exception("use setVersion() before driving")

def __drive():
    __i2cWrite(0x10, __mot)
    delay(1)

def reset():
    """
        - stop robot motion
        - turn off LEDs
        - reset speed to default 50
    """
    __mot[1] = 0; __mot[2] = 0; __mot[3] = 0; __mot[4] = 0
    __drive()
    setDisco(0,0,0)
    delay(1)
    setHeadlight(0)
    delay(1)
    display.clear()
    delay(1)

def __clamp(speed):
    if speed < 0:
        dir = 1
    else:
        dir = 0
    return dir, min(abs(int(speed)), 255)

def drive(speed):
    """
        - drives both motors
        - negative values mean backward
        - keeps rotating until another command is given
    """
    __checkVersion()
    __mot[1], __mot[2] = __clamp(speed)
    __mot[3], __mot[4] = __mot[1], __mot[2]
    __drive()

def driveLeft(speed):
    """
        - drives the left motor
        - negative values mean backward
        - keeps rotating until another command is given
    """
    __checkVersion()
    __mot[1], __mot[2] = __clamp(speed)
    __drive()

def driveRight(speed):
    """
        - drives the right motor
        - negative values mean backward
        - keeps rotating until another command is given
    """
    __checkVersion()
    __mot[3], __mot[4] = __clamp(speed)
    __drive()

def getDistance():
    """
        - sends a signal from the ultrasonic sensor (front) and measures the reflection time
        - return value in centimeters
        - return value is an integer between 0 and a maximum of 255
        - return value of 999: no signal received or object is too far away
    """   

    delay(10)

    max_time = 20000
    trig = pin13
    echo = pin14
    
    echo.read_digital() # makes sure echo pin is in input mode

    trig.write_digital(0)
    sleep_us(2)
    trig.write_digital(1)
    sleep_us(10)
    trig.write_digital(0)

    micros = machine.time_pulse_us(echo, 1, max_time)

    if micros < 0: # error
        return 999
    
    t_echo = micros / 1000000
    
    d = int((t_echo/2)*34300-1)
    
    delay(10)

    return d

def setHeadlight(value):  
    """
        - controls both LEDs (red, in front)
        - value: 0 (off) or 1 (on)
        - value is maintained until a new LED command is given
        - equivalent to setLightL(value) and setLightR(value).
    """    
    setHeadlightLeft(value)
    setHeadlightRight(value)

def setHeadlightLeft(value):
    """
        - controls the left LED (red, in front)
        - value: 0 (off) or 1 (on)
        - value is maintained until a new LED command is given
    """  
    __i2cWrite(0x10, bytearray([0x0B, value]))
    delay(1)

def setHeadlightRight(value):
    """
        - controls the right LED (red, in front)
        - value: 0 (off) or 1 (on)
        - value is maintained until a new LED command is given
    """  
    __i2cWrite(0x10, bytearray([0x0C, value]))
    delay(1)

def setDisco(r, g, b): 
    """
        - controls the RGB LEDs on the bottom
        - controls all 4 LEDs simultaneously
        - r, g, b: color values between 0 and 255
    """      
    for id in range(len(np_rgb_pixels)):
        np_rgb_pixels[id] = (int(r),int(g),int(b))
    
    np_rgb_pixels.show()
    delay(1)


def setDiscoFrontLeft(r, g, b):
    """
        - controls RGB LED on the bottom (left, front)
        - r, g, b: color values between 0 and 255
    """      
    np_rgb_pixels[0] = (int(r),int(g),int(b))
    np_rgb_pixels.show()
    delay(1)


def setDiscoBackLeft(r, g, b):   
    """
        - controls RGB LED on the bottom (left, back)
        - r, g, b: color values between 0 and 255
    """      
    np_rgb_pixels[1] = (int(r),int(g),int(b))
    np_rgb_pixels.show()
    delay(1)


def setDiscoFrontRight(r, g, b):    
    """
        - controls RGB LED on the bottom (right, front)
        - r, g, b: color values between 0 and 255
    """   
    np_rgb_pixels[3] = (int(r),int(g),int(b))
    np_rgb_pixels.show()
    delay(1)


def setDiscoBackRight(r, g, b):
    """
        - controls RGB LED on the bottom (right, back)
        - r, g, b: color values between 0 and 255
    """   
    np_rgb_pixels[2] = (int(r),int(g),int(b))
    np_rgb_pixels.show()
    delay(1)


def beep(frequency, duration=0.1):
    """
        - plays a sound on the buzzer
        - frequency: frequency of the sound between 40 and 16'000 Hz
        - higher frequency means higher pitch
        - sound plays for 0.1 seconds
    """
    if frequency < 40:
        return 
    elif frequency > 16000:
        return 
        
    music.pitch(frequency, int(duration*1000), wait=False)
    delay(1)

def alarm():
    """ 
        - plays a short alarm melody
    """  
    _m = music.POWER_UP
    music.play(_m, wait = False, loop = False)    

    for i in range(10):
        setHeadlight(1)
        setDisco(255,0,0)
        delay(100)
        setHeadlight(0)
        setDisco(0,0,0)
        delay(100)

def __getValue(index):
    __i2cWrite(0x10, bytearray([0x1D]))
    buf = __i2cRead(0x10, 11)
    return buf[1+index*2]

def getSensorMiddle():
    """ 
        - returns the middle reflectance sensor value from 0 to 255
        - 0 means no reflection (black); 255 means maximal reflection (white)
    """
    return __getValue(__mapping[0])

def getSensorFrontLeft():
    """ 
        - returns the front-left reflectance sensor value from 0 to 255
        - 0 means no reflection (black); 255 means maximal reflection (white)
    """
    return __getValue(__mapping[1])

def getSensorFrontRight():
    """ 
        - returns the front-right reflectance sensor value from 0 to 255
        - 0 means no reflection (black); 255 means maximal reflection (white)
    """
    return __getValue(__mapping[2])

def getSensorBackLeft():
    """ 
        - returns the back-left reflectance sensor value from 0 to 255
        - 0 means no reflection (black); 255 means maximal reflection (white)
    """
    return __getValue(__mapping[3])

def getSensorBackRight():
    """ 
        - returns the back-right reflectance sensor value from 0 to 255
        - 0 means no reflection (black); 255 means maximal reflection (white)
    """
    return __getValue(__mapping[4])

def setVersion(version):
    """
        (see back of robot to find out which version you have)

        - use 2.0 for white motors
        - and 2.1 for black motors
    """
    global __mapping

    if version == "2.0":
        __mapping = __mappingv20
    elif version == "2.1":
        __mapping = __mappingv21
    else:
        raise ValueError("unknown version")
    
delay = sleep

def __init():
    # same handshake as DFRobot's MakeCode extension
    __i2cWrite(0x10, bytearray([0x49, 1]))
    delay(100)
    for _ in range(50):
        __i2cWrite(0x10, bytearray([0x32]))
        if __i2cRead(0x10, 1)[0] != 0:
            return
        delay(100)
    print(" > Warning. Maqueen did not answer init handshake.")

try:    
    np_rgb_pixels = neopixel.NeoPixel(pin15, 4)
    pin13.write_digital(0) # turn off pin13 (ultrasound) initially
    __init()
    reset()
except Exception as e:
    print(" > micro:bit not connected to Maqueen?")
    print(e)
    exit(1)
