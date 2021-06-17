from machine import Pin,ADC
import time

# 溫度感測器
adc_pin=Pin(32)             
adc = ADC(adc_pin)           # 建立 ADC 物件
adc.width(ADC.WIDTH_12BIT)   # 設定 ADC 解析度。12BIT代表範圍是0~4095
adc.atten(ADC.ATTN_11DB)     # 將最大感測電壓設定成3.6V, 超過3.6V時會得到ADC最大值511

while True:
    vol = (adc.read()/4095)*3.6
    tem = (vol-0.5)*100
    print("目前溫度:",tem)        # 顯示溫度值
    time.sleep(1)