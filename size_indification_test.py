import cv2
import picture
import copy
import numpy as np
import math

draw_color = (255,0,0)

pic = picture.picture(0, 0, 0)
pic.use_masked_img = True
pic.original = cv2.imread("hane_shu_toku.jpg")
pic.frame = pic.original
pic.get_cherry_area(pic.area_min)
pic.get_flower_pattern_area(50)

cv2.imshow("flower", pic.masked_flower_pattern)
cv2.imshow("cherry", pic.masked_cherry)

result = copy.copy(pic.original)

# contours, hierarchy = cv2.findContours(pic.flower_pattern_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


for cherry_info in pic.cherry_infos:

    # 花柄輪郭抽出
    contours, hierarchy = cv2.findContours(pic.flower_pattern_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
    if cherry_info["width"] < floral_base_dist_min:
        continue

    cv2.circle(result,center=(cherry_x,cherry_y),radius=10,color=draw_color,thickness=-1)
    cv2.circle(result,center=(floral_base_x,floral_base_y),radius=10,color=draw_color,thickness=3)
    cv2.line(result, (cherry_x, cherry_y), (floral_base_x, floral_base_y), draw_color, 3, cv2.LINE_4)

    # 赤道線(マスク用)1次関数計算
    a = (floral_base_y - cherry_y)/(floral_base_x - cherry_x)
    a = -(1/a)
    b = cherry_y - a*cherry_x
    pt1_x = int(cherry_info["left"] - cherry_info["width"]*0.1)
    pt1_y = int(a * pt1_x + b)
    pt2_x = int(cherry_info["right"] + cherry_info["width"]*0.1)
    pt2_y = int(a * pt2_x + b)
    # cv2.line(result, (pt1_x, pt1_y), (pt2_x, pt2_y), draw_color, 3, cv2.LINE_4)

    # 赤道線マスク画像生成
    mask=np.zeros((1080,1920),dtype=np.uint8)
    equator_mask = copy.copy(pic.cherry_mask)
    cv2.line(mask, (pt1_x, pt1_y), (pt2_x, pt2_y), 255, 1, cv2.LINE_4)
    equator_mask[mask==0] = [0]

    # 赤道径(pixel)取得
    contours, hierarchy = cv2.findContours(equator_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    rect = cv2.minAreaRect(contours[0])
    box = cv2.boxPoints(rect)
    pt1_x=box[0][0]
    pt1_y=box[0][1]
    pt2_x=box[1][0]
    pt2_y=box[1][1]
    d = math.sqrt((pt2_x - pt1_x) ** 2 + (pt2_y - pt1_y) ** 2)
    # print(d)

    cv2.line(result, (int(pt1_x), int(pt1_y)), (int(pt2_x), int(pt2_y)), draw_color, 3, cv2.LINE_4)

cv2.imshow("result", result)
cv2.waitKey(0)