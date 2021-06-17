from servo import Servo
import network
import ESPWebServer
from machine import Pin

def handleCmd(socket, args):         
    if 'status' in args:
        print(args['status'])
        if args['status'] == 'open':
            my_servo.write_angle(0)
        elif args['status'] == 'close':
            my_servo.write_angle(90)            
        ESPWebServer.ok(socket, "200", "OK")   
    else:
        ESPWebServer.err(socket, "400", "ERR")   

# 建立伺服馬達物件
my_servo = Servo(Pin(22))

sta = network.WLAN(network.STA_IF)
sta.active(True)   
sta.connect('無線網路名稱','無線網路密碼')   
while(not sta.isconnected()):
    pass

print('Wi-Fi連線成功')               

ESPWebServer.begin(80)                      
ESPWebServer.onPath("/Door",handleCmd)      
print("伺服器位址：" + sta.ifconfig()[0])        

while True:
    ESPWebServer.handleClient()                         
