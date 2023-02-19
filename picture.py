import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import numpy as np
import copy
import math

class picture():

    # ---------------------------------------------------------------

    use_masked_img = False

    # box+文字の色
    result_color_toku = (0, 0, 255)
    result_color_shu = (0, 165, 255)
    result_color_hane = (0, 255, 255)
    char_color = (0,0,0)
    size_guide_color = (255,0,0)

    # 文字サイズ
    fontscale = 1

    # 画素ずれ余裕(さくらんぼ領域-hsv抽出領域)
    area_offset = 50
    
    # 画素ずれ余裕(さくらんぼ位置引き継ぎ時x座標)
    continuity_x_offset = 30

    # hsv抽出範
    # サンプル果実用
    cherry_hsv_min = [145, 0, 0]
    cherry_hsv_max = [30, 255, 255]
    tokushu_hsv_min = [152, 120, 0]
    tokushu_hsv_max = [170, 255, 200]
    shu_hsv_min = [160, 168, 170]
    shu_hsv_max = [178, 255, 255]
    hane_hsv_min = [177, 0, 0]
    hane_hsv_max = [17, 255, 255]
    flower_pattern_hsv_min = [90, 50, 150]
    flower_pattern_hsv_max = [100, 255, 210]

    # 冷凍果実用
    # cherry_hsv_min = [110, 93, 0]
    # cherry_hsv_max = [170, 231, 160]
    # tokushu_hsv_min = [110, 93, 0]
    # tokushu_hsv_max = [170, 231, 160]

    flower_area_min = 50

    # ---------------------------------------------------------------

    # リスト参照用
    H = 0
    S = 1
    V = 2    

    cherry_infos = []
    old_cherry_infos = []

    original = None

    # hsv値域
    hsv_min = 0
    h_max = 179
    sv_max = 255

    def __init__(self, num, width, height, area_min=50000):
        self.num = num
        self.width = width
        self.height = height
        self.area_min = area_min
        pass

    # カメラ初期化, 設定
    def cam_set(self):
        self.area_min = self.area_min

        self.capture = cv2.VideoCapture(self.num, cv2.CAP_MSMF)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.width))
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,int(self.height))

    # カメラファイナライズ
    def cam_release(self):
        self.capture.release()

    # 画像取得+さくらんぼ領域取得
    def get_img(self, flip=False):

        ret, self.frame = self.capture.read()
        if flip==True:
            self.frame = cv2.flip(self.frame, 1)
        self.original = self.frame

    # さくらんぼ領域取得
    def get_cherry_area(self, area_min):

        self.cherry_mask, self.masked_cherry, self.stats_cherry = self.detection(self.cherry_hsv_min, self.cherry_hsv_max, area_min = area_min)
        self.pic = {"original":self.original,
                    "cherry mask":self.cherry_mask,
                    "toku mask":None,
                    "shu mask":None,
                    "hane mask":None,
                    "flower pattern mask":None,
                    "masked cherry":self.masked_cherry,
                    "masked toku":None,
                    "masked shu":None,
                    "masked hane":None,
                    "masked flower pattern":None}

        self.old_cherry_infos = self.cherry_infos
        self.cherry_infos = []

        # さくらんぼ情報取得 (果実位置情報)
        self.cherry_label_infos = self.label_info(self.stats_cherry)
        for cherry_label_info in self.cherry_label_infos:

            # データ格納
            cherry_info = { "left":cherry_label_info["left"],
                            "right":cherry_label_info["right"],
                            "top":cherry_label_info["top"],
                            "bottom":cherry_label_info["bottom"],
                            "center_x":int(cherry_label_info["center_x"]),
                            "center_y":int(cherry_label_info["center_y"]),
                            "width":cherry_label_info["right"]-cherry_label_info["left"],
                            "height":cherry_label_info["bottom"]-cherry_label_info["top"],
                            "toku_area":0,
                            "shu_area":0,
                            "hane_area":0,
                            "grade":"",
                            "Floral_base_x":None,
                            "Floral_base_y":None,
                            "diameter_edge1_x":None,
                            "diameter_edge1_y":None,
                            "diameter_edge2_x":None,
                            "diameter_edge2_y":None,
                            "diameter_pixel":None,
                            "size":None,
                            "centered":False}

            # 位置情報の引き継ぎ
            for old_cherry_info in self.old_cherry_infos:
                if old_cherry_info["left"]-self.continuity_x_offset<cherry_info["center_x"] and cherry_info["center_x"]<old_cherry_info["right"]+self.continuity_x_offset:
                    cherry_info["centered"] = old_cherry_info["centered"]
                    cherry_info["grade"] = old_cherry_info["grade"]
                    cherry_info["size"] = old_cherry_info["size"]

            self.cherry_infos.append(cherry_info)

    # 花柄領域取得
    def get_flower_pattern_area(self, area_min):
        self.flower_pattern_mask, self.masked_flower_pattern, self.stats_flower_pattern = self.detection(self.flower_pattern_hsv_min, self.flower_pattern_hsv_max, area_min = area_min)
        self.pic["flower pattern mask"] = self.flower_pattern_mask
        self.pic["masked flower pattern"] = self.masked_flower_pattern

    # 赤道径取得
    def get_diameter(self):
        self.get_flower_pattern_area(self.flower_area_min)

        for cherry_info in self.cherry_infos:

            # 花柄輪郭抽出
            contours, hierarchy = cv2.findContours(self.flower_pattern_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # 果実中心座標
            cherry_x = int(cherry_info["center_x"])
            cherry_y = int(cherry_info["center_y"])

            # 果実中心ー花柄根本 最短距離計算→根本座標取得
            floral_base_dist_min = None
            floral_base_x = None
            floral_base_y = None
            for contour in contours:
                for floral_outline_xy in contour:
                    x2 = floral_outline_xy[0][0]
                    y2 = floral_outline_xy[0][1]
                    d = math.sqrt((x2 - cherry_x) ** 2 + (y2 - cherry_y) ** 2)
                    if floral_base_dist_min is None or d < floral_base_dist_min:
                        floral_base_dist_min = d
                        floral_base_x = x2
                        floral_base_y = y2
            # print(floral_base_x, floral_base_y)

            # 花柄根本座標が遠すぎる場合は花柄無しとする
            if floral_base_dist_min is None or cherry_info["width"]*1.5 < floral_base_dist_min:
                continue
            cherry_info["Floral_base_x"] = floral_base_x
            cherry_info["Floral_base_y"] = floral_base_y

            # 赤道線(マスク用)1次関数計算
            if floral_base_x==cherry_x:     # ゼロ除算回避
                a=0
            else:
                a = (floral_base_y - cherry_y)/(floral_base_x - cherry_x)
                if a==0:
                    a=math.inf
                else:
                    a = -(1/a)
            
            if a==math.inf or a==np.inf:    # 赤道径が縦線の場合
                d=cherry_info["height"]
                cherry_info["diameter_edge1_x"] = int(cherry_info["center_x"])
                cherry_info["diameter_edge1_y"] = int(cherry_info["top"])
                cherry_info["diameter_edge2_x"] = int(cherry_info["center_x"])
                cherry_info["diameter_edge2_y"] = int(cherry_info["bottom"])

            else:   # その他(基本こっち)

                b = cherry_y - a*cherry_x
                pt1_x = int(cherry_info["left"] - cherry_info["width"]*0.1)
                pt1_y = int(a * pt1_x + b)
                pt2_x = int(cherry_info["right"] + cherry_info["width"]*0.1)
                pt2_y = int(a * pt2_x + b)

                # 赤道線マスク画像生成
                height, width, channels = self.original.shape[:3]
                mask=np.zeros((height,width),dtype=np.uint8)
                equator_mask = copy.copy(self.cherry_mask)
                cv2.line(mask, (pt1_x, pt1_y), (pt2_x, pt2_y), 255, 1, cv2.LINE_4)
                equator_mask[mask==0] = [0]

                # 赤道径(pixel)取得
                contours, hierarchy = cv2.findContours(equator_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
                area_max_num = 0
                for i in range(len(contours)):
                    if cv2.contourArea(contours[area_max_num]) < cv2.contourArea(contours[i]):
                        area_max_num = i
                rect = cv2.minAreaRect(contours[i])
                box = cv2.boxPoints(rect)
                pt1_x=box[0][0]
                pt1_y=box[0][1]
                pt2_x=box[1][0]
                pt2_y=box[1][1]
                pt3_x=box[2][0]
                pt3_y=box[2][1]
                d12 = math.sqrt((pt2_x - pt1_x) ** 2 + (pt2_y - pt1_y) ** 2)
                d13 = math.sqrt((pt3_x - pt1_x) ** 2 + (pt3_y - pt1_y) ** 2)

                if d13 < d12:
                    d=d12
                    cherry_info["diameter_edge2_x"] = int(pt2_x)
                    cherry_info["diameter_edge2_y"] = int(pt2_y)
                else:
                    d=d13
                    cherry_info["diameter_edge2_x"] = int(pt3_x)
                    cherry_info["diameter_edge2_y"] = int(pt3_y)

                cherry_info["diameter_edge1_x"] = int(pt1_x)
                cherry_info["diameter_edge1_y"] = int(pt1_y)

            cherry_info["diameter_pixel"] = d

    # 等級色の取得
    def get_grade_color_area(self):

        # 色情報抽出
        self.toku_mask, self.masked_toku, stats_toku = self.detection(self.tokushu_hsv_min, self.tokushu_hsv_max)
        self.shu_mask, self.masked_shu, stats_shu = self.detection(self.shu_hsv_min, self.shu_hsv_max)
        self.hane_mask, self.masked_hane, stats_hane = self.detection(self.hane_hsv_min, self.hane_hsv_max)
        
        self.pic["toku mask"] = self.toku_mask
        self.pic["shu mask"] = self.shu_mask
        self.pic["hane mask"] = self.hane_mask
        self.pic["masked toku"] = self.masked_toku
        self.pic["masked shu"] = self.masked_shu
        self.pic["masked hane"] = self.masked_hane        

        for cherry_info in self.cherry_infos:

            # 画素のズレを考慮したサクランボ概説矩形座標
            c_offset_top = cherry_info["top"]-self.area_offset
            c_offset_bottom = cherry_info["bottom"]+self.area_offset
            c_offset_left = cherry_info["left"]-self.area_offset
            c_offset_right = cherry_info["right"]+self.area_offset

            # 各等級領域の面積取得
            toku_label_info = self.label_info(stats_toku)
            for r_info in toku_label_info:
                    if c_offset_left<r_info["left"] and r_info["right"]<c_offset_right and c_offset_top<r_info["top"] and r_info["bottom"]<c_offset_bottom:
                            cherry_info["toku_area"] += r_info["area"]
            shu_label_info = self.label_info(stats_shu)
            for r_info in shu_label_info:
                    if c_offset_left<r_info["left"] and r_info["right"]<c_offset_right and c_offset_top<r_info["top"] and r_info["bottom"]<c_offset_bottom:
                            cherry_info["shu_area"] += r_info["area"]
            hane_label_info = self.label_info(stats_hane)
            for r_info in hane_label_info:
                    if c_offset_left<r_info["left"] and r_info["right"]<c_offset_right and c_offset_top<r_info["top"] and r_info["bottom"]<c_offset_bottom:
                            cherry_info["hane_area"] += r_info["area"]

    # 結果の描画
    def draw_result(self, box=True, text=True, size_guide=True):
        # 表示用画像
        self.output_img = copy.copy(self.original)

        # ボックス+識別結果描画
        for c_info in self.cherry_infos:

            color = (0,0,0)
            if c_info["grade"]=="tokushu":
                color = self.result_color_toku
            if c_info["grade"]=="shu":
                color = self.result_color_shu
            if c_info["grade"]=="hanedashi":
                color = self.result_color_hane

            if text==True:
                cv2.putText(self.output_img,
                            text="{} {}".format(c_info["grade"], c_info["size"]),
                            org=(c_info["left"], c_info["top"]-10),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=self.fontscale,
                            color=self.char_color,
                            thickness=4,
                            lineType=cv2.LINE_4)
            if box==True:
                LeftTop = (c_info["left"], c_info["top"])
                RightButtom = (c_info["right"], c_info["bottom"])
                cv2.rectangle(self.output_img, LeftTop, RightButtom, color, thickness=5)

            if size_guide==True and c_info["diameter_pixel"] is not None:
                cv2.circle(self.output_img,center=(c_info["center_x"],c_info["center_y"]),radius=10,color=self.size_guide_color,thickness=-1)
                cv2.circle(self.output_img,center=(c_info["Floral_base_x"],c_info["Floral_base_y"]),radius=10,color=self.size_guide_color,thickness=3)
                cv2.line(self.output_img, (c_info["center_x"], c_info["center_y"]), (c_info["Floral_base_x"],c_info["Floral_base_y"]), self.size_guide_color, 3, cv2.LINE_4)
                cv2.line(self.output_img, (c_info["diameter_edge1_x"], c_info["diameter_edge1_y"]), (c_info["diameter_edge2_x"], c_info["diameter_edge2_y"]), self.size_guide_color, 3, cv2.LINE_4)

        return self.output_img

    # 色領域取得
    def detection(self, range_min, range_max, area_min=None):
        mask, masked_img = self.mask(self.original, range_min, range_max)
        retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
        del_list = [0]
        if area_min != None:
            for i, row in enumerate(stats):
                if row[cv2.CC_STAT_AREA] < area_min:
                    del_list.append(i)
                    mask[labels==i] = 0
        stats = np.delete(stats, del_list, 0)
        if self.use_masked_img == True:
            masked_img[mask==0] = [0,0,0]
        else:
            masked_img = None
        return mask, masked_img, stats

    # hsv指定範囲でマスク処理
    def mask(self, img, range_min, range_max):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hsv_range_min_1, hsv_range_max_1, hsv_range_min_2, hsv_range_max_2 = self.consider_distant_range(range_min, range_max)
        mask1 = cv2.inRange(hsv, hsv_range_min_1, hsv_range_max_1)
        mask2 = cv2.inRange(hsv, hsv_range_min_2, hsv_range_max_2)
        mask = mask1 + mask2
        if self.use_masked_img == True:
            masked_img = cv2.bitwise_and(img, img, mask=mask)
        else:
            masked_img = None
        return mask, masked_img

    # hsv抽出範囲取得 (バンドカット対応)
    def consider_distant_range(self, range_min, range_max):

        h_min_1, h_max_1, h_min_2, h_max_2 = self.single_range(self.hsv_min, self.h_max, range_min[self.H], range_max[self.H])
        s_min_1, s_max_1, s_min_2, s_max_2 = self.single_range(self.hsv_min, self.sv_max, range_min[self.S], range_max[self.S])
        v_min_1, v_max_1, v_min_2, v_max_2 = self.single_range(self.hsv_min, self.sv_max, range_min[self.V], range_max[self.V])
        hsv_range_1_min = np.array([h_min_1, s_min_1, v_min_1])
        hsv_range_1_max = np.array([h_max_1, s_max_1, v_max_1])
        hsv_range_2_min = np.array([h_min_2, s_min_2, v_min_2])
        hsv_range_2_max = np.array([h_max_2, s_max_2, v_max_2])
        return hsv_range_1_min, hsv_range_1_max, hsv_range_2_min, hsv_range_2_max

    # h,s,v 単体抽出範囲取得 (バンドカット対応)
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

    # ラベリング結果をリストで返す
    def label_info(self, stats):
        info = []
        for i, row in enumerate(stats):
            left = row[cv2.CC_STAT_LEFT]
            width = row[cv2.CC_STAT_WIDTH]
            top = row[cv2.CC_STAT_TOP]
            height = row[cv2.CC_STAT_HEIGHT]
            area = row[cv2.CC_STAT_AREA]
            right = left + width
            bottom = top+height
            center_x = left + width/2
            center_y = top + height/2
            info.append({"left":left, "right":right, "top":top, "bottom":bottom, "center_x":center_x, "center_y":center_y, "area":area})
        return info

if __name__ == "__main__":

    color = (0,255,0)
    thick = 3
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
        frame = picture_F.get_grade_color_area()

        # 画像サイズ取得
        height, width, channels = frame.shape[:3]
        height_half = int(height/2)
        width_half = int(width/2)

        # 描画
        cv2.line(frame, (0, height_half), (width, height_half), color, thickness=thick, lineType=cv2.LINE_8, shift=0)
        cv2.line(frame, (width_half, 0), (width_half, height), color, thickness=thick, lineType=cv2.LINE_8, shift=0)

        # フレーム描画
        cv2.imshow('frame',frame)

        # 「q」キーで終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()