from machine import Pin
import time

# 上面按鈕
button_up=Pin(13,Pin.IN,Pin.PULL_UP)   
# 下面按鈕
button_down=Pin(0,Pin.IN,Pin.PULL_UP)    

while True:
    # 讀取上面按鈕的值
    print(button_up.value())
    # 讀取下面按鈕的值
    print(button_down.value())
    print()
    time.sleep(0.1)