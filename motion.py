import numpy as np
import cv2
import time

#C:\Users\YahelNachum\AppData\Local\Programs\Python\Python38-32\python.exe "C:\Users\YahelNachum\Desktop\Caroline Worms\motion.py"

#now = time.time()
cap = cv2.VideoCapture('C:\\Users\\YahelNachum\\Desktop\\Caroline Worms\\caroline-worm-1.avi')
#cap = cv2.VideoCapture('A4_P2_0805200001.avi')
stillImage = None
#future = time.time()
#print("videocapture: ", future-now)
#now = time.time()

#cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
#cv2.resizeWindow('frame', 1200,1000)

#cv2.namedWindow('thres',cv2.WINDOW_NORMAL)
#cv2.resizeWindow('thres', 1200,1000)

width=int(1800 * 0.4)
height=int(1500 * 0.4)

count = 0
limit = 1
while(cap.isOpened()):
    ret, frame = cap.read()

#    future = time.time()
#    print("read: ", future-now)
#    now = time.time()

    if not(ret):
        break
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)

    if stillImage is None:
        stillImage = gray
        continue
    # Still Image and current image.
    diff_frame = cv2.absdiff(stillImage, gray)
    thresh_frame = cv2.threshold(diff_frame, 8, 255, cv2.THRESH_BINARY)[1]

    contours,hierachy = cv2.findContours(thresh_frame.copy(),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
#        motion = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

#    cv2.imshow('frame',gray)
#    cv2.imshow('frame',diff_frame)

#    future = time.time()
#    print("calculations: ", future-now)
#    now = time.time()

#    if (count % show == 0):

    frame = cv2.resize(frame, (width, height)) 
    thresh_frame = cv2.resize(thresh_frame, (width, height)) 
    thresh_frame = cv2.cvtColor(thresh_frame, cv2.COLOR_GRAY2RGB)
    if (count % limit == 0):
        cv2.imshow('frame',frame)
        cv2.moveWindow("frame", 0,0);
        cv2.imshow('what',thresh_frame)
        cv2.moveWindow("what", width,0);
#        cv2.imshow('frame',frame)
#        cv2.imshow('thres',thresh_frame)

    count = count + 1

#    future = time.time()
#    print("imshow: ", future-now)
#    now = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

