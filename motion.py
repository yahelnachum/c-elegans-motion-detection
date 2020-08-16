import numpy as np
import cv2
import sys
from win32api import GetSystemMetrics
import math
import re

# get screen properties
screenXPositionOffset = -13
screenWidthOffset = 10
screenWidth = GetSystemMetrics(0) + screenWidthOffset
screenHeight = GetSystemMetrics(1)

# get video and its properties
videoFilePath = sys.argv[1]
videoFileFolder = re.sub('/[^/]*$', '/', videoFilePath)
p = re.compile('.*/([^/.]*).*$')
m = p.match(videoFilePath)
videoFileName = m.group(1)
cap = cv2.VideoCapture(videoFilePath)
capWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
capHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# calculate window properties
windows = 3
windowWidth = int(screenWidth / windows)
downscaled_factor = windowWidth / capWidth
windowHeight = int(downscaled_factor * capHeight)

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
dropletCirclePosition = [(100,100)]
dropletCircleRadius = [100]
dropletCircleIndex=0
cv2.namedWindow("Current Circle",cv2.WINDOW_NORMAL)
cv2.moveWindow("Current Circle", 0 + screenXPositionOffset, windowHeight);
cv2.resizeWindow("Current Circle", 250, 250)

isButtonDown = False

def getDropletCircleRadius(x, y):
    global dropletCirclePosition, dropletCircleRadius
    diffX = dropletCirclePosition[dropletCircleIndex][0] - (x / downscaled_factor)
    diffY = dropletCirclePosition[dropletCircleIndex][1] - (y / downscaled_factor)
    dropletCircleRadius[dropletCircleIndex] = int(math.sqrt(diffX**2 + diffY**2))

mode='center'
def click_and_crop(event, x, y, flags, param):
    global mode, dropletCirclePosition, dropletCircleRadius, isButtonDown, dropletCircleIndex
    if event == cv2.EVENT_LBUTTONDOWN:
        isButtonDown = True
        if mode == 'duplicate':
            dropletCirclePosition.append((int(x/downscaled_factor),int(y/downscaled_factor)))
            dropletCircleRadius.append(dropletCircleRadius[dropletCircleIndex])
            dropletCircleIndex = len(dropletCirclePosition) - 1
        if mode == 'center':
            dropletCirclePosition[dropletCircleIndex] = (int(x/downscaled_factor),int(y/downscaled_factor))
        if mode == 'radius':
            getDropletCircleRadius(x,y)
#    elif event == cv2.EVENT_MOUSEMOVE:
    elif event == cv2.EVENT_LBUTTONUP:
        isButtonDown = False
cv2.setMouseCallback(window1Name, click_and_crop)

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale              = 2
lineType               = 2

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

    for i in range(len(dropletCirclePosition)):

        dropletCircleColor = (255, 255, 255)
        dropletCircleColor1 = (255, 255, 255)
        fontColor = (255,255,255)
        if i == dropletCircleIndex:
            fontColor = (0,0,255)
            if mode == 'center':
                dropletCircleColor = (0, 0, 255)
            if mode == 'radius':
                dropletCircleColor1 = (0, 0, 255)
            if mode == 'duplicate':
                dropletCircleColor = (255, 0, 0)
                dropletCircleColor1 = (255, 0, 0)

        cv2.circle(frame, dropletCirclePosition[i], dropletCircleRadius[i], dropletCircleColor1, boundingRectThickness)
        cv2.circle(frame, dropletCirclePosition[i], 10, dropletCircleColor, boundingRectThickness)
        cv2.putText(frame, str(i), (dropletCirclePosition[i][0] + 10, dropletCirclePosition[i][1] - 10), font, fontScale, fontColor, lineType)

        if i == dropletCircleIndex:
            buffer = 40
            y0 = max(0, min(dropletCirclePosition[i][1]-dropletCircleRadius[i]-buffer, capHeight))
            y1 = max(0, min(dropletCirclePosition[i][1]+dropletCircleRadius[i]+buffer, capHeight))
            x0 = max(0, min(dropletCirclePosition[i][0]-dropletCircleRadius[i]-buffer, capWidth))
            x1 = max(0, min(dropletCirclePosition[i][0]+dropletCircleRadius[i]+buffer, capWidth))
            crop_frame = frame[y0:y1, x0:x1]
            zoom = 1.2
            crop_frame = cv2.resize(crop_frame, (int((x1-x0)*zoom), int((y1-y0)*zoom)))
            cv2.imshow("Current Circle",crop_frame)

    # resize images for windows
    downscaled_frame = cv2.resize(frame, (windowWidth, windowHeight))
    downscaled_thresh_frame = cv2.resize(thresh_frame, (windowWidth, windowHeight))
    downscaled_thresh_frame = cv2.cvtColor(downscaled_thresh_frame, cv2.COLOR_GRAY2RGB)

    # display images on windows
    cv2.imshow(window1Name,downscaled_frame)
    cv2.imshow(window2Name,downscaled_thresh_frame)

    # break out of program on 'q' key
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('d'):
        mode = 'duplicate'
    elif key == ord('c'):
        mode = 'center'
    elif key == ord('r'):
        mode = 'radius'
    elif key == ord('-'):
        dropletCircleIndex = dropletCircleIndex - 1
        if dropletCircleIndex < 0:
            dropletCircleIndex = len(dropletCirclePosition) - 1
    elif key == ord('='):
        dropletCircleIndex = dropletCircleIndex + 1
        if dropletCircleIndex > len(dropletCirclePosition) - 1:
            dropletCircleIndex = 0
    elif key == ord('s'):
        text_file = open(videoFileFolder + videoFileName + "-circles.csv", "w")
        text_file.write("circle,x,y,radius\n")
        for i in range(len(dropletCirclePosition)):
            text_file.write(str(i) + "," +
                    str(dropletCirclePosition[i][0]) + "," +
                    str(dropletCirclePosition[i][1]) + "," +
                    str(dropletCircleRadius[i]) + "\n")
        text_file.close()

# clean up
cap.release()
cv2.destroyAllWindows()

