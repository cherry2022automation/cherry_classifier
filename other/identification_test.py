import enum
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
import copy

class picture():

    cherry_hsv_min = [145, 0, 0]
    cherry_hsv_max = [10, 255, 255]
    tokushu_hsv_min = [152, 120, 0]
    tokushu_hsv_max = [170, 255, 200]
    shu_hsv_min = [160, 168, 170]
    shu_hsv_max = [178, 255, 255]
    hane_hsv_min = [177, 0, 0]
    hane_hsv_max = [10, 255, 255]

    original = None

    # hsv値域
    hsv_min = 0
    h_max = 179
    sv_max = 255

    H = 0
    S = 1
    V = 2

    def __init__(self, image):
        self.original = image

    def identification(self):

        # 色情報抽出
        self.mask_cherry, self.masked_img_cherry, stats_cherry = self.detection(self.cherry_hsv_min, self.cherry_hsv_max, area_min = 50000)
        self.mask_tokushu, self.masked_img_tokushu, stats_tokushu = self.detection(self.tokushu_hsv_min, self.tokushu_hsv_max)
        self.mask_shu, self.masked_img_shu, stats_shu = self.detection(self.shu_hsv_min, self.shu_hsv_max)
        self.mask_hane, self.masked_img_hane, stats_hane = self.detection(self.hane_hsv_min, self.hane_hsv_max)
        
        output_img = copy.copy(self.original)
        for i, row in enumerate(stats_cherry):
            TopLeft = ( row[cv2.CC_STAT_LEFT], row[cv2.CC_STAT_TOP] )
            ButtomRight = ( row[cv2.CC_STAT_LEFT]+row[cv2.CC_STAT_WIDTH], row[cv2.CC_STAT_TOP]+row[cv2.CC_STAT_HEIGHT])
            cv2.rectangle(output_img, TopLeft, ButtomRight, (255, 255, 0), thickness=5)
        return output_img
        # self.mask_tokushu, self.masked_img_tokushu = self.mask(self.original, self.tokushu_hsv_min, self.tokushu_hsv_max)
        # self.mask_shu, self.masked_img_shu = self.mask(self.original, self.shu_hsv_min, self.shu_hsv_max)
        # self.mask_hane, self.masked_img_hane = self.mask(self.original, self.hane_hsv_min, self.hane_hsv_max)

    def detection(self, range_min, range_max, area_min=None):
        mask, masked_img = self.mask(self.original, range_min, range_max)
        retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
        del_list = [0]
        if area_min != None:
            for i, row in enumerate(stats):
                if row[cv2.CC_STAT_AREA] < area_min:
                    del_list.append(i)         
        stats = np.delete(stats, del_list, 0)
        return mask, masked_img, stats

    def mask(self, img, range_min, range_max):
        # マスク処理
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_range_min_1, hsv_range_max_1, hsv_range_min_2, hsv_range_max_2 = self.consider_distant_range(range_min, range_max)
        mask1 = cv2.inRange(hsv, hsv_range_min_1, hsv_range_max_1)
        mask2 = cv2.inRange(hsv, hsv_range_min_2, hsv_range_max_2)
        mask = mask1 + mask2
        masked_img = cv2.bitwise_and(img, img, mask=mask)
        return mask, masked_img

    def consider_distant_range(self, range_min, range_max):

        h_min_1, h_max_1, h_min_2, h_max_2 = self.single_range(self.hsv_min, self.h_max, range_min[self.H], range_max[self.H])
        s_min_1, s_max_1, s_min_2, s_max_2 = self.single_range(self.hsv_min, self.sv_max, range_min[self.S], range_max[self.S])
        v_min_1, v_max_1, v_min_2, v_max_2 = self.single_range(self.hsv_min, self.sv_max, range_min[self.V], range_max[self.V])
        hsv_range_1_min = np.array([h_min_1, s_min_1, v_min_1])
        hsv_range_1_max = np.array([h_max_1, s_max_1, v_max_1])
        hsv_range_2_min = np.array([h_min_2, s_min_2, v_min_2])
        hsv_range_2_max = np.array([h_max_2, s_max_2, v_max_2])
        return hsv_range_1_min, hsv_range_1_max, hsv_range_2_min, hsv_range_2_max

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

color = (0,255,0)
thick = 5
camera_num = 1
width = 1920
height = 1080

capture = cv2.VideoCapture(camera_num, cv2.CAP_MSMF)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,int(height))

while(True):

    # 画像取得
    ret, frame = capture.read()

    picture_F = picture(frame)
    frame = picture_F.identification()

    # 画像サイズ取得
    height, width, channels = frame.shape[:3]
    height_half = int(height/2)
    width_half = int(width/2)

    # 描画
    cv2.line(frame, (0, height_half), (width, height_half), color, thickness=thick, lineType=cv2.LINE_8, shift=0)
    cv2.line(frame, (width_half, 0), (width_half, height), color, thickness=thick, lineType=cv2.LINE_8, shift=0)
    cv2.putText(frame,
                text='end with "q"',
                org=(0, height-30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=3.0,
                color=color,
                thickness=4,
                lineType=cv2.LINE_4)

    # フレーム描画
    cv2.imshow('frame',frame)

    # 「q」キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()