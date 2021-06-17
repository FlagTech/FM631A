from machine import Pin,PWM
import time

# 建立 PWM 物件
buzzer = PWM(Pin(23,Pin.OUT),freq=0, duty=512)

buzzer.freq(349)   # 發出 Fa 聲
time.sleep(1)
buzzer.freq(294)   # 發出 Re 聲
time.sleep(1)

buzzer.deinit()