import time
import motor_control
import RPi.GPIO as GPIO

try:
    print("Moving motor forward")
    motor_control.move_motor_forward()
    time.sleep(2)  # Run for 2 seconds

    print("Stopping motor")
    motor_control.stop_motor()
    time.sleep(1)

    print("Moving motor backward")
    motor_control.move_motor_backward()
    time.sleep(2)

    print("Stopping motor")
    motor_control.stop_motor()

except KeyboardInterrupt:
    print("Test interrupted by user")

finally:
    motor_control.stop_motor()
    GPIO.cleanup()
    print("GPIO cleanup done")
