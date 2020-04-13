# coding: utf-8
from __future__ import division
import webiopi
import os
import numpy as np
import cv2
import math
import sys
from PIL import Image

#webiopi
#save directory
SAVEDIR = '/home/pi/ex7'
#a function to take a picture when it is called from html
@webiopi.macro
def camera():
    path = SAVEDIR + '/camera.jpg'
    #taking a photo
    command = 'fswebcam -r 640x480 -d /dev/video0 ' + path
    os.system(command)
    #writing to disk cache
    os.system('sync')
    return path

face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')

img = cv2.imread(camera(), cv2.IMREAD_COLOR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray)
    
for (x,y,w,h) in faces:
    img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    roi_gray = gray[y:y+h, x:x+w]
    #顔の上半分を検出対象範囲
    eye_gray = gray[y : y + (int)(h/2), x : x+w]
    roi_color = img[y:y+h, x:x+w]
    totalx = x
    totaly = y
    for i in range(1,20):
        minValue = i * 5
        eyes = eye_cascade.detectMultiScale(eye_gray, scaleFactor=1.11, minNeighbors=5, minSize=(minValue,minValue))        
        ce = []
        el = list(eyes)
        for (ex,ey,ew,eh) in el:
            ce.append([ex,ey,ew,eh])
        if len(ce) == 2:
            break
    for (ex,ey,ew,eh) in ce:
        cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

cv2.imwrite('test.jpg',img)

#サングラスの合成
layer1 = Image.open('camera.jpg')
layer2 = Image.open('glasses.png')
w,h = layer2.size

# 合成のため、RGBAモードに変更
layer1 = layer1.convert('RGBA')
# 同じ大きさの透過キャンパスを用意
c = Image.new('RGBA', layer1.size, (255, 255,255, 0))

aaax=0
aaay=0
bbbx=0
bbby=0
tmp = 0

# rect[0]:x, rect[1]:y, rect[2]:width, rect[3]:height
for rect in eyes:
    # 上書きする画像をリサイズ
    if rect[2] > rect[3]:
        rate = rect[2] / w
    else:
        rate = rect[3] / h

    resize_img = layer2.resize((int(w*rate*0.83), int(h*rate*0.83)))
            
    if aaax == 0:
        aaax = totalx+rect[0]
        aaay = totaly+rect[1]
    else:
        bbbx = totalx+rect[0]+rect[2]
        bbby = totaly+rect[1]

if aaax==0 and aaay==0 and bbbx==0 and bbby==0:
    print("目の検出に失敗しました。再度撮影して下さい。")
    sys.exit()

if bbbx > 0:
    #左右の目の位置から角度を検出
    if aaax < bbbx:
        rad= math.atan2(bbby-aaay,bbbx-aaax)
    else:
        rad= math.atan2(aaay-bbby,aaax-bbbx)
    deg = math.degrees(rad)
    print("rad:",rad," deg:",deg)
    if deg > 0 and deg < 90:
        deg = 0-deg
    elif deg >= 90:
        deg = 180-deg
    elif deg < -90:
        deg = 0-deg
        deg = 180-deg
    else:
        deg = 0-deg
        
#print("deg:",deg)
sg_rotate =  resize_img.rotate(deg,expand=True)
    
# 用意したキャンパスに上書き
if deg > 10:
    aaay = aaay-30
    bbby = bbby-30
if aaax < bbbx:
    c.paste(sg_rotate, (aaax-25,aaay+12), sg_rotate)
else:
    c.paste(sg_rotate, (bbbx-25,bbby+12), sg_rotate)
    
# オリジナルとキャンパスを合成して保存
result = Image.alpha_composite(layer1, c)
result.save('result.jpg')
res = cv2.imread('result.jpg', cv2.IMREAD_COLOR)
cv2.imshow('result.jpg',res)

cv2.waitKey(0)
cv2.destroyAllWindows()
