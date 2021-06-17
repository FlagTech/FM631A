from machine import Pin
import time
from ble_hid import BLE_HID

keyboard = BLE_HID("ESP32_keyboard")

last_staUp = 1     # 是否按下按鈕

# 上面按鈕
button_up=Pin(13,Pin.IN,Pin.PULL_UP)   

while True:
    # 讀取按鈕值
    staUp = button_up.value()
    # 前一次沒按 且 這次有按
    if(last_staUp == 1 and staUp == 0):
        keyboard.screenShot()
        print("截圖")
    # 紀錄前一次狀態
    last_staUp = staUp
    time.sleep(0.05)