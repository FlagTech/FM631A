from machine import Pin
import time
from ble_hid import BLE_HID

keyboard = BLE_HID("ESP32_keyboard")

sta_up = False     # 是否按下按鈕
sta_down = False   # 是否按下按鈕

# 上面按鈕
button_up=Pin(13,Pin.IN,Pin.PULL_UP)   
# 下面按鈕
button_down=Pin(0,Pin.IN,Pin.PULL_UP)

while True:
    # 傳送文字
    bu = button_up.value()
    if bu == 1:
        sta_up = False
    if(bu == 0 and sta_up == False):
        keyboard.send_char("a")
        print("傳送文字")
        sta_up = True
    # 切換語言    
    bd = button_down.value()    
    if bd == 1:
        sta_down = False
    if(bd == 0 and sta_down == False):
        keyboard.changeLanguage()
        print("切換語言")
        sta_down = True   
    time.sleep(0.05)

