from csv import reader
import sys
from tkinter import messagebox, ttk
from tkinter import *
import Relay

from pyparsing import col

class solenoid_valve_control(Frame):

    def __init__(self, master=None):

        # ウィンドウ初期化
        super().__init__(master)
        self.master = master
        self.master.title('電磁弁操作')
        self.pack()

        font_size = 20

        self.label1 = ttk.Label(self, text="on time", padding=(5,2))
        self.label1.grid(row=0, column=1, sticky=E)

        self.on_time_ms = StringVar()
        self.time_entry = ttk.Entry(self, textvariable=self.on_time_ms, width = 10, justify=RIGHT)
        self.time_entry.insert(0, "30")
        self.time_entry.grid(row=0, column=2)

        self.label2 = ttk.Label(self, text="[ms]", padding=(5,2))
        self.label2.grid(row=0, column=3, sticky=W)

        self.label3 = ttk.Label(self, text="SV1", padding=(5,2))
        self.label3.grid(row=1, column=0, sticky=E)

        self.label4 = ttk.Label(self, text="SV2", padding=(5,2))
        self.label4.grid(row=2, column=0, sticky=E)

        self.button_sv1 = ttk.Button(self, text="Pulse", command=lambda:self.sv_pulse(1,int(self.on_time_ms.get())))
        self.button_sv1.grid(row=1, column=1)

        self.button_sv2 = ttk.Button(self, text="Pulse", command=lambda:self.sv_pulse(2,int(self.on_time_ms.get())))
        self.button_sv2.grid(row=2, column=1)

        self.button_sv1_on = ttk.Button(self, text="ON", command=lambda:self.sv_on(1))
        self.button_sv1_on.grid(row=1, column=2)

        self.button_sv1_off = ttk.Button(self, text="OFF", command=lambda:self.sv_off(1))
        self.button_sv1_off.grid(row=1, column=3)

        self.button_sv2_on = ttk.Button(self, text="ON", command=lambda:self.sv_on(2))
        self.button_sv2_on.grid(row=2, column=2)

        button_sv2_off = ttk.Button(self, text="OFF", command=lambda:self.sv_off(2))
        button_sv2_off.grid(row=2, column=3)

    def sv_pulse(self, ch, on_time_ms):
        try:
            on_time_s = on_time_ms/1000
            Relay.pulse(ch, on_time_s)
        except:
            messagebox.showinfo("エラー", "・「on time」の入力が半角数字になっているか\n・USBリレーが接続されているか\n確認してください")

    def sv_on(self, ch):
        try:
            Relay.on(ch)
        except:
            messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")

    def sv_off(self, ch):
        try:
            Relay.off(ch)
        except:
            messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")


if __name__ == "__main__":

    root = Tk()
    app = solenoid_valve_control(master=root)
    app.mainloop()