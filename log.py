
import cv2
import numpy as np

import pyperclip

# function called by trackbar, sets the next frame to be read
def getFrame(frame_nr):
    global video
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_nr)

#  function called by trackbar, sets the speed of playback
def setSpeed(val):
    global playSpeed
    playSpeed = max(val,1)

# open video
video = cv2.VideoCapture("movie.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

print(fps)
# get total number of frames
nr_of_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
# create display window
cv2.namedWindow("Video")
cv2.namedWindow("Controls")
# set wait for each frame, determines playbackspeed
playSpeed = 1
# add trackbar
cv2.createTrackbar("Frame", "Controls", 0,nr_of_frames,getFrame)
cv2.createTrackbar("Speed", "Controls", playSpeed,100,setSpeed)

def nothing(x):
    pass

switch = '0 : OFF \n1 : ON'
cv2.createTrackbar(switch, 'Controls',0,1,nothing)

font = cv2.FONT_HERSHEY_SIMPLEX
org = (50, 50)
color = (255, 0, 0)
fontScale = 1
thickness = 2

#image = np.zeros((512,512,3), np.uint8)
#image = cv2.putText(image, 'Controls', org, font, 
#                   fontScale, color, thickness, cv2.LINE_AA)
#cv2.imshow('Controls', image) 

#drawing = False # true if mouse is pressed
#mode = True # if True, draw rectangle. Press 'm' to toggle to curve
#ix,iy = -1,-1


def draw_circle(event,x,y,flags,param):
    #global ix,iy,drawing,mode

    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        #drawing = True
        #ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        x = 5
        #if drawing == True:
        #    if mode == True:
        #        cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
        #    else:
        #        cv2.circle(img,(x,y),5,(0,0,255),-1)

    elif event == cv2.EVENT_LBUTTONUP:
        x = 5
        #drawing = False
        #if mode == True:
        #    cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
        #else:
        #    cv2.circle(img,(x,y),5,(0,0,255),-1)

img = np.zeros((512,512,3), np.uint8)
cv2.rectangle(img,(10,10),(50,50),(0,255,0),-1)
cv2.setMouseCallback('Controls',draw_circle)

def formatTimeAsString(time):
    timeSeconds = time[2]
    timeMinutes = time[2]
    timeMinutes = time[3]
    return "%02d:%02d"%(timeMinutes, timeSeconds)

times = []
def printTime(strType):
    currentFrameNum = video.get(cv2.CAP_PROP_POS_FRAMES)
    totalSeconds = int(currentFrameNum / fps)
    timeMinutes = int(totalSeconds / 60)
    timeSeconds = totalSeconds - timeMinutes * 60
    times.append([totalSeconds, timeMinutes, timeSeconds, strType])

def copyToClipboard():
    finalStr = 'total time (seconds),time (minutes),time (seconds)\r\n'
    for i in range(len(times)):
        time = times[i]
        for j in range(len(time)):
            col = time[j]
            finalStr += str(col) + ','
        finalStr += '\r\n'
    pyperclip.copy(finalStr)

# main loop
count = 0
skip = 100
while True:
    # Get the next videoframe
    ret, frame = video.read()

    # show frame, break the loop if no frame is found
    if ret:
        scale_percent = 60 # percent of original size
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        
        # resize image
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        cv2.imshow("Video", resized)
    else:
        break

    # display frame for 'playSpeed' ms, detect key input
    key = cv2.waitKey(playSpeed)

    # stop playback when q is pressed
    if key == ord('q'):
        break
    if key == ord('i'):
        printTime('in')
    if key == ord('o'):
        printTime('out')
    if key == ord('c'):
        copyToClipboard()

    # update slider position on trackbar
    # NOTE: this is an expensive operation, remove to greatly increase max playback speed
    if count % skip == 0:
        cv2.setTrackbarPos("Frame","Controls", int(video.get(cv2.CAP_PROP_POS_FRAMES)))
    
    count += 1

# release resources
video.release()
cv2.destroyAllWindows()