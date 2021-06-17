import tm1637
from machine import Pin
import ntptime
import time
import network 

# 四位數顯示器
tm = tm1637.TM1637(clk=Pin(16), dio=Pin(17))

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')
while not sta.isconnected() :
    pass
print('Wi-Fi連線成功')

# 將 RTC 設定成世界協調時間(UTC)
ntptime.settime()
# UTC 時間加上28800秒(8小時)才會等於台灣時間
TW_sec = time.mktime(time.localtime())+28800

while True:
    TW = time.localtime(TW_sec)
    print(TW)
    hour = TW[3]   # 時
    minu = TW[4]   # 分
    tm.numbers(hour,minu)
    time.sleep(1)
    TW_sec += 1