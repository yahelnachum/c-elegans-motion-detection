import numpy as np
import cv2
import sys

video = sys.argv[1]
cap = cv2.VideoCapture(video)
stillImage = None

width=int(1900 * 0.4)
height=int(1400 * 0.4)

cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
cv2.namedWindow('what',cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', width, height)
cv2.resizeWindow('what', width, height)
cv2.moveWindow("frame", 0,0);
cv2.moveWindow("what", width,0);

while(cap.isOpened()):
    ret, frame = cap.read()

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
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    frame = cv2.resize(frame, (width, height)) 
    thresh_frame = cv2.resize(thresh_frame, (width, height)) 
    thresh_frame = cv2.cvtColor(thresh_frame, cv2.COLOR_GRAY2RGB)
    cv2.imshow('frame',frame)
    cv2.imshow('what',thresh_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

