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

    color = (0,255,0)
    thick = 3
    camera_num = 1
    scale = 0.3
    width = int(1920*scale)
    height = int(1080*scale)
    area_min = int(50000*scale*scale)
    schedule_toku = []
    schedule_shu = []
    
    def __init__(self, img, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('tkinter canvas trial')
        self.pack()

        image_bgr = img
        
        image_bgr = cv2.resize(image_bgr, dsize=None, fx=0.4, fy=0.4)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        image_pil = Image.fromarray(image_rgb) # RGBからPILフォーマットへ変換
        self.image_tk_F  = ImageTk.PhotoImage(image_pil) # ImageTkフォーマットへ変換

        self.canvas_F = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_F.grid(row=0, column=0)
        self.canvas_F.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas_T = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_T.grid(row=0, column=1)
        self.canvas_T.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas_R = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_R.grid(row=1, column=0)
        self.canvas_R.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas_B = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas_B.grid(row=1, column=1)
        self.canvas_B.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置

        self.cam_T = picture(oder_T, self.width, self.height, area_min=self.area_min)
        self.cam_B = picture(oder_B, self.width, self.height, area_min=self.area_min)
        self.cam_F = picture(oder_F, self.width, self.height, area_min=self.area_min)
        self.cam_R = picture(oder_R, self.width, self.height, area_min=self.area_min)
        self.cam_T.cam_set()
        self.cam_B.cam_set()
        self.cam_F.cam_set()
        self.cam_R.cam_set()

        time.sleep(5)
        

        self.update_picture()

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

        
        for info_i in range(len(self.cam_F.cherry_infos)):
            # 前フレームのさくらんぼと一致確認
            for info_before in self.cam_F.cherry_infos_before:
                if info_before["center_x"]-5 < self.cam_F.cherry_infos[info_i]["center_x"] and self.cam_F.cherry_infos[info_i]["center_x"] < info_before["center_x"]+10:
                    self.cam_F.cherry_infos[info_i]["centered"] = info_before["centered"]

            if self.cam_F.cherry_infos[info_i]["center_x"] < self.width/4:
                self.cam_F.cherry_infos[info_i]["centered"] = False
            if (self.width*3)/4 < self.cam_F.cherry_infos[info_i]["center_x"]:
                self.cam_F.cherry_infos[info_i]["centered"] = True
            # centerに来たらエアータイマーセット
            if self.width/2 < self.cam_F.cherry_infos[info_i]["center_x"] and self.cam_F.cherry_infos[info_i]["centered"]==False:
            # if self.width/2-5 < info["center_x"] and info["center_x"] < self.width/2+5:
                self.cam_F.cherry_infos[info_i]["centered"] = True
                if self.cam_F.cherry_infos[info_i]["grade"] == "tokushu":
                    self.schedule_toku.append(datetime.datetime.now()+datetime.timedelta(seconds=11))
                    print("detect tokushu")
                if self.cam_F.cherry_infos[info_i]["grade"] == "shu":
                    self.schedule_shu.append(datetime.datetime.now()+datetime.timedelta(seconds=17))
                    print("detect shu")
        self.cam_F.cherry_infos_before = self.cam_F.cherry_infos
        # print(self.cam_F.cherry_infos)

        del_list = []
        for i in range(len(self.schedule_toku)):
            if self.schedule_toku[i] < datetime.datetime.now():
                Relay.pulse(1, 0.05)
                del_list.append(i)
        for i in del_list:
            del self.schedule_toku[i]

        del_list = []
        for i in range(len(self.schedule_shu)):
            if self.schedule_shu[i] < datetime.datetime.now():
                Relay.pulse(2, 0.05)
                del_list.append(i)
        for i in del_list:
            del self.schedule_shu[i]

        self.after(5, self.update_picture)

    def sv_push(self, ch, on_time, delay_s):
        time.sleep(delay_s)
        Relay.pulse(ch, on_time)

    def cv2_to_tk(self, img):
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
        image_pil = Image.fromarray(image_rgb) # RGBからPILフォーマットへ変換
        image_tk  = ImageTk.PhotoImage(image_pil) # ImageTkフォーマットへ変換
        return image_tk

    def draw_center_line(self, img):

        # 画像サイズ取得
        height, width, channels = img.shape[:3]
        height_half = int(height/2)
        width_half = int(width/2)

        # 描画
        cv2.line(img, (0, height_half), (width, height_half), self.color, thickness=self.thick, lineType=cv2.LINE_8, shift=0)
        cv2.line(img, (width_half, 0), (width_half, height), self.color, thickness=self.thick, lineType=cv2.LINE_8, shift=0)

        return img


if __name__ == "__main__":



    img = cv2.imread("photo.jpg")

    root = tkinter.Tk()
    app = Application(img, master=root)
    app.mainloop()

    # 



        