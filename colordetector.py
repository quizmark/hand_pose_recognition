# import the necessary packages
import handy
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
from win32com.client import constants, Dispatch


# control pp
pp = Dispatch('Powerpoint.Application')
pp.Presentations.Open(FileName=r'pptest.pptx')
pp.ActivePresentation.SlideShowSettings.Run()
pp.SlideShowWindows(1).View.Last()
ns=pp.SlideShowWindows(1).View.Slide.SlideIndex
pp.SlideShowWindows(1).View.First()

# start cam
vs = VideoStream(src=0).start()
 
# allow the camera to warm up
time.sleep(1.0)

# distance of 2 pts
def dist(x,y):
    return np.sqrt((x[0]-y[0])*(x[0]-y[0])+(x[1]-y[1])*(x[1]-y[1]))    

# get hist
hist = handy.capture_histogram(vs)

# control pp slides values
n=1
dt=time.process_time()

if hist is not None:
    while True:
        # grab the current frame
        frame = vs.read()
        if frame is None:
            break
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (600, 600))
        
        # detect the hand
        hand = handy.detect_hand(frame, hist)

        # draw hand
        frame = hand.outline

        # get center
        center = hand.get_center_of_mass()
        cv2.circle(frame, center, 20, (255, 0, 0), -1)
        
        # draw fingertips
        numfinger = 0
        fingers = hand.fingertips
        if fingers:
            for finger in fingers:
                if dist(finger, center)>175 and finger[1]<center[1]:
                    cv2.circle(frame, finger, 5, (0, 0, 255), -1)
                    numfinger += 1
            
        if center:
            # control pp slides  
            if ((numfinger==1)or(numfinger==2)) and n<ns and time.process_time()-dt>2:
                pp.SlideShowWindows(1).View.Next()
                n+=1
                dt=time.process_time()
            elif ((numfinger==3)or(numfinger==4)) and n>1 and time.process_time()-dt>2:
                pp.SlideShowWindows(1).View.Previous()
                n-=1
                dt=time.process_time()              
     
        # show frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
     
        # press 'esc' to stop
        if key == 27:
            pp.SlideShowWindows(1).View.Exit()
            break                   
 
# stop cam
vs.stop() 
 
cv2.destroyAllWindows()
