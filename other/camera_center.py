# ==============================================
# camera_center.py
# カメラ位置調整用プログラム
#
# 2022/10/13 T19JM042 長谷季樹
#
# 参考： https://weblabo.oscasierra.net/python/opencv-videocapture-camera.html
# 　　　 https://qiita.com/Zumwalt/items/202f2728b6354984e88b
#　　　  https://github.com/opencv/opencv/issues/21408
#       https://qiita.com/youichi_io/items/b894b85d790720ea2346
#       https://shikaku-mafia.com/opencv-puttext/
# ==============================================

import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2

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