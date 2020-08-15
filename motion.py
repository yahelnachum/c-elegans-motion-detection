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
window1Name = 'final'
window2Name = 'mask'
cv2.namedWindow(window1Name,cv2.WINDOW_NORMAL)
cv2.namedWindow(window2Name,cv2.WINDOW_NORMAL)

cv2.resizeWindow(window1Name, windowWidth, windowHeight)
cv2.resizeWindow(window2Name, windowWidth, windowHeight)

cv2.moveWindow(window1Name, 0 + screenXPositionOffset, 0);
cv2.moveWindow(window2Name, windowWidth + screenXPositionOffset, 0);

# general image processing properties
blur = (11, 11)
threshold = 10
contourAreaMin = 10
boundingRectColor = (0, 255, 0)
boundingRectThickness = 3

stillImage = None
while(cap.isOpened()):
    ret, frame = cap.read()

    if not(ret):
        break

    # turn image to grayscale and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, blur, 0)

    # take first frame as the background
    if stillImage is None:
        stillImage = gray
        continue

    # get mask of motion
    diff_frame = cv2.absdiff(stillImage, gray)
    thresh_frame = cv2.threshold(diff_frame, threshold, 255, cv2.THRESH_BINARY)[1]

    # get contours of mask
    contours,hierachy = cv2.findContours(thresh_frame.copy(),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # draw bounding rectangles around contours
    for contour in contours:
        if cv2.contourArea(contour) < contourAreaMin:
            continue
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), boundingRectColor, boundingRectThickness)

    # resize images for windows
    frame = cv2.resize(frame, (windowWidth, windowHeight)) 
    thresh_frame = cv2.resize(thresh_frame, (windowWidth, windowHeight)) 
    thresh_frame = cv2.cvtColor(thresh_frame, cv2.COLOR_GRAY2RGB)

    # display images on windows
    cv2.imshow(window1Name,frame)
    cv2.imshow(window2Name,thresh_frame)

    # break out of program on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# clean up
cap.release()
cv2.destroyAllWindows()

