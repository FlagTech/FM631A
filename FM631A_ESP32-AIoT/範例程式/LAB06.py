import esp32
import time

while True:
    # 霍爾感測值
    hall = esp32.hall_sensor()
    print(hall)
    # 如果磁鐵距離太遠
    if(hall<100 and hall>0):
        print("收藏盒已開啟")
    time.sleep(0.1)
    
'''
霍爾感測值會根據 ESP32 個體的差異產生誤差,有些 ESP32 的霍爾感測值會在沒有磁鐵的狀況下
維持在 100 ~ 150 上下。如果執行上述程式就會出現問題(磁鐵距離太遠也不會顯示『收藏盒已開啟)

如果您的 ESP32 有遇到此問題, 可以將第 9 行的程式更改為:

    if((hall<250 and hall>0)):
    
調整完就可以正常執行囉！如果此程式有更改, 也請記得更改 LAB07 的第 25 行喔！
'''