import numpy as np
import cv2
import sys
from win32api import GetSystemMetrics
import math

# get screen properties
screenXPositionOffset = -13
screenWidthOffset = 10
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
dropletCirclePosition = (20,20)
dropletCircleRadius = 20
dropletCircleColor = (0, 0, 255)

isButtonDown = False

"""
def getDropletCircleRadius(x, y):
    global dropletCirclePosition, dropletCircleRadius
    diffX = dropletCirclePosition[0] - x
    diffY = dropletCirclePosition[1] - y
    dropletCircleRadius = int(math.sqrt(diffX**2 + diffY**2))

def click_and_crop(event, x, y, flags, param):
    global dropletCirclePosition, dropletCircleRadius, isButtonDown
    if event == cv2.EVENT_LBUTTONDOWN:
        dropletCirclePosition = (x, y)
        isButtonDown = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if isButtonDown == True:
            getDropletCircleRadius(x,y)
    elif event == cv2.EVENT_LBUTTONUP:
        isButtonDown = False
        getDropletCircleRadius(x,y)
cv2.setMouseCallback(window1Name, click_and_crop)
"""

points = []
def recalculatePosition():
    global dropletCirclePosition, points
    x = 0
    y = 0
    for point in points:
        x = x + point[0]
        y = y + point[1]
    x = x / len(points)
    y = y / len(points)
    dropletCirclePosition = (int(x),int(y))

def recalculateRadius():
    global dropletCirclePosition, dropletCircleRadius, points
    x = 0
    y = 0
    for point in points:
        x = x + abs(point[0] - dropletCirclePosition[0])
        y = y + abs(point[1] - dropletCirclePosition[1])
    x = x / len(points)
    y = y / len(points)
    dropletCircleRadius = int(math.sqrt(x**2+y**2))

def click_and_crop(event, x, y, flags, param):
    global points, isButtonDown
    if event == cv2.EVENT_LBUTTONDOWN:
        isButtonDown = True
        points.append((x,y))
        recalculatePosition()
        recalculateRadius()
    elif event == cv2.EVENT_MOUSEMOVE:
        if isButtonDown == True:
            points.append((x,y))
            recalculatePosition()
            recalculateRadius()
    elif event == cv2.EVENT_LBUTTONUP:
        isButtonDown = False

cv2.setMouseCallback(window1Name, click_and_crop)

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

    cv2.circle(frame, dropletCirclePosition, dropletCircleRadius, dropletCircleColor, boundingRectThickness)

    # display images on windows
    cv2.imshow(window1Name,frame)
    cv2.imshow(window2Name,thresh_frame)

    # break out of program on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# clean up
cap.release()
cv2.destroyAllWindows()

