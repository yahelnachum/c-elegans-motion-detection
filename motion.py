import numpy as np
import cv2
import sys
from win32api import GetSystemMetrics
import math
import re

# get screen properties
screenWidth = GetSystemMetrics(0)
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

cv2.moveWindow(window1Name, 0, 0);
cv2.moveWindow(window2Name, windowWidth, 0);

# general image processing properties
# (blur, threshold, contours)
blur = (11, 11)
threshold = 10
contourAreaMin = 10
boundingRectColor = (0, 255, 0)
boundingRectThickness = 3

# initial droplet properties
dropletCirclePosition = [(100,100)]
dropletCircleRadius = [100]
dropletCircleIndex=0
cv2.namedWindow("Current Circle",cv2.WINDOW_NORMAL)
cv2.moveWindow("Current Circle", 0, windowHeight);
cv2.resizeWindow("Current Circle", 250, 250)

# pythagorean theorem to get radius of circle
def getDropletCircleRadius(x0, y0):
    global dropletCirclePosition, dropletCircleRadius

    # normalize for windows scaling
    x0 = x0 / downscaled_factor
    y0 = y0 / downscaled_factor

    x1 = dropletCirclePosition[dropletCircleIndex][0]
    y1 = dropletCirclePosition[dropletCircleIndex][1]

    xLen = x0 - x1
    yLen = y0 - y1
    radius = int(math.sqrt(xLen**2 + yLen**2))
    dropletCircleRadius[dropletCircleIndex] = radius

# initial program mode
# center: changes position of current circle
# radius: changes radius of current circle
# duplicate: creates a duplicate of the current circle
mode='center'
def click(event, x, y, flags, param):
    global mode, dropletCirclePosition, dropletCircleRadius, isButtonDown, dropletCircleIndex
    if event == cv2.EVENT_LBUTTONDOWN:
        if mode == 'duplicate':
            dropletCirclePosition.append((int(x/downscaled_factor),int(y/downscaled_factor)))
            dropletCircleRadius.append(dropletCircleRadius[dropletCircleIndex])
            dropletCircleIndex = len(dropletCirclePosition) - 1
        if mode == 'center':
            dropletCirclePosition[dropletCircleIndex] = (int(x/downscaled_factor),int(y/downscaled_factor))
        if mode == 'radius':
            getDropletCircleRadius(x,y)
cv2.setMouseCallback(window1Name, click)

# circle display properties
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 2
lineType = 2

stillImageTempCounter = 200
stillImageTempTotal = stillImageTempCounter
stillImageTemp = np.empty((0,0))
stillImage = None
while(cap.isOpened()):
    ret, frame = cap.read()

    if not(ret):
        break

    # turn image to grayscale and blur it
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, blur, 0)

    # take first frame as the background
    if stillImageTempCounter > 0:
        if not(stillImageTemp.any()):
            stillImageTemp = gray / stillImageTempTotal
        else:
            stillImageTemp = stillImageTemp + gray / stillImageTempTotal
        stillImageTempCounter = stillImageTempCounter - 1

    if stillImageTempCounter == 0:
        stillImage = stillImageTemp.astype(np.uint8)
        stillImageTempCounter = stillImageTempCounter - 1
    elif stillImageTempCounter > 0:
        stillImage = gray

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

    # draw circles on frame
    for i in range(len(dropletCirclePosition)):

        # get general properties of circle
        pos = dropletCirclePosition[i]
        x = pos[0]
        y = pos[1]
        r = dropletCircleRadius[i]

        # decide color by current circle's mode
        colorCenter = (255, 255, 255)
        colorRadius = (255, 255, 255)
        fontColor = (255,255,255)
        if i == dropletCircleIndex:
            fontColor = (0,0,255)
            if mode == 'center':
                colorCenter = (0, 0, 255)
            if mode == 'radius':
                colorRadius = (0, 0, 255)
            if mode == 'duplicate':
                colorCenter = (255, 0, 0)
                colorRadius = (255, 0, 0)

        # draw circle (radius, center, label)
        cv2.circle(frame, pos, r, colorRadius, boundingRectThickness)
        cv2.circle(frame, pos, 10, colorCenter, boundingRectThickness)
        cv2.putText(frame, str(i), (x + 10, y - 10), font, fontScale, fontColor, lineType)

        # display current circle in separate, zoomed in window
        if i == dropletCircleIndex:
            buffer = r
            x0 = max(0, x - r - buffer)
            x1 = min(   x + r + buffer, capWidth)
            y0 = max(0, y - r - buffer)
            y1 = min(   y + r + buffer, capHeight)
            crop_frame = frame[y0:y1, x0:x1]
            cv2.imshow("Current Circle",crop_frame)
            cv2.resizeWindow("Current Circle", (x1-x0), (y1-y0))

    # resize images for windows
    downscaled_frame = cv2.resize(frame, (windowWidth, windowHeight))
    downscaled_thresh_frame = cv2.resize(thresh_frame, (windowWidth, windowHeight))
    downscaled_thresh_frame = cv2.cvtColor(downscaled_thresh_frame, cv2.COLOR_GRAY2RGB)

    # display images on windows
    cv2.imshow(window1Name,downscaled_frame)
    cv2.imshow(window2Name,downscaled_thresh_frame)

    key = cv2.waitKey(1) & 0xFF
    # break out of program on 'q' key
    if key == ord('q'):
        break

    # set different circle modes
    elif key == ord('d'):
        mode = 'duplicate'
    elif key == ord('c'):
        mode = 'center'
    elif key == ord('r'):
        mode = 'radius'

    # switch between circles
    elif key == ord('-'):
        dropletCircleIndex = dropletCircleIndex - 1
        if dropletCircleIndex < 0:
            dropletCircleIndex = len(dropletCirclePosition) - 1
    elif key == ord('='):
        dropletCircleIndex = dropletCircleIndex + 1
        if dropletCircleIndex > len(dropletCirclePosition) - 1:
            dropletCircleIndex = 0

    # save circles to file
    elif key == ord('s'):
        circleFile = open(videoFileFolder + videoFileName + "-circles.csv", "w")
        circleFile.write("circle,x,y,radius\n")
        for i in range(len(dropletCirclePosition)):
            circleFile.write(str(i) + "," +
                    str(dropletCirclePosition[i][0]) + "," +
                    str(dropletCirclePosition[i][1]) + "," +
                    str(dropletCircleRadius[i]) + "\n")
        circleFile.close()

# clean up
cap.release()
cv2.destroyAllWindows()

