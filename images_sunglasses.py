# coding: utf-8
from __future__ import division
import os
import numpy as np
import cv2
import math
import sys
from PIL import Image

@webiopi
def sg():
    image_path = 'woman.jpg'

    #サングラスの合成
    face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')

    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)
 
    for (x,y,w,h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        # 顔の上半分を検出対象範囲
        eye_gray = gray[y : y + (int)(h/2), x : x+w]
        totalx = x
        totaly = y
        for i in range(1,20):
            minValue = i * 5
            eyes = eye_cascade.detectMultiScale(eye_gray, minSize=(minValue,minValue))        
            ce = []
            el = list(eyes)
            for (ex,ey,ew,eh) in el:
                ce.append([ex,ey,ew,eh])
            if len(ce) == 2:
                break
        for (ex,ey,ew,eh) in ce:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    cv2.imwrite('test2.jpg',img)

    #サングラスの合成
    layer1 = Image.open('woman.jpg')
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

    # rect[0]:x, rect[1]:y, rect[2]:width, rect[3]:height
    for rect in eyes:
        # 上書きする画像をリサイズ
        if rect[2] > rect[3]:
            rate = rect[2] / w
        else:
            rate = rect[3] / h

        resize_img = layer2.resize((int(w*rate*0.7), int(h*rate*0.7)))
        if aaax == 0:
            aaax = totalx+rect[0]
            aaay = totaly+rect[1]
        else:
            bbbx = totalx+rect[0]+rect[2]
            bbby = totaly+rect[1]

    if aaax==0 and aaay==0 and bbbx==0 and bbby==0:
        print("目の検出に失敗しました。再度顔を撮影してください。\n")
        sys.exit()

    if bbbx > 0:
        #左右の目の位置から角度を検出    
        rad= math.atan2(bbby-aaay,bbbx-aaax)
        deg = math.degrees(rad)
        #print("rad:",rad," deg:",deg)
        if deg > 0 and deg < 90:
            deg = 0-deg
        elif deg >= 90:
            deg = 180-deg
        elif deg < -90:
            deg = 0-deg
            deg = 180-deg
        
    sg_rotate =  resize_img.rotate(deg,expand=True)

    # 用意したキャンパスに上書き
    c.paste(sg_rotate, (aaax-25,aaay+12), sg_rotate)
    
    
    # オリジナルとキャンパスを合成して保存
    result = Image.alpha_composite(layer1, c)
    result.save('result2.jpg')

