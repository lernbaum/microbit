from robot import *

setVersion("2.1")

SPEED=100     
for i in range(4):
    drive(SPEED)
    delay(1000)
    driveRight(SPEED)
    driveLeft(-SPEED)
    delay(550)
    
drive(0)