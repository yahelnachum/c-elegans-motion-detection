import numpy as np
import cv2
import sys
from win32api import GetSystemMetrics

# get screen properties
screenXPositionOffset = -16
screenWidthOffset = 15
screenWidth = GetSystemMetrics(0) + screenWidthOffset
screenHeight = GetSystemMetrics(1)

# get video and its properties
video = sys.argv[1]
cap = cv2.VideoCapture(video)
capWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
capHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# calculate window properties
windows = 2
windowWidth = int(screenWidth / windows)
windowHeight = int(windowWidth / capWidth * capHeight)

# set window properties
cv2.namedWindow('frame',cv2.WINDOW_NORMAL)
cv2.namedWindow('what',cv2.WINDOW_NORMAL)

cv2.resizeWindow('frame', windowWidth, windowHeight)
cv2.resizeWindow('what', windowWidth, windowHeight)

cv2.moveWindow("frame", 0 + screenXPositionOffset, 0);
cv2.moveWindow("what", windowWidth + screenXPositionOffset, 0);

stillImage = None
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

    frame = cv2.resize(frame, (windowWidth, windowHeight)) 
    thresh_frame = cv2.resize(thresh_frame, (windowWidth, windowHeight)) 
    thresh_frame = cv2.cvtColor(thresh_frame, cv2.COLOR_GRAY2RGB)
    cv2.imshow('frame',frame)
    cv2.imshow('what',thresh_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

