from machine import Pin,ADC
import time
import network     
import urequests
import gc

adc_pin=Pin(32)            
adc = ADC(adc_pin)         # 建立ADC物件
adc.width(ADC.WIDTH_12BIT) # 設定ADC範圍
adc.atten(ADC.ATTN_11DB)   # 將最大感測電壓設定成3.6V

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')

while not sta.isconnected() :
    pass

print('Wi-Fi連線成功')

device_label = "ESP32"           # 裝置名稱
variable_label = "temperature"   # 變數名稱
token = "Ubidots金鑰"

url = "https://things.ubidots.com/api/v1.6/devices/"+ device_label

while True:
    gc.collect()
    vol = (adc.read()/4095)*3.6
    tem = (vol-0.5)*100
    print('目前溫度:',tem)
    data = {variable_label:tem}
    headers = {"X-Auth-Token":token}
    res = urequests.post(url,json = data,headers = headers)
    if(res.status_code == 200):
        print("傳送成功")
    else:
        print("傳送失敗")
        print("錯誤碼：",res.status_code)
    res.close()
    time.sleep(5)