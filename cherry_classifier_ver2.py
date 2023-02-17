import cherry_classfier as cc
import tkinter
import Relay
import solenoid_valve

Relay.R_name = "USBRelay"

cc.solenoid_valve_control.sv_num = 8

class Application_ver2(cc.Application):

    oder_T = 3
    oder_F = 0
    oder_R = 1

    delay = {"tokushu":1.9, "shu":3}

if __name__ == "__main__":

    root = tkinter.Tk()
    app = Application_ver2(master=root)

    app.mainloop()