# =================================================
# Relay.py
# USBリレーライブラリ
#
# 2023/02/17 T19JM042 長谷季樹
#
# 参考：https://jj8xnp.github.io/AmateurRadio/USB_Relay_CW.html
# =================================================

import hid
import time
import threading

# R_name = "USBRelay"     # 「USB-Relay-2」、「USB-Relay-8」とシルク印刷されているタイプ
R_name = "HIDRelay"     # 「USB Relay QYF-UR02」とシルク印刷されているタイプ

class Relay():

    USBRelay_ID = {"vendor":0x16c0, "product":0x05df}
    HIDRelay_ID = {"vendor":0x519, "product":0x2018}
    ID = {"USBRelay":USBRelay_ID, "HIDRelay":HIDRelay_ID}

    h = None
    R_name = None

    def __init__(self, R_name="USBRelay"):

        self.R_name = R_name

        # 初期化
        self.h = hid.device()
        self.h.open(self.ID[R_name]["vendor"], self.ID[R_name]["product"])

    def send_command(self, ch, on_off):

        ch = int(ch)
        send_data = [0] * 9

        if self.R_name == "USBRelay":
            if on_off == "on":
                send_data[1] = 0xff
            elif on_off == "off":
                send_data[1] = 0xfd
            else:
                return
            send_data[2] = ch
            self.h.send_feature_report(send_data)

        if self.R_name == "HIDRelay":
            if on_off == "on":
                send_data[1] = 0xf0 + ch
            elif on_off == "off":
                send_data[1] = 0x00 + ch
            else:
                return
            self.h.write(send_data)

def send_command_saferry(ch, on_off):
    while 1:
            try:
                relay = Relay(R_name=R_name)
                relay.send_command(ch, on_off)
                break   # 正常に送信完了
            except:     # エラー発生 もう一度送信
                print("error & retry [" + str(ch) + " " + on_off + "]")

def on(ch):
    send_command_saferry(ch, "on")

def off(ch):
    send_command_saferry(ch, "off")

def pulse(ch, on_time_s):
    send_command_saferry(ch, "on")
    time.sleep(on_time_s)
    send_command_saferry(ch, "off")

# 別スレッドを生成して1パルス
def pulse_with_thread(ch, on_times_s):
    th_pulse = threading.Thread(target=pulse, args=(ch, on_times_s, ))
    th_pulse.start()

if __name__ == "__main__":

    # 命令送信
    while 1:
        ch = input("channel (1 ~ 8) : ")
        on_off = input("Relay (on or off) : ")
        send_command_saferry(ch, on_off)