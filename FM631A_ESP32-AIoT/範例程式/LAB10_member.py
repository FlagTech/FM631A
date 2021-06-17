import flag_utils
from machine import Pin,PWM
import network     
import urequests  
import time
import tm1637
import ntptime

# APP ID
app_ID = '"1c0a99d7fb1b4001ac1685acabb10e00"'
# APP Key
app_KEY = "x6jAQAhLhknObLZPJuk9Dd1047w"

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

# 取得電子簽章
gmt_time = time.localtime(
    ntptime.time()   
)
x_date = flag_utils.to_x_date(gmt_time)
dig = flag_utils.HMAC_sha1(
    str.encode(app_KEY),
    x_date
)
signature = flag_utils.b64encode(dig.digest()).decode()

ifttt_url = "IFTTT請求網址"

# 讓網站認為請求是使用瀏覽器發出。因為有些網頁會擋爬蟲程式
headers = {
    'user-agent':'curl/7.76.1',
    'Accept': 'application/json',
    'Authorization':'hmac username={}, algorithm="hmac-sha1", headers="x-date", signature="{}"'.format(app_ID,signature),
    'x-date': x_date.decode()[7:]
}

# 查詢指定火車起點與終點
train_url = "https://ptx.transportdata.tw/MOTC/v2/Rail/TRA/GeneralTrainInfo/TrainNo/" \
            + str(s_number) +"?$format=JSON"
train_res = urequests.get(train_url,headers=headers)
if(train_res.status_code == 200):
    pass
else:
    print("傳送失敗")
    print("錯誤碼：",train_res.status_code)
train_j = train_res.json()
print("\n車號:",s_number)
print(train_j[0]['StartingStationName']['Zh_tw'] \
      +" → "+train_j[0]['EndingStationName']['Zh_tw'])
train_res.close()
# 車子第一次出現在時刻表時要提醒使用者
remind = False  

# 查詢火車時刻表
time_url = "https://ptx.transportdata.tw/MOTC/v2/Rail/TRA/LiveBoard/Station/" \
            + str(sta_number)+"?$top=20&$format=JSON"

while True:
    time_res = urequests.get(time_url,headers=headers)
    if(time_res.status_code == 200):
        pass
    else:
        print("傳送失敗")
        print("錯誤碼：",time_res.status_code)    
    time_j = time_res.json()
    time_res.close()
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