from machine import Pin, Timer
from time import sleep_ms
import bluetooth

class BLE_UART():
    def __init__(self, name):
        print("等待手機連線中...")
        # 是否連上裝置
        self.conn = False
        # 藍牙名稱
        self.name = name
        # 建立藍牙物件
        self.ble = bluetooth.BLE()
        # 啟動藍牙
        self.ble.active(True)

        self.led = Pin(5, Pin.OUT)
        self.timer1 = Timer(0)
        self.timer2 = Timer(1)
        
        # 目前是未連接的狀態
        self.disconnected()
        # 事件處理
        self.ble.irq(self.ble_irq)
        self.register()
        # 廣播
        self.advertiser()
    # 連線狀態
    def connected(self):
        self.conn = True
        self.timer1.deinit()
        self.timer2.deinit()
    # 沒連線狀態(雖然都是頻率為1來點亮和關閉LED燈, 但點亮和關閉之間差了0.2秒, 所以每次都會差0.2秒)
    def disconnected(self):
        self.conn = False
        # 以頻率1來點亮 LED 燈
        self.timer1.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(0))
        sleep_ms(200)
        # 以頻率1來關閉 LED 燈
        self.timer2.init(period=1000, mode=Timer.PERIODIC, callback=lambda t: self.led(1))   

    def ble_irq(self, event, data):   # event:事件
        #print(event)
        self.event = event
        if event == 1:        # 連接外部裝置
            self.connected()
            self.led(0)
            print("連線到手機或電腦")
            self.advertiser()
        elif event == 2:      # 與外部裝置斷開連線    
            self.advertiser()
            self.disconnected()
            print("中斷連線")
        elif event == 3:      # 收到訊息
            self.new = True   # 收到新訊息
            buffer = self.ble.gatts_read(self.rx)
            self.message = buffer.decode('UTF-8').strip()
            #print('original',self.message)

    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'  # UUID 通用唯一辨識碼
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = bluetooth.UUID(NUS_UUID)
        BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
        BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)
    # 傳送訊息
    def send(self, data):
        # 如果有連上裝置
        if(self.conn == True):
            self.ble.gatts_notify(0, self.tx, data + '\n')
    # 廣播
    def advertiser(self):
        # 藍牙名稱
        name = bytes(self.name, 'UTF-8')
        self.ble.gap_advertise(100, bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)
    # 取得數值
    def get(self):
        try:
            if(self.new == True):
                self.new = False
                return(self.message)
            else:
                return("")
        except:
            return("")