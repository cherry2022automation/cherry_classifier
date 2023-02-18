import cv2
import picture
import copy
import numpy as np
import math

pic = picture.picture(0, 0, 0)
pic.use_masked_img = True
pic.original = cv2.imread("toku.jpg")
pic.frame = pic.original
pic.get_cherry_area(pic.area_min)
pic.get_flower_pattern_area(pic.area_min)
result = pic.original

contours, hierarchy = cv2.findContours(pic.flower_pattern_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


for cherry_info in pic.cherry_infos:
    
    x = int(cherry_info["center_x"])
    y = int(cherry_info["center_y"])

    floral_base_dist_min = None
    floral_base_x = None
    floral_base_y = None
    for contour in contours:
        for floral_outline_xy in contour:
            x2 = floral_outline_xy[0][0]
            y2 = floral_outline_xy[0][1]
            d = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
            if floral_base_dist_min is None or d < floral_base_dist_min:
                floral_base_dist_min = d
                floral_base_x = x2
                floral_base_y = y2
    print(floral_base_x, floral_base_y)

    cv2.circle(pic.original,center=(x,y),radius=3,color=(255,255,255),thickness=-1)
    cv2.circle(pic.original,center=(floral_base_x,floral_base_y),radius=3,color=(255,255,255),thickness=-1)
        
cv2.imshow("result", result)
cv2.waitKey(0)