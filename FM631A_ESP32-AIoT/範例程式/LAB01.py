#從 machine 模組匯入 Pin 物件
from machine import Pin
#匯入時間相關的time模組
import time

#建立 5 號腳位的 Pin 物件, 設定為腳位輸出, 命名為 led
led = Pin(5,Pin.OUT)

while True:
    led.value(1)     #熄滅 LED 燈
    time.sleep(0.5)  #暫停 0.5 秒
    led.value(0)     #點亮 LED 燈
    time.sleep(0.5)  #暫停 0.5 秒