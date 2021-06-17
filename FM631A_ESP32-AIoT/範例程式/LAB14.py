from umqtt.robust import MQTTClient 
from machine import Pin,PWM
import network
import time

# 連線至無線網路
sta=network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')  
while not sta.isconnected() :
    pass
print('Wi-Fi連線成功')

# mqtt參數
mqtt_client_id = 'age'             # 用戶端識別名稱(可以隨意取名)
AIO_URL = 'io.adafruit.com'        # 主機網址
AIO_USERNAME = '請填入 Adafruit IO 使用者名稱'  # 帳戶名稱
AIO_KEY = '請填入 Adafruit IO 金鑰'             # 金鑰
    
client = MQTTClient(client_id=mqtt_client_id,  # 用戶端識別名稱
                    server=AIO_URL,            # 中介伺服器網址
                    user=AIO_USERNAME,         # 帳戶名稱
                    password=AIO_KEY)          # 金鑰
# 連線至mqtt伺服器          
client.connect()           
print('MQTT連線成功')
# 年齡限制
age_limit = 10 

# 從 MQTT 伺服器獲得資料
def get_cmd(topic,msg):
    age = int(msg)
    print(age)
    if(age>=age_limit):
        print("超過年齡限制")
        # 建立 PWM 物件
        buzzer = PWM(Pin(23,Pin.OUT),freq=0, duty=512)
        buzzer.freq(494)   # 發出 Ti 聲
        time.sleep(1)
        buzzer.deinit()
        
client.set_callback(get_cmd)

client.subscribe(str.encode(AIO_USERNAME)+b"/feeds/age")

while True:
    # 確定是否有新資料
    client.check_msg()
