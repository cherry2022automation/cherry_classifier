import cherry_classfier as cc
import tkinter
import Relay

Relay.R_name = "USBRelay"

cc.solenoid_valve_control.sv_num = 8

class Application_ver2(cc.Application):

    oder_T = 3
    oder_F = 0
    oder_R = 1

    delay = {"":1, "tokushu":1.9, "shu":3, "hanedashi":1}

    view_en = { "original":False,
                "cherry mask":True, "toku mask":False, "shu mask":False, "hane mask":False,
                # "masked cherry":True, "masked toku":True, "masked shu":True, "masked hane":True}
                "masked cherry":False, "masked toku":False, "masked shu":False, "masked hane":False, "flower pattern mask":False}


if __name__ == "__main__":

    root = tkinter.Tk()
    app = Application_ver2(master=root)

    app.mainloop()