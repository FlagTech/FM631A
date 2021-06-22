from machine import Pin
import time
from ble_hid import BLE_HID

mult = BLE_HID("ESP32_Multimedia")

# 上面按鈕
button_up=Pin(13,Pin.IN,Pin.PULL_UP)   
# 下面按鈕
button_down=Pin(0,Pin.IN,Pin.PULL_UP) 

while True:
    # 按下 上按鈕
    staUp = button_up.value()
    if(staUp == 0):
        mult.volumeIncrement()
        print("音量增強")
    # 按下 下按鈕    
    staDown = button_down.value()
    if(staDown == 0):
        mult.volumeDecrement()
        print("音量減弱")
    time.sleep(0.15)