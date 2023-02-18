import cv2
import picture
import copy
import numpy as np
import math

draw_color = (255,0,0)

pic = picture.picture(0, 1920, 1080)
pic.use_masked_img = True
pic.original = cv2.imread("hane_shu_toku.jpg")
pic.frame = pic.original
pic.get_cherry_area(pic.area_min)
pic.get_flower_pattern_area(50)
pic.get_diameter()
pic.draw_result()

cv2.imshow("result", pic.output_img)
cv2.waitKey(0)