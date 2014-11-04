#!/usr/bin/env python
import sys
sys.path.append('C:\opencv248\sources\samples\python2')
import numpy as np
import cv2
import video
import math
import time

help_message = '''
USAGE: opt_flow.py [<video_source>]
'''

OVERIMAGE = '../img/disp.png'
MASKIMAGE = '../img/mask.png'
WINNAME = 'kane_tsuki'
RESIZE_RATE = 2

# draw motion flow image
def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2 , 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis

class settingRoi:
    def __init__(self):
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0
        
    def showSettingWindow(self, img):
        green = (0, 255, 0)
        cv2.line(img, (self.left, self.top), (self.left, self.bottom), green)
        cv2.line(img, (self.left, self.bottom), (self.right, self.bottom), green)
        cv2.line(img, (self.right, self.bottom), (self.right, self.top), green)
        cv2.line(img, (self.right, self.top), (self.left, self.top), green)
        cv2.imshow('set', img)

    def mouseCall(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            ret, img = params.read()
            self.left = x
            self.top = y
            self.showSettingWindow(img)
        if event == cv2.EVENT_RBUTTONDOWN:
            ret, img = params.read()
            self.right = x
            self.bottom = y
            self.showSettingWindow(img)
        
    def setRoi(self, cam):
        ret, img = cam.read()
        cv2.imshow('set', img)
        cv2.moveWindow('set', 0, 0)
                   
        shape = img.shape
        self.right = shape[1] - 1
        self.bottom = shape[0] - 1
        self.showSettingWindow(img)
        
        cv2.setMouseCallback('set', self.mouseCall, cam)

        while True:
            ret, img = cam.read()
            self.showSettingWindow(img)
            ch = 0xFF & cv2.waitKey(5)
            if ch == 27:
                 break
            cv2.waitKey(5)

        cv2.destroyWindow('set')
        return self.left, self.top, self.right, self.bottom

# display a masking overImg on a camera image
def dispHitImage(cam, overImg, maskImg, fgImg):
    ret, img = cam.read()
    shape = (img.shape[1] * RESIZE_RATE, img.shape[0] * RESIZE_RATE)

    sTime = time.time()
    while True:
        bgImg = cv2.bitwise_and(img ,img ,mask = maskImg)
        addImg = cv2.add(bgImg, fgImg)
        cv2.imshow(WINNAME, cv2.resize(addImg, shape, interpolation = cv2.INTER_LINEAR))
        
        if (time.time() - sTime > 2.0):
            break
        ret, img = cam.read()
        
        cv2.waitKey(5)
        
if __name__ == '__main__':
    import sys
    print help_message
    try: fn = sys.argv[1]
    except: fn = 0

    cam = video.create_capture(fn)
    
    se = settingRoi()
    left, top, right, bottom = se.setRoi(cam)
    width = right - left + 1
    height = bottom - top + 1
    area = width * height
    if (width < 1 or height < 1):
        exit()
    
    ret, read = cam.read()
    prevClip = read[top:bottom, left:right]   
    prevClip = cv2.cvtColor(prevClip, cv2.COLOR_BGR2GRAY)

    # create mask image and overlay image
    shape = (read.shape[1], read.shape[0])
    overImg = cv2.imread(OVERIMAGE)
    maskImg = cv2.imread(MASKIMAGE, cv2.IMREAD_GRAYSCALE)
    overImg = cv2.resize(overImg, shape)
    maskImg = cv2.resize(maskImg, shape)
    maskInv = cv2.bitwise_not(maskImg)
    fgImg = cv2.bitwise_and(overImg, overImg ,mask = maskInv)

    shape = (shape[0] * RESIZE_RATE, shape[1] * RESIZE_RATE)
    
    cv2.imshow(WINNAME, cv2.resize(read, shape))
    cv2.moveWindow(WINNAME, 0, 0)
     
    while True:
        ret, read = cam.read()
        gray = cv2.cvtColor(read, cv2.COLOR_BGR2GRAY)
        grayClip = gray[top:bottom, left:right]
        flow = cv2.calcOpticalFlowFarneback(prevClip, grayClip, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevClip = grayClip

        def isMoving():
            integral = cv2.integral(flow)
            totalFlow = integral[height - 1, width - 1]
        
            totalFlow = totalFlow / area
            norm = totalFlow[0] * totalFlow[0] + totalFlow[1] * totalFlow[1]
            norm = math.sqrt(norm) + 1.0 # 1.0 : relaxation parameter
            totalFlow = totalFlow / norm
            if (totalFlow[0] > 0.5):
                return True
            return False
        
        if (isMoving()):
            dispHitImage(cam, overImg, maskImg, fgImg)
        else:
            cv2.imshow(WINNAME, cv2.resize(read, shape))

        cv2.imshow('flow', draw_flow(grayClip, flow))

        ch = 0xFF & cv2.waitKey(2)
        if ch == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
