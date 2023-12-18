# 手冊上使用的 PTX 服務已經在 2022 年結束，所以改用 TDX 服務
# 相關說明請參考本書線上服務專區教學文件：
# https://www.flag.com.tw/bk/t/FM631A

from machine import Pin,PWM
import network     
import urequests  
import time
import tm1637
import ntptime
from tdx import TDX

client_id = '你的 Client Id'
client_secret = '你的 Client Secret'

# 想查詢的車號
s_number = 4171
# 想查詢的車站(1000是台北)
# 可以使用以下網址查詢
# https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip111/view
sta_number = 1000

# 四位數顯示器
tm = tm1637.TM1637(clk=Pin(16), dio=Pin(17))
# 清空四位數顯示器
tm.write([0, 0, 0, 0])

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')
while not sta.isconnected() :
    pass

print('Wi-Fi連線成功')

# 建立 TDX API 存取物件
tdx = TDX(client_id, client_secret)

ifttt_url = "IFTTT請求網址"

# 查詢指定火車起點與終點
train_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/GeneralTrainInfo/TrainNo/" \
            + str(s_number) +"?$format=JSON"
train_j = tdx.get_json(train_url)
if('error_code' in train_j):
    print("傳送失敗")
    print("錯誤碼：",train_j['error_code'])
print("\n車號:",s_number)
print(train_j[0]['StartingStationName']['Zh_tw'] \
      +" → "+train_j[0]['EndingStationName']['Zh_tw'])
# 車子第一次出現在時刻表時要提醒使用者
remind = False  

# 查詢火車時刻表
time_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/" \
            + str(sta_number)+"?$top=20&$format=JSON"

while True:
    time_j = tdx.get_json(time_url)
    if('error_code' in time_j):
        print("傳送失敗")
        print("錯誤碼：",time_j['error_code'])    
    # 將車號加入 number列表 中
    number = []
    for i in range(len(time_j)):
        number.append(time_j[i]['TrainNo'])    
    print("\n即時班車號碼：",number)

    # 有查到對應車號, 顯示延遲時間
    if(str(s_number) in number):
        if(remind == False):
            # 蜂鳴器
            buzzer = PWM(Pin(23,Pin.OUT),freq=0, duty=512)
            buzzer.freq(349)
            time.sleep(1)
            buzzer.freq(294)
            time.sleep(1)
            buzzer.deinit()
            remind = True
        ind = number.index(str(s_number))
        print("\n表定發車時間:",time_j[ind]['ScheduledArrivalTime'])
        print("延遲時間:",time_j[ind]['DelayTime'],"分鐘")
        tm.number(time_j[ind]['DelayTime'])
        res = urequests.get(ifttt_url + "?value1=" + str(time_j[ind]['DelayTime']))
        if(res.status_code == 200):
            pass
        else:
            print("傳送失敗")
            print("錯誤碼：",res.status_code)
        res.close()
    # 沒有查到對應車號
    else:
        print("\n目前無"+str(s_number)+"號火車")
        TW_sec = time.mktime(time.localtime())+28800
        TW = time.localtime(TW_sec)
        hour = TW[3]
        minu = TW[4]
        tm.numbers(hour,minu)
        remind = False
    time.sleep(300)  # 暫停 300 秒