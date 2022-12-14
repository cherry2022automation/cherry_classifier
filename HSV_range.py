# =============================================
# HSV_checker
# ---------------------------------------------
# 指定したHSV範囲の画素以外をマスクして表示
# ---------------------------------------------
# 2022/10/20
# 山梨大学 工学部 メカトロニクス工学科
# T19JM042 長谷季樹
# =============================================

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import cv2
import sys

class Application(ttk.Frame):

    mask_color = (0, 255, 255)

    # スライドバー 長さ
    length_num = 200

    # hsv値域
    hsv_min = 0
    h_max = 179
    sv_max = 255

    row_label = 0
    row_min = 1
    row_max = 2
    row_pic = 3

    column_label = 0
    column_h_sc = 1
    column_h_lb = 2
    column_s_sc = 3
    column_s_lb = 4
    column_v_sc = 5
    column_v_lb = 6

    lb_val_width = 5

    now_dir = "C:"

    def __init__(self, image=None, master=None, view=False):
        super().__init__(master)
        self.grid(row=0, column=0)

        self.view_en = view
        self.cv2_image = image

        self.new_window()

    def new_window(self):

        self.master.title('HSV Checker')
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Frame
        self.frame = ttk.Frame(self.master, padding=10)
        self.frame.grid(sticky=(N, W, S, E))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        # ラベルの作成
        self.label1 = ttk.Label(self.frame, text='Hue', padding=(5, 10))
        self.label1.grid(row=self.row_label, column=self.column_h_sc)

        self.label2 = ttk.Label(self.frame, text='Saturation', padding=(5, 10))
        self.label2.grid(row=self.row_label, column=self.column_s_sc)

        self.label3 = ttk.Label(self.frame, text='Value', padding=(5, 10))
        self.label3.grid(row=self.row_label, column=self.column_v_sc)

        self.label4 = ttk.Label(self.frame, text='Min', padding=(5, 10))
        self.label4.grid(row=self.row_min, column=self.column_label, sticky=(E))

        self.label5 = ttk.Label(self.frame, text='Max', padding=(5, 10))
        self.label5.grid(row=self.row_max, column=self.column_label, sticky=(E))


        self.label_h_min = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_h_min.grid(row=self.row_min , column=self.column_h_lb, sticky=(W))

        self.label_h_max = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_h_max.grid(row=self.row_max , column=self.column_h_lb, sticky=(W))

        self.label_s_min = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_s_min.grid(row=self.row_min , column=self.column_s_lb, sticky=(W))

        self.label_s_max = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_s_max.grid(row=self.row_max , column=self.column_s_lb, sticky=(W))

        self.label_v_min = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_v_min.grid(row=self.row_min , column=self.column_v_lb, sticky=(W))

        self.label_v_max = ttk.Label(self.frame, text='0', padding=(5, 10), width=self.lb_val_width)
        self.label_v_max.grid(row=self.row_max , column=self.column_v_lb, sticky=(W))

        #　スケール用ウィジット変数
        self.val_h_min = DoubleVar()
        self.val_s_min = DoubleVar()
        self.val_v_min = DoubleVar()
        self.val_h_max = DoubleVar()
        self.val_s_max = DoubleVar()
        self.val_v_max = DoubleVar()


        # スケールの作成
        self.sc_h_min = ttk.Scale(self.frame, variable=self.val_h_min, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.h_max, command=lambda e: self.update_screen())
        self.sc_h_min.grid(row=self.row_min, column=self.column_h_sc, sticky=(N, E, S, W))
        
        self.sc_s_min = ttk.Scale(self.frame, variable=self.val_s_min, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.sv_max, command=lambda e: self.update_screen())
        self.sc_s_min.grid(row=self.row_min, column=self.column_s_sc, sticky=(N, E, S, W))
        
        self.sc_v_min = ttk.Scale(self.frame, variable=self.val_v_min, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.sv_max, command=lambda e: self.update_screen())
        self.sc_v_min.grid(row=self.row_min, column=self.column_v_sc, sticky=(N, E, S, W))
        
        self.sc_h_max = ttk.Scale(self.frame, variable=self.val_h_max, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.h_max, command=lambda e: self.update_screen())
        self.sc_h_max.grid(row=self.row_max, column=self.column_h_sc, sticky=(N, E, S, W))
        self.sc_h_max.set(self.h_max)
        
        self.sc_s_max = ttk.Scale(self.frame, variable=self.val_s_max, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.sv_max, command=lambda e: self.update_screen())
        self.sc_s_max.grid(row=self.row_max, column=self.column_s_sc, sticky=(N, E, S, W))
        self.sc_s_max.set(self.sv_max)
        
        self.sc_v_max = ttk.Scale(self.frame, variable=self.val_v_max, orient=HORIZONTAL, length=self.length_num, from_=self.hsv_min, to=self.sv_max, command=lambda e: self.update_screen())
        self.sc_v_max.grid(row=self.row_max, column=self.column_v_sc, sticky=(N, E, S, W))
        self.sc_v_max.set(self.sv_max)

        # メニューバー作成
        men = Menu(self)
        self.master.config(menu=men)

        menu_file = Menu(self)
        men.add_cascade(label="ファイル", menu=menu_file)
        menu_file.add_command(label="開く", command=self.open_file)

        menu_setting = Menu(self)
        men.add_cascade(label="設定", menu=menu_setting)
        menu_setting.add_command(label="マスク色", command=self.update_mask_color)


    # 画面更新処理
    def update_screen(self):
        self.label_h_min["text"] = int(self.val_h_min.get())
        self.label_h_max["text"] = int(self.val_h_max.get())
        self.label_s_min["text"] = int(self.val_s_min.get())
        self.label_s_max["text"] = int(self.val_s_max.get())
        self.label_v_min["text"] = int(self.val_v_min.get())
        self.label_v_max["text"] = int(self.val_v_max.get())
        if self.view_en==True:
            self.update_masked_picture()

    # 画像更新処理
    def update_masked_picture(self):

        if self.cv2_image is None:
            return

        # マスク処理
        hsv = cv2.cvtColor(self.cv2_image, cv2.COLOR_BGR2HSV)
        hsv_range_min_1, hsv_range_max_1, hsv_range_min_2, hsv_range_max_2 = self.hsv_range()
        mask1 = cv2.inRange(hsv, hsv_range_min_1, hsv_range_max_1)
        mask2 = cv2.inRange(hsv, hsv_range_min_2, hsv_range_max_2)
        mask = mask1 + mask2
        masked_img = cv2.bitwise_and(self.cv2_image, self.cv2_image, mask=mask)
        masked_img[mask==0]=self.mask_color

        # 表示
        cv2.namedWindow("HSV masked image", cv2.WINDOW_NORMAL)
        cv2.imshow("HSV masked image", masked_img)

    # 元画像更新
    def update_original_picture(self):
        if self.cv2_image is None:
            return
        try:
            if self.view_en==True:
                cv2.namedWindow("original", cv2.WINDOW_NORMAL)
                cv2.imshow("original", self.cv2_image)
        except:
            messagebox.showinfo("エラー", "画像の読み込みに失敗しました")
            sys.exit()

    # HSV抽出範囲取得
    def hsv_range(self):
        h_min_1, h_max_1, h_min_2, h_max_2 = self.single_range(self.hsv_min, self.h_max, self.val_h_min.get(), self.val_h_max.get())
        s_min_1, s_max_1, s_min_2, s_max_2 = self.single_range(self.hsv_min, self.sv_max, self.val_s_min.get(), self.val_s_max.get())
        v_min_1, v_max_1, v_min_2, v_max_2 = self.single_range(self.hsv_min, self.sv_max, self.val_v_min.get(), self.val_v_max.get())
        hsv_range_min_1 = np.array([h_min_1, s_min_1, v_min_1])
        hsv_range_max_1 = np.array([h_max_1, s_max_1, v_max_1])
        hsv_range_min_2 = np.array([h_min_2, s_min_2, v_min_2])
        hsv_range_max_2 = np.array([h_max_2, s_max_2, v_max_2])
        return hsv_range_min_1, hsv_range_max_1, hsv_range_min_2, hsv_range_max_2

    # h,s,v 単体抽出範囲取得
    def single_range(self, range_min, range_max, min, max):

        if min <= max:
            min_1 = min
            max_1 = max
            min_2 = min
            max_2 = max

        elif max < min:
            min_1 = range_min
            max_1 = max
            min_2 = min
            max_2 = range_max

        return min_1, max_1, min_2, max_2

    def open_file(self):

        # 画像読み込み
        filetypes = [("Image file", ".bmp .png .jpg .tif"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif")]
        file_pass = filedialog.askopenfilename(title="画像ファイルを開く", filetypes=filetypes, initialdir=self.now_dir)          
        image = cv2.imread(file_pass)

        if image is not None:
            self.cv2_image = image
            self.now_dir = file_pass

        # 画面更新
        self.update_original_picture()
        self.update_screen()

    # マスク色更新
    def update_mask_color(self):

        try:
            r = int(input("R:"))
            g = int(input("G:"))
            b = int(input("B:"))

            for i in [r,g,b]:
                if i < 0:
                    i=0
                elif 255 < i:
                    i=255
            self.mask_color = (r,g,b)
            self.update_screen()
        except:
            print("更新失敗：0~255を入力してください")

if __name__ == "__main__":

    

    # ウィンドウ表示
    root = Tk()
    app = Application(master=root, view=True)
    app.mainloop()