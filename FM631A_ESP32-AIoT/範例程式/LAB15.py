from ble_uart import BLE_UART
from servo import Servo
from machine import Pin
import time

# 名稱列表
name_list = ["Teddy","Chuan"]

# 建立伺服馬達物件
my_servo = Servo(Pin(22))
# 建立藍牙物件
ble = BLE_UART("藍牙門鎖")

while True:
    # 取得藍牙傳送過來的值
    getValue = ble.get()
    if(getValue != ""):
        # 使用:切割字串
        get_split = getValue.split(":")
        # 名稱
        name = get_split[0]
        # 距離
        dis = float(get_split[1])
        print(name,dis)
        # 如果名稱有在name_list 且 距離小於0.4
        if((name in name_list) and (dis<0.4)):
            print("開啟")
            my_servo.write_angle(0)
            time.sleep(3)
            my_servo.write_angle(90)
        else:
            print("我不認識你!!")