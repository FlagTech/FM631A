from micropython import const
import struct
import bluetooth

class BLE_HID:
    def __init__(self, name):
        print("等待裝置連線中...")
        self.ble = bluetooth.BLE()
        self.ble.active(1)
        self.ble.irq(self.ble_irq)
        self.name = name
        self.con = False
        
        UUID = bluetooth.UUID

        F_READ = bluetooth.FLAG_READ
        F_WRITE = bluetooth.FLAG_WRITE
        F_READ_WRITE = bluetooth.FLAG_READ | bluetooth.FLAG_WRITE
        F_READ_NOTIFY = bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY
        F_READ_WRITE_NORESPONSE = bluetooth.FLAG_READ | bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE
        
        ATT_F_READ = 0x01
        ATT_F_WRITE = 0x02
        ATT_F_READ_WRITE = ATT_F_READ | ATT_F_WRITE
        
        # 建立伺服器
        hid_service = (
            UUID(0x1812),  # Human Interface Device            人機介面設備
            (
                (UUID(0x2A4A), F_READ),  # HID information     HID信息
                (UUID(0x2A4B), F_READ),  # HID report map      HID報告圖
                (UUID(0x2A4C), F_WRITE),  # HID control point  HID控制點
                (UUID(0x2A4D), F_READ_NOTIFY, ((UUID(0x2908), ATT_F_READ),(UUID(0x2902), ATT_F_READ),)),  # HID report / reference
                (UUID(0x2A4D), F_READ_WRITE_NORESPONSE, ((UUID(0x2908), ATT_F_READ),)),  # HID report / reference
                (UUID(0x2A4D), F_READ_NOTIFY, ((UUID(0x2908), ATT_F_READ),)),  # HID report / reference
                (UUID(0x2A4E), F_READ_WRITE),  # HID protocol mode
            ),
        )
            # fmt: off

        HID_REPORT_MAP = bytes([
            # 鍵盤
            0x05, 0x01,     # Usage Page (Generic Desktop) 通用桌面控制類型
            0x09, 0x06,     # Usage (Keyboard)             鍵盤
            0xA1, 0x01,     # Collection (Application)     集合(應用)
            0x85, 0x01,     #     Report ID (1)            報告編號 (1)
            0x75, 0x01,     #     Report Size (1)          單位數據大小 (1)
            0x95, 0x08,     #     Report Count (8)         數據量:8
            0x05, 0x07,     #     Usage Page (Key Codes)   用途類型:鍵盤 (修飾鍵)
            0x19, 0xE0,     #     Usage Minimum (224)      內容最小值:0xE0
            0x29, 0xE7,     #     Usage Maximum (231)      內容最小值:0xE7
            0x15, 0x00,     #     Logical Minimum (0)      狀態最小值:0 (放開)
            0x25, 0x01,     #     Logical Maximum (1)      狀態最大值:1 (按下)
            0x81, 0x02,     #     Input (Data, Variable, Absolute); Modifier byte
            0x95, 0x01,     #     Report Count (1)         數據量:1
            0x75, 0x08,     #     Report Size (8)          單位數據大小 (8)
            0x81, 0x01,     #     Input (Constant); Reserved byte
            0x95, 0x05,     #     Report Count (5)         數據量:5
            0x75, 0x01,     #     Report Size (1)          單位數據大小 (1)
            0x05, 0x08,     #     Usage Page (LEDs)        用途類型:LED指示燈
            0x19, 0x01,     #     Usage Minimum (1)        內容最小值:0x01,代表數字鎖定
            0x29, 0x05,     #     Usage Maximum (5)        內容最大值:0x05,代表日文假名切換
            0x91, 0x02,     #     Output (Data, Variable, Absolute); LED report  輸出，絕對值
            0x95, 0x01,     #     Report Count (1)         數據量:1
            0x75, 0x03,     #     Report Size (3)          單位數據大小 (3)
            0x91, 0x01,     #     Output (Constant); LED report padding
            0x95, 0x06,     #     Report Count (6)
            0x75, 0x08,     #     Report Size (8)
            0x15, 0x00,     #     Logical Minimum (0)
            0x25, 0x65,     #     Logical Maximum (101)
            0x05, 0x07,     #     Usage Page (Key Codes)   用途類型:鍵盤
            0x19, 0x00,     #     Usage Minimum (0)
            0x29, 0x65,     #     Usage Maximum (101)
            0x81, 0x00,     #     Input (Data, Array); Key array (6 bytes)
            0xC0,           # End Collection
            # 多媒體鍵
            0x05, 0x0C,     
            0x09, 0x01,     
            0xA1, 0x01,     
            0x85, 0x02,     
            0x75, 0x10,     
            0x95, 0x01,     
            0x15, 0x01,     
            0x26,
            0x8C, 0x02,     
            0x19, 0x01,     
            0x2A,
            0x8C, 0x02,
            0x81, 0x00,     
            0xC0,
        ])
        
        # register services  註冊服務
        self.ble.config(gap_name=name)
        handles = self.ble.gatts_register_services((hid_service,))
        #print(handles)
        h_info, h_hid, _, self.h_rep, h_d1, _, _, h_d2, self.h_com, h_d3, h_proto = handles[0]
        #print(self.HID_REPORT_MAP)
        # set initial data  設定初始資料
        self.ble.gatts_write(h_info, b"\x01\x01\x00\x02")  # HID info: ver=1.1, country=0, flags=normal
        self.ble.gatts_write(h_hid, HID_REPORT_MAP)  # HID report map
        self.ble.gatts_write(h_d1, struct.pack("<BB", 1, 1))  # report: id=1, type=input
        self.ble.gatts_write(h_d2, struct.pack("<BB", 1, 2))  # report: id=1, type=output
        self.ble.gatts_write(h_d3, struct.pack("<BB", 2, 1))  # report: id=1, type=output
        self.ble.gatts_write(h_proto, b"\x01")  # protocol mode: report

        # advertise 廣告
        adv = (
            b"\x02\x01\x06"
            b"\x03\x03\x12\x18"  # complete list of 16-bit service UUIDs: 0x1812
            b"\x03\x19\xc1\x03"  # appearance: keyboard
            +bytes((len(name)+1,9,))+ str.encode(name)
        )
        conn_handle = None
        self.ble.gap_advertise(100_000, adv)

    def ble_irq(self,event, data):
        #print(event)
        #print("event:", event, data)
        global conn_handle
        if event == 1:
            self.con = True
            print("連線到手機或電腦")
            conn_handle = data[0]       
        else:
            #print("event:", event, data)
            if event == 2:
                self.con = False
                print("中斷連線\n")
                self.__init__(self.name)
    
    # 傳送字元
    def send_char(self,char):
        if char == " ":
            mod = 0
            code = 0x2C
        elif ord("a") <= ord(char) <= ord("z"):
            mod = 0
            code = 0x04 + ord(char) - ord("a")
        elif ord("A") <= ord(char) <= ord("Z"):
            mod = 2
            code = 0x04 + ord(char) - ord("A")
        else:
            assert 0
        if(self.con == True):
            self.ble.gatts_notify(conn_handle, self.h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
            self.ble.gatts_notify(conn_handle, self.h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
    # 傳送字串
    def send_str(self,st):
        if(self.con == True):
            for c in st:
                self.send_char(c)
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")

    # 可以查看以下對照表
    # https://circuitpython.readthedocs.io/projects/hid/en/latest/_modules/adafruit_hid/keycode.html
    # https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
    
    # 自訂按鈕
    def customized(self,mod,code):
        if(self.con == True):
            self.ble.gatts_notify(conn_handle, self.h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
            self.ble.gatts_notify(conn_handle, self.h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
           
    # 手機切換語言(Shift + Space)
    def changeLanguage(self):
        if(self.con == True):
            mod = 0x02    # shift
            code = 0x2C   # 空白鍵
            self.ble.gatts_notify(conn_handle, self.h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
            self.ble.gatts_notify(conn_handle, self.h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
    # 截圖
    def screenShot(self):   # 0x28:ENTER    0x46:Print Scrn
        if(self.con == True):
            mod = 0
            code = 0x46
            self.ble.gatts_notify(conn_handle, self.h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
            self.ble.gatts_notify(conn_handle, self.h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
    # 照相：按下ENTER    
    def photograph(self):   # 0x28:ENTER    0x46:Print Scrn
        if(self.con == True):
            mod = 0
            code = 0x28
            self.ble.gatts_notify(conn_handle, self.h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
            self.ble.gatts_notify(conn_handle, self.h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
    # 音量增強
    def volumeIncrement(self):
        if(self.con == True):
            self.ble.gatts_notify(conn_handle, self.h_com, b"\xE9\x00")
            self.ble.gatts_notify(conn_handle, self.h_com, b"\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
    # 音量減弱
    def volumeDecrement(self):   
        if(self.con == True):
            self.ble.gatts_notify(conn_handle, self.h_com, b"\xEA\x00")
            self.ble.gatts_notify(conn_handle, self.h_com, b"\x00\x00")
        elif(self.con == False):
            print("ESP32 尚未與其它裝置連線")
