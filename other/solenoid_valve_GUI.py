from csv import reader
import sys
from tkinter import messagebox, ttk
from tkinter import *
import Relay

from pyparsing import col

def sv_pulse(ch, on_time_ms):
    try:
        on_time_s = on_time_ms/1000
        Relay.pulse(ch, on_time_s)
    except:
        messagebox.showinfo("エラー", "・「on time」の入力が半角数字になっているか\n・USBリレーが接続されているか\n確認してください")

def sv_on(ch):
    try:
        Relay.on(ch)
    except:
        messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")

def sv_off(ch):
    try:
        Relay.off(ch)
    except:
        messagebox.showinfo("エラー", "USBリレーが接続されているか確認してください")

font_size = 20

root = Tk()
root.title(u"USB Relay control")

frame1 = ttk.Frame(root, padding=(32))
frame1.grid()

label1 = ttk.Label(frame1, text="on time", padding=(5,2))
label1.grid(row=0, column=1, sticky=E)

on_time_ms = StringVar()
time_entry = ttk.Entry(frame1, textvariable=on_time_ms, width = 10, justify=RIGHT)
time_entry.insert(0, "30")
time_entry.grid(row=0, column=2)

label2 = ttk.Label(frame1, text="[ms]", padding=(5,2))
label2.grid(row=0, column=3, sticky=W)

label3 = ttk.Label(frame1, text="SV1", padding=(5,2))
label3.grid(row=1, column=0, sticky=E)

label4 = ttk.Label(frame1, text="SV2", padding=(5,2))
label4.grid(row=2, column=0, sticky=E)

button_sv1 = ttk.Button(frame1, text="Pulse", command=lambda:sv_pulse(1,int(on_time_ms.get())))
button_sv1.grid(row=1, column=1)

button_sv2 = ttk.Button(frame1, text="Pulse", command=lambda:sv_pulse(2,int(on_time_ms.get())))
button_sv2.grid(row=2, column=1)

button_sv1_on = ttk.Button(frame1, text="ON", command=lambda:sv_on(1))
button_sv1_on.grid(row=1, column=2)

button_sv1_off = ttk.Button(frame1, text="OFF", command=lambda:sv_off(1))
button_sv1_off.grid(row=1, column=3)

button_sv2_on = ttk.Button(frame1, text="ON", command=lambda:sv_on(2))
button_sv2_on.grid(row=2, column=2)

button_sv2_off = ttk.Button(frame1, text="OFF", command=lambda:sv_off(2))
button_sv2_off.grid(row=2, column=3)



root.mainloop()