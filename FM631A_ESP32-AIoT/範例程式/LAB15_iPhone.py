from umqtt.robust import MQTTClient # mqtt函式庫
from servo import Servo
from machine import Pin
import math
import network
import time

# 名稱列表
name_list = ["Teddy","Chuan"]

# 建立伺服馬達物件
my_servo = Servo(Pin(22))

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')  
while not sta.isconnected() :
    pass
print('Wi-Fi連線成功')

# MQTT 參數
mqtt_client_id = 'door'                       # 用戶端識別名稱(可以隨意取名)
AIO_URL = 'io.adafruit.com'                   # 主機網址
AIO_USERNAME = '請填入 Adafruit IO 使用者名稱' # 帳戶名稱
AIO_KEY = '請填入 Adafruit IO 金鑰'            # 金鑰

client = MQTTClient(client_id=mqtt_client_id,  # 用戶端識別名稱
                    server=AIO_URL,            # 中介伺服器網址
                    user=AIO_USERNAME,         # 帳戶名稱
                    password=AIO_KEY)          # 金鑰                      
# 連線至 MQTT 伺服器          
client.connect()          
print('MQTT連線成功')

# 從 MQTT 伺服器獲得資料
def get_cmd(topic,msg):
    face = float(msg)
    name_index = int(math.ceil(face))-1
    dis = face-name_index
    if((name_index >= 0) and (dis < 0.4)):
        print(name_list[name_index],dis)
        print("開啟")
        my_servo.write_angle(0)
        time.sleep(3)
        my_servo.write_angle(90)
    else:
        print("我不認識你!!")
    
client.set_callback(get_cmd)

client.subscribe(str.encode(AIO_USERNAME)+b"/feeds/door")

while True:
    # 確定是否有新資料
    client.check_msg()