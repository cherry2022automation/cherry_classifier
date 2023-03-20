# ================================================
# Cherry Classifier_ver2.py
# ================================================
# Cherry Classifier2号機 操作用プログラム
# ------------------------------------------------

import cherry_classfier as cc
import tkinter
import Relay
import datetime

Relay.R_name = "USBRelay"

cc.solenoid_valve_control.sv_num = 8

class Application_ver2(cc.Application):

    oder_T = 3
    oder_F = 0
    oder_R = 1

    # 電磁弁タスクスケジュールリスト
    sche_M = []
    sche_L = []
    sche_LL = []
    sche_error = []
    schedule = {"":sche_error, "M":sche_M, "L":sche_L, "LL":sche_LL}
    sv_num = {"":0, "M":1, "L":3, "LL":5}
    delay = {"":1, "M":1.9, "L":4, "LL":6}

    view_en = { "original":False,
                "cherry mask":False, "toku mask":False, "shu mask":False, "hane mask":False,
                # "masked cherry":True, "masked toku":True, "masked shu":True, "masked hane":True}
                "masked cherry":False, "masked toku":False, "masked shu":False, "masked hane":False, "flower pattern mask":False}

    def scheduling(self, info):
        # スケジューリング
        self.schedule[info["size"]].append(datetime.datetime.now()+datetime.timedelta(seconds=self.delay[info["size"]]))

if __name__ == "__main__":

    root = tkinter.Tk()
    app = Application_ver2(master=root)

    app.mainloop()