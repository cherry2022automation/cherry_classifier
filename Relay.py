# =================================================
# Relay.py
# USBリレーライブラリ
#
# 2022/10/13 T19JM042 長谷季樹
# =================================================

import hid
import time
import threading

class Relay():

    vendor_ID = 0x16c0
    product_ID = 0x05df
    command_on = 0xff
    command_off = 0xfd
    h = None

    def __init__(self):

        # 初期化
        self.h = hid.device()
        self.h.open(self.vendor_ID, self.product_ID)

    def send_command(self, ch, on_off):

        ch = int(ch)

        if on_off == "on":
            command = self.command_on
        elif on_off == "off":
            command = self.command_off
        else:
            return

        send_data = [0] * 9
        send_data[1] = command
        send_data[2] = ch
        self.h.send_feature_report(send_data)

def send_command_saferry(ch, on_off):
    while 1:
            try:
                relay = Relay()
                relay.send_command(ch, on_off)
                break
            except:
                print("error & retry [" + ch + " " + on_off + "]")

def on(ch):
    send_command_saferry(ch, "on")

def off(ch):
    send_command_saferry(ch, "off")

def pulse(ch, on_time_s):

    send_command_saferry(ch, "on")
    time.sleep(on_time_s)
    send_command_saferry(ch, "off")

def pulse_with_thread(ch, on_times_s):
    th_pulse = threading.Thread(target=pulse, args=(ch, on_times_s, ))
    th_pulse.start()

if __name__ == "__main__":

    # 命令送信
    while 1:
        ch = input("channel (1 ~ 8) : ")
        on_off = input("Relay (on or off) : ")
        send_command_saferry(ch, on_off)