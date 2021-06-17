import esp32
import time
import network     # 匯入network模組
import urequests   # 匯入urequests模組

# IFTTT網址
url = 'IFTTT請求網址'

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)
# 更換無線網路名稱、密碼 
sta.connect('無線網路名稱','無線網路密碼')  

while not sta.isconnected():
    pass

print('Wi-Fi連線成功')

while True:
    # 霍爾感測值
    hall = esp32.hall_sensor()
    print(hall)
    # 如果磁鐵距離太遠
    if(hall<100 and hall>0):
        print("發送警訊!!!!")
        res = urequests.get(url)
        if(res.status_code == 200):
            print("傳送成功")
        else:
            print("傳送失敗")
            print("錯誤碼：",res.status_code)
        res.close()
        time.sleep(10)
    time.sleep(0.1)