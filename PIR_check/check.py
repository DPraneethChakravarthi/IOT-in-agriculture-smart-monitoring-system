from gpiozero import buzzer
from gpiozero import MotionSensor

green_led = buzzer(17)
pir = MotionSensor(4)
green_led.off()

while True:
    pir.wait_for_active()
    print("Motion Detected")
    green_led.on()
    pir.wait_for_inactive()
    print("Motion Stopped")