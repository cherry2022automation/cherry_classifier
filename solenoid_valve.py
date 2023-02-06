from csv import reader
import sys
from tkinter import messagebox, ttk
from tkinter import *
import Relay

# from pyparsing import col

class solenoid_valve_control(Frame):

    def __init__(self, master=None):

        # ウィンドウ初期化
        super().__init__(master)
        self.master = master
        self.master.title('電磁弁操作')
        self.pack()

        font_size = 20
        sv_num = 8

        self.label1 = ttk.Label(self, text="on time", padding=(5,2))
        self.label1.grid(row=0, column=1, sticky=E)

        self.on_time_ms = StringVar()
        self.time_entry = ttk.Entry(self, textvariable=self.on_time_ms, width = 10, justify=RIGHT)
        self.time_entry.insert(0, "30")
        self.time_entry.grid(row=0, column=2)

        self.label2 = ttk.Label(self, text="[ms]", padding=(5,2))
        self.label2.grid(row=0, column=3, sticky=W)


        self.label_sv_num = []
        self.button_pulse = []
        self.button_on = []
        self.button_off = []


        for i in range(8):

            self.label_sv_num.append(ttk.Label(self, text="SV"+str(i+1), padding=(5,2)))
            self.label_sv_num[i].grid(row=i+1, column=0, sticky=E)

            # self.button_pulse.append(ttk.Button(self, text="Pulse", command=lambda:self.sv_pulse(i_num,int(self.on_time_ms.get()))))
            self.button_pulse.append(ttk.Button(self, text="Pulse", command=self.sv_pulse(i)))
            self.button_pulse[i].grid(row=i+1, column=1, sticky=E)
            
            self.button_on.append(ttk.Button(self, text="ON", command=self.sv_on(i)))
            self.button_on[i].grid(row=i+1, column=2)

            self.button_off.append(ttk.Button(self, text="OFF", command=self.sv_off(i)))
            self.button_off[i].grid(row=i+1, column=3)

    def sv_pulse(self, ch):
        ch = ch+1
        def x():
            on_time_ms = int(self.on_time_ms.get())
            try:
                on_time_s = on_time_ms/1000
                Relay.pulse(ch, on_time_s)
            except:
                messagebox.showinfo("エラー", "・「on time」の入力が半角数字になっているか\n・USBリレーが接続されているか\n確認してください")
        return x


    def sv_on(self, ch):
        ch = ch+1
        def x():
            try:
                Relay.on(ch)
            except:
                messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")
        return x

    def sv_off(self, ch):
        ch = ch+1
        def x():
            try:
                Relay.off(ch)
            except:
                messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")
        return x

if __name__ == "__main__":

    root = Tk()
    app = solenoid_valve_control(master=root)
    app.mainloop()