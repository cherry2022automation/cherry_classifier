import cherry_classfier as cc
import tkinter
import Relay

Relay.R_name = "USBRelay"

class Application_ver2(cc.Application):

    oder_T = 3
    oder_F = 0
    oder_R = 1

if __name__ == "__main__":

    root = tkinter.Tk()
    app = Application_ver2(master=root)

    app.mainloop()