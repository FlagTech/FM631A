from servo import Servo
from machine import Pin
import time

# 建立伺服馬達物件
my_servo = Servo(Pin(22))

# 轉至 0 度
my_servo.write_angle(0)
time.sleep(1)
# 轉至 90 度
my_servo.write_angle(90)
time.sleep(1)