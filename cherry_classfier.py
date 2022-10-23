import threading
import tkinter
import cv2
from PIL import Image, ImageTk
from matplotlib import image
from picture import picture
import time
import Relay
import datetime

oder_T = 1
oder_B = 4
oder_F = 3
oder_R = 2

class Application(tkinter.Frame):

    # 取得画像サイズ
    cap_width = 1920
    cap_height = 1080

    # ラベリング時しきい値(果実面積)
    original_cherry_area_min = 50000

    # 表示時拡大率
    scale = 0.45

    # エアー電磁弁ON時間
    sv_on_time = 0.15   # [s]
    
    # カメラ中心-電磁弁位置 時間
    delay_toku = 11 # [s]
    delay_shu = 17  # [s]

    color = (0,255,0)
    center_line_thick = 2

    roop_interval = 5   # [m]

    # 従属変数
    width = int(cap_width*scale)
    height = int(cap_height*scale)
    area_min = int(original_cherry_area_min*scale*scale)

    # 電磁弁タスクスケジュールリスト
    schedule_toku = []
    schedule_shu = []
    
    def __init__(self, img, master=None):

        # ウィンドウ初期化
        super().__init__(master)
        self.master = master
        self.master.title('tkinter canvas trial')
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
        self.cam_T = picture(oder_T, self.width, self.height, area_min=self.area_min)
        self.cam_B = picture(oder_B, self.width, self.height, area_min=self.area_min)
        self.cam_F = picture(oder_F, self.width, self.height, area_min=self.area_min)
        self.cam_R = picture(oder_R, self.width, self.height, area_min=self.area_min)

        # カメラ初期化
        self.cam_T.cam_set()
        self.cam_B.cam_set()
        self.cam_F.cam_set()
        self.cam_R.cam_set()

        # 画像更新処理開始
        self.update_picture()

    # 画像更新処理
    def update_picture(self):
        
        # 画像取得
        self.cam_T.get_img(flip=True)
        pic_T = self.cam_T.result
        self.img_tk_T = self.cv2_to_tk(self.draw_center_line(pic_T))
        self.canvas_T.create_image(0, 0, image=self.img_tk_T, anchor='nw') # ImageTk 画像配置

        self.cam_B.get_img()
        pic_B = self.cam_B.result
        self.img_tk_B = self.cv2_to_tk(self.draw_center_line(pic_B))
        self.canvas_B.create_image(0, 0, image=self.img_tk_B, anchor='nw') # ImageTk 画像配置
        
        self.cam_F.get_img(flip=True)
        pic_F = self.cam_F.result
        self.img_tk_F = self.cv2_to_tk(self.draw_center_line(pic_F))
        self.canvas_F.create_image(0, 0, image=self.img_tk_F, anchor='nw') # ImageTk 画像配置

        self.cam_R.get_img()
        pic_R = self.cam_R.result
        self.img_tk_R = self.cv2_to_tk(self.draw_center_line(pic_R))
        self.canvas_R.create_image(0, 0, image=self.img_tk_R, anchor='nw') # ImageTk 画像配置

        # centerに来たらエアー制御予約 (タスクリストに追加)
        for info in self.cam_F.cherry_infos:
            if info["centered"]==False and self.width/2<info["center_x"]:
                if info["grade"] == "tokushu":
                    self.schedule_toku.append(datetime.datetime.now()+datetime.timedelta(seconds=self.delay_toku))
                    print("detect tokushu")
                if info["grade"] == "shu":
                    self.schedule_shu.append(datetime.datetime.now()+datetime.timedelta(seconds=self.delay_shu))
                    print("detect shu")
                info["centered"]=True

        del_list = []
        # エアー制御予約の実行 (特秀)
        for i in range(len(self.schedule_toku)):
            if self.schedule_toku[i] < datetime.datetime.now():
                Relay.pulse(1, self.sv_on_time)
                del_list.append(i)
        for i in del_list:
            del self.schedule_toku[i]

        del_list = []
        # エアー制御予約の実行 (秀)
        for i in range(len(self.schedule_shu)):
            if self.schedule_shu[i] < datetime.datetime.now():
                Relay.pulse(2, self.sv_on_time)
                del_list.append(i)
        for i in del_list:
            del self.schedule_shu[i]

        # ループ用
        self.after(self.roop_interval, self.update_picture)

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

        # 画像サイズ取得
        height, width, channels = img.shape[:3]
        # height_half = int(height/2)
        width_half = int(width/2)

        # 描画
        # cv2.line(img, (0, height_half), (width, height_half), self.color, thickness=self.thick, lineType=cv2.LINE_8, shift=0)
        cv2.line(img, (width_half, 0), (width_half, height), self.color, thickness=self.center_line_thick, lineType=cv2.LINE_8, shift=0)

        return img


if __name__ == "__main__":

    img = cv2.imread("photo.jpg")

    root = tkinter.Tk()
    app = Application(img, master=root)
    app.mainloop()




        