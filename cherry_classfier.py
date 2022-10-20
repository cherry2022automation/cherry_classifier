import threading
import tkinter
import cv2
from PIL import Image, ImageTk
from matplotlib import image
from picture import picture
import time

class Application(tkinter.Frame):

    color = (0,255,0)
    thick = 3
    camera_num = 1
    scale = 0.05
    width = int(1920*scale)
    height = int(1080*scale)
    area_min = int(50000*scale*scale)
    # width = 1920
    # height = 1080
    # area_min = 50000
    
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

        self.canvas = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas.grid(row=0, column=0)
        self.canvas.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas2 = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas2.grid(row=0, column=1)
        self.canvas2.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas3 = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas3.grid(row=1, column=0)
        self.canvas3.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置
        self.canvas4 = tkinter.Canvas(self, width=self.width, height=self.height) # Canvas作成
        self.canvas4.grid(row=1, column=1)
        self.canvas4.create_image(0, 0, image=self.image_tk_F, anchor='nw') # ImageTk 画像配置


        self.cam_T = picture(1, self.width, self.height, area_min=self.area_min)
        cam_thread_T = threading.Thread(target=self.cam_T.get_img)
        cam_thread_T.start()
        self.cam_B = picture(2, self.width, self.height, area_min=self.area_min)
        cam_thread_B = threading.Thread(target=self.cam_B.get_img)
        cam_thread_B.start()
        self.cam_F = picture(3, self.width, self.height, area_min=self.area_min)
        cam_thread_F = threading.Thread(target=self.cam_F.get_img)
        cam_thread_F.start()
        self.cam_R = picture(4, self.width, self.height, area_min=self.area_min)
        cam_thread_R = threading.Thread(target=self.cam_R.get_img)
        cam_thread_R.start()

        time.sleep(5)
        

        self.update_picture()

    def update_picture(self):
        
        # 画像取得
        pic_T = self.cam_T.result
        self.img_tk_T = self.cv2_to_tk(self.draw_center_line(pic_T))
        self.canvas.create_image(0, 0, image=self.img_tk_T, anchor='nw') # ImageTk 画像配置

        pic_B = self.cam_B.result
        self.img_tk_B = self.cv2_to_tk(self.draw_center_line(pic_B))
        self.canvas2.create_image(0, 0, image=self.img_tk_B, anchor='nw') # ImageTk 画像配置
        
        pic_F = self.cam_F.result
        self.img_tk_F = self.cv2_to_tk(self.draw_center_line(pic_F))
        self.canvas3.create_image(0, 0, image=self.img_tk_F, anchor='nw') # ImageTk 画像配置

        pic_R = self.cam_R.result
        self.img_tk_R = self.cv2_to_tk(self.draw_center_line(pic_R))
        self.canvas.create_image(0, 0, image=self.img_tk_R, anchor='nw') # ImageTk 画像配置

        self.after(10, self.update_picture)

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



        