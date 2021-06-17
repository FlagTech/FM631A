from ble_uart import BLE_UART
from servo import Servo
from machine import Pin

# 建立伺服馬達物件
my_servo = Servo(Pin(22))
# 建立藍牙物件
ble = BLE_UART("door_lock")

while True:
    getValue = ble.get()
    # 將取得的英文字母都更改為小寫
    getValue = getValue.lower()
    if(getValue == "open"):  
        # 轉至 0 度
        my_servo.write_angle(0)
        print("開啟")
    if(getValue == "close"):
        # 轉至 90 度
        my_servo.write_angle(90)
        print("關閉")