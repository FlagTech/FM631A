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