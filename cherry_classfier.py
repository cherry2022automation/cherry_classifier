# ================================================
# Cherry Classifier.py
# ================================================
# Cherry Classifier 操作用プログラム
# ------------------------------------------------

import threading
import tkinter
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
from PIL import Image, ImageTk
from picture import picture
import time
import Relay
import datetime
import solenoid_valve

# 電磁弁操作クラス
class solenoid_valve_control(solenoid_valve.solenoid_valve_control):
    sv_num = 2

# メインフレーム
class Application(tkinter.Frame):

    # ----------------------------------------------------------------------------------------------

    # カメラ番号
    oder_T = 1
    oder_F = 3
    oder_R = 2

    # エアー電磁弁ON時間
    sv_on_time = 0.15   # [s]

    # カメラ中心-電磁弁位置 時間
    delay_toku = 1.55 # [s]
    delay_shu = 2.6  # [s]

    # ウィンドウ表示イネーブル
    view_en = { "original":False,
                "cherry mask":False, "toku mask":False, "shu mask":False, "hane mask":False,
                # "masked cherry":True, "masked toku":True, "masked shu":True, "masked hane":True}
                "masked cherry":False, "masked toku":False, "masked shu":False, "masked hane":False}

    # 描画イネーブル
    draw_box_en = True
    draw_text_en = True
    draw_line_en = False

    print_fps_en = False

    # 取得画像最大サイズ
    cap_width = 1920
    cap_height = 1080

    # ラベリング時しきい値(果実面積)
    original_cherry_area_min = 50000

    # カメラ解像度拡大率
    scale = 0.2

    center_line_color = (0,255,0)
    center_line_thick = 2

    # 画像更新インターバル
    roop_interval = 5   # [mS]

    # -----------------------------------------------------------------------------------------------

    last_cycle_end = None

    # 従属変数
    width = int(cap_width*scale)
    height = int(cap_height*scale)
    area_min = int(original_cherry_area_min*scale*scale)

    # 電磁弁タスクスケジュールリスト
    schedule_toku = []
    schedule_shu = []
    
    def __init__(self, master=None):

        # ウィンドウ初期化
        super().__init__(master)
        self.master = master
        self.master.title('Cherry Classfier')
        self.pack()
        
        # 画像表示用キャンバス配置
        self.canvas_F = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_F.grid(row=0, column=0)
        self.canvas_T = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_T.grid(row=0, column=1)
        self.canvas_R = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_R.grid(row=1, column=0)
        self.canvas_B = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_B.grid(row=1, column=1)

        # 画像オブジェクト生成
        self.cam_T = picture(self.oder_T, self.width, self.height, area_min=self.area_min)
        self.cam_F = picture(self.oder_F, self.width, self.height, area_min=self.area_min)
        self.cam_R = picture(self.oder_R, self.width, self.height, area_min=self.area_min)

        # カメラ初期化
        self.cam_T.cam_set()
        self.cam_F.cam_set()
        self.cam_R.cam_set()

        # メニューバー配置
        men = tkinter.Menu(self)
        self.master.config(menu=men)

        menu_operation = tkinter.Menu(self.master)
        men.add_cascade(label="操作", menu=menu_operation)
        # 電磁弁操作
        menu_operation.add_command(label="電磁弁操作", command=self.sv_operation)

        menu_setting = tkinter.Menu(self.master)
        men.add_cascade(label="設定", menu=menu_setting)
        menu_setting.add_command(label="パラメータ設定", command=self.set_parameter)

        # 画像更新処理開始
        self.update_picture()

    # 画像更新処理
    def update_picture(self):

        self.cam_T.get_img(flip=True)
        self.cam_F.get_img(flip=True)
        self.cam_R.get_img()
        
        # 画像取得 (マルチスレッド)
        th_cam_T = threading.Thread(target=self.cam_T.get_cherry_area, args=(self.area_min,))
        th_cam_F = threading.Thread(target=self.cam_F.get_cherry_area, args=(self.area_min,))
        th_cam_R = threading.Thread(target=self.cam_R.get_cherry_area, args=(self.area_min,))
        th_cam_T.start()
        th_cam_F.start()
        th_cam_R.start()
        th_cam_T.join()
        th_cam_R.join()
        th_cam_F.join()
        
        # centerに来たら識別+エアー制御予約 (タスクリストに追加)
        for info in self.cam_F.cherry_infos:
            if info["centered"]==False and self.width/2<info["center_x"]:
                self.identification()
                if info["grade"] == "tokushu":
                    self.schedule_toku.append(datetime.datetime.now()+datetime.timedelta(seconds=self.delay_toku))
                    print("detect tokushu")
                if info["grade"] == "shu":
                    self.schedule_shu.append(datetime.datetime.now()+datetime.timedelta(seconds=self.delay_shu))
                    print("detect shu")
                info["centered"]=True

        # 識別結果描画
        self.cam_F.draw_result(box=self.draw_box_en, text=self.draw_text_en)
        self.cam_R.draw_result(box=self.draw_box_en, text=self.draw_text_en)
        self.cam_T.draw_result(box=self.draw_box_en, text=self.draw_text_en)

        # 画像配置
        pic_T = self.cam_T.output_img
        self.img_tk_T = self.cv2_to_tk(self.draw_center_line(pic_T))
        self.canvas_T.create_image(0, 0, image=self.img_tk_T, anchor='nw') # ImageTk 画像配置
        
        pic_F = self.cam_F.output_img
        self.img_tk_F = self.cv2_to_tk(self.draw_center_line(pic_F))
        self.canvas_F.create_image(0, 0, image=self.img_tk_F, anchor='nw') # ImageTk 画像配置

        pic_R = self.cam_R.output_img
        self.img_tk_R = self.cv2_to_tk(self.draw_center_line(pic_R))
        self.canvas_R.create_image(0, 0, image=self.img_tk_R, anchor='nw') # ImageTk 画像配置

        del_list = []
        # エアー制御予約の実行 (特秀)
        for sche in self.schedule_toku:
            if sche < datetime.datetime.now():
                Relay.pulse_with_thread(1, self.sv_on_time)
                self.schedule_toku.remove(sche)

        del_list = []
        # エアー制御予約の実行 (秀)
        for sche in self.schedule_shu:
            if sche < datetime.datetime.now():
                Relay.pulse_with_thread(2, self.sv_on_time)
                self.schedule_shu.remove(sche)

        self.view()

        # ループ用
        self.after(self.roop_interval, self.update_picture)

        if self.print_fps_en == True:
            cycle_end = time.time()
            if self.last_cycle_end != None:
                cycle_time = cycle_end - self.last_cycle_end
                fps = 1/cycle_time
                print("fps : ", str(fps))
            self.last_cycle_end = cycle_end
        

    # 等級識別
    def identification(self):

        # 各等級色領域取得(マルチスレッド)
        th_cam_F = threading.Thread(target=self.cam_F.get_grade_color_area)
        th_cam_R = threading.Thread(target=self.cam_F.get_grade_color_area)
        th_cam_T = threading.Thread(target=self.cam_F.get_grade_color_area)
        th_cam_F.start()
        th_cam_R.start()
        th_cam_T.start()
        th_cam_F.join()
        th_cam_R.join()
        th_cam_T.join()

        # 3画面の果実のx位置が近ければ
        for c_info_F in self.cam_F.cherry_infos:
            for c_info_R in self.cam_R.cherry_infos:
                for c_info_T in self.cam_T.cherry_infos:

                    # 画面中央のもののみ
                    if c_info_F["centered"]==False and self.width/2<c_info_F["center_x"]:

                        if c_info_R["left"]<c_info_F["center_x"] and c_info_F["center_x"]<c_info_R["right"]:
                            if c_info_T["left"]<c_info_F["center_x"] and c_info_F["center_x"]<c_info_T["right"]:

                                # 各等級領域の面積を各々合計
                                toku_area = c_info_F["toku_area"] + c_info_R["toku_area"] + c_info_T["toku_area"]
                                shu_area = c_info_F["shu_area"] + c_info_R["shu_area"] + c_info_T["shu_area"]
                                hane_area = c_info_F["hane_area"] + c_info_R["hane_area"] + c_info_T["hane_area"]
                                # 識別
                                grade = "?"
                                if shu_area<toku_area and hane_area<toku_area:
                                    grade = "tokushu"
                                elif toku_area<shu_area and hane_area<shu_area:
                                    grade = "shu"
                                elif toku_area<hane_area and shu_area<hane_area:
                                    grade = "hanedashi"
                                c_info_F["grade"] = grade
                                c_info_R["grade"] = grade
                                c_info_T["grade"] = grade

    # エアー制御
    def sv_push(self, ch, on_time, delay_s):
        time.sleep(delay_s)
        Relay.pulse(ch, on_time)

    # 画像変換 OpenCV→tkinter
    def cv2_to_tk(self, img):
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        image_pil = Image.fromarray(image_rgb) # RGBからPILフォーマットへ変換
        image_tk  = ImageTk.PhotoImage(image_pil) # ImageTkフォーマットへ変換
        return image_tk

    # センターライン(x)描画
    def draw_center_line(self, img):

        if self.draw_line_en==True:

            # 画像サイズ取得
            height, width, channels = img.shape[:3]
            # height_half = int(height/2)
            width_half = int(width/2)

            # 描画
            # cv2.line(img, (0, height_half), (width, height_half), self.color, thickness=self.thick, lineType=cv2.LINE_8, shift=0)
            cv2.line(img, (width_half, 0), (width_half, height), self.center_line_color, thickness=self.center_line_thick, lineType=cv2.LINE_8, shift=0)

        return img

    def view(self):

        for name in ["original", "cherry mask", "toku mask", "shu mask", "hane mask", "masked cherry", "masked toku", "masked shu", "masked hane"]:
            if self.view_en[name] == True:
                im_FR = cv2.vconcat([self.cam_F.pic[name], self.cam_R.pic[name]])
                im_TB = cv2.vconcat([self.cam_T.pic[name], self.cam_B.pic[name]])
                combine = cv2.hconcat([im_FR, im_TB])
                cv2.imshow(name, combine)

    # 設定ウィンドウ
    def set_parameter(self):

        self.setting_win = tkinter.Toplevel(self)
        self.setting_win.title("Modal Dialog") # ウィンドウタイトル
        self.setting_win.geometry("300x200")   # ウィンドウサイズ(幅x高さ)

        self.label_sv_on_time = tkinter.Label(self.setting_win, text="電磁弁ON時間[s]")
        self.label_sv_on_time.grid(row=0, column=0, sticky=tkinter.E)

        self.box_sv_on_time_val = tkinter.StringVar()
        box_sv_on_time = tkinter.Entry(self.setting_win, textvariable=self.box_sv_on_time_val, width = 10, justify=tkinter.RIGHT)
        box_sv_on_time.insert(0, self.sv_on_time)
        box_sv_on_time.grid(row=0, column=1)

        self.label_delay_toku = tkinter.Label(self.setting_win, text="カメラ中央-SV1時間[s]")
        self.label_delay_toku.grid(row=1, column=0)

        self.box_delay_toku_val = tkinter.StringVar()
        box_delay_toku = tkinter.Entry(self.setting_win, textvariable=self.box_delay_toku_val, width = 10, justify=tkinter.RIGHT)
        box_delay_toku.insert(0, self.delay_toku)
        box_delay_toku.grid(row=1, column=1)

        self.label_delay_shu = tkinter.Label(self.setting_win, text="カメラ中央-SV2時間[s]")
        self.label_delay_shu.grid(row=2, column=0)

        self.box_delay_shu_val = tkinter.StringVar()
        box_delay_shu = tkinter.Entry(self.setting_win, textvariable=self.box_delay_shu_val, width = 10, justify=tkinter.RIGHT)
        box_delay_shu.insert(0, self.delay_shu)
        box_delay_shu.grid(row=2, column=1)

        apply_button = tkinter.Button(self.setting_win, text="適用", command=lambda:self.apply_setting())
        apply_button.grid(row=2, column=2)

    def apply_setting(self):
        self.sv_on_time = float(self.box_sv_on_time_val.get())
        self.delay_toku = float(self.box_delay_toku_val.get())
        self.delay_shu = float(self.box_delay_shu_val.get())
        self.setting_win.destroy()

# 電磁弁操作
    def sv_operation(self):
        window = tkinter.Toplevel(self)
        window.title("電磁弁操作")
        app = solenoid_valve_control(window)

        # モーダルにする設定
        window.grab_set()        # モーダルにする
        window.focus_set()       # フォーカスを新しいウィンドウをへ移す
        # window.transient()   # タスクバーに表示しない

        # ダイアログが閉じられるまで待つ
        app.wait_window(window)  

if __name__ == "__main__":

    root = tkinter.Tk()
    app = Application(master=root)

    app.mainloop()