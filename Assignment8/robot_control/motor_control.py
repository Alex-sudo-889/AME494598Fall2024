# motor_control.py

import RPi.GPIO as GPIO

# Define GPIO pins
NSLEEP1 = 12
AN11 = 17
AN12 = 27
BN11 = 22
BN12 = 23
NSLEEP2 = 13
AN21 = 24
AN22 = 25
BN21 = 26
BN22 = 16
temp1 = 1  # State variable to toggle run state

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(NSLEEP1, GPIO.OUT)
GPIO.setup(NSLEEP2, GPIO.OUT)
GPIO.setup(AN11, GPIO.OUT)
GPIO.setup(AN12, GPIO.OUT)
GPIO.setup(BN11, GPIO.OUT)
GPIO.setup(BN12, GPIO.OUT)
GPIO.setup(AN21, GPIO.OUT)
GPIO.setup(AN22, GPIO.OUT)
GPIO.setup(BN21, GPIO.OUT)
GPIO.setup(BN22, GPIO.OUT)

# Initialize PWM for speed control
p1 = GPIO.PWM(NSLEEP1, 1000)  # PWM frequency: 1kHz
p2 = GPIO.PWM(NSLEEP2, 1000)
p1.start(75)  # Start PWM with 75% duty cycle (high speed)
p2.start(75)

def run():
    global temp1
    print("run")
    if temp1 == 1:
        # Set GPIO for backward
        GPIO.output(AN11, GPIO.HIGH)
        GPIO.output(AN12, GPIO.LOW)
        GPIO.output(BN11, GPIO.HIGH)
        GPIO.output(BN12, GPIO.LOW)
        GPIO.output(AN21, GPIO.HIGH)
        GPIO.output(AN22, GPIO.LOW)
        GPIO.output(BN21, GPIO.HIGH)
        GPIO.output(BN22, GPIO.LOW)
        print("backward")
        temp1 = 0
    else:
        # Set GPIO for forward
        GPIO.output(AN11, GPIO.LOW)
        GPIO.output(AN12, GPIO.HIGH)
        GPIO.output(BN11, GPIO.LOW)
        GPIO.output(BN12, GPIO.HIGH)
        GPIO.output(AN21, GPIO.LOW)
        GPIO.output(AN22, GPIO.HIGH)
        GPIO.output(BN21, GPIO.LOW)
        GPIO.output(BN22, GPIO.HIGH)
        print("forward")
        temp1 = 1

def stop():
    print("stop")
    GPIO.output(AN11, GPIO.LOW)
    GPIO.output(AN12, GPIO.LOW)
    GPIO.output(BN11, GPIO.LOW)
    GPIO.output(BN12, GPIO.LOW)
    GPIO.output(AN21, GPIO.LOW)
    GPIO.output(AN22, GPIO.LOW)
    GPIO.output(BN21, GPIO.LOW)
    GPIO.output(BN22, GPIO.LOW)
    # Optionally set PWM duty cycle to 0
    p1.ChangeDutyCycle(0)
    p2.ChangeDutyCycle(0)

def forward():
    global temp1
    print("forward")
    GPIO.output(AN11, GPIO.LOW)
    GPIO.output(AN12, GPIO.HIGH)
    GPIO.output(BN11, GPIO.LOW)
    GPIO.output(BN12, GPIO.HIGH)
    GPIO.output(AN21, GPIO.LOW)
    GPIO.output(AN22, GPIO.HIGH)
    GPIO.output(BN21, GPIO.LOW)
    GPIO.output(BN22, GPIO.HIGH)
    temp1 = 0
    # Ensure speed is high
    p1.ChangeDutyCycle(75)
    p2.ChangeDutyCycle(75)

def backward():
    global temp1
    print("backward")
    GPIO.output(AN11, GPIO.HIGH)
    GPIO.output(AN12, GPIO.LOW)
    GPIO.output(BN11, GPIO.HIGH)
    GPIO.output(BN12, GPIO.LOW)
    GPIO.output(AN21, GPIO.HIGH)
    GPIO.output(AN22, GPIO.LOW)
    GPIO.output(BN21, GPIO.HIGH)
    GPIO.output(BN22, GPIO.LOW)
    temp1 = 1
    # Ensure speed is high
    p1.ChangeDutyCycle(75)
    p2.ChangeDutyCycle(75)

def leftrotation():
    global temp1
    print("leftrotation")
    GPIO.output(AN11, GPIO.HIGH)
    GPIO.output(AN12, GPIO.LOW)
    GPIO.output(BN11, GPIO.LOW)
    GPIO.output(BN12, GPIO.HIGH)
    GPIO.output(AN21, GPIO.HIGH)
    GPIO.output(AN22, GPIO.LOW)
    GPIO.output(BN21, GPIO.LOW)
    GPIO.output(BN22, GPIO.HIGH)
    temp1 = 0
    # Ensure speed is high
    p1.ChangeDutyCycle(75)
    p2.ChangeDutyCycle(75)

def rightrotation():
    global temp1
    print("rightrotation")
    GPIO.output(AN11, GPIO.LOW)
    GPIO.output(AN12, GPIO.HIGH)
    GPIO.output(BN11, GPIO.HIGH)
    GPIO.output(BN12, GPIO.LOW)
    GPIO.output(AN21, GPIO.LOW)
    GPIO.output(AN22, GPIO.HIGH)
    GPIO.output(BN21, GPIO.HIGH)
    GPIO.output(BN22, GPIO.LOW)
    temp1 = 0
    # Ensure speed is high
    p1.ChangeDutyCycle(75)
    p2.ChangeDutyCycle(75)

def set_speed_low():
    print("low speed")
    p1.ChangeDutyCycle(25)
    p2.ChangeDutyCycle(25)

def set_speed_medium():
    print("medium speed")
    p1.ChangeDutyCycle(50)
    p2.ChangeDutyCycle(50)

def set_speed_high():
    print("high speed")
    p1.ChangeDutyCycle(75)
    p2.ChangeDutyCycle(75)

def cleanup():
    print("GPIO cleanup")
    p1.stop()
    p2.stop()
    GPIO.cleanup()
