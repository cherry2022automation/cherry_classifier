import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import time
import cv2

camera_num = 1
width = 1920
height = 1080

cap = cv2.VideoCapture(camera_num)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,int(height))

shoot_times = []

for i in range(1001):

    time_start = time.time()
    ret, frame = cap.read()
    time_end = time.time()

    shoot_time = time_end - time_start
    shoot_times.append(shoot_time)

    cv2.imshow('picture', frame)
    key = cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()

del shoot_times[0]

shoot_time_ave = sum(shoot_times)/len(shoot_times)
print("shoot time ave ：" + str(shoot_time_ave) + "[s]")