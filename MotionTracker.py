#!/usr/bin/env python

import cv
from math import sqrt
from random import randint
from ServerConnection import *

# boolean to send data to server or not
CONNECT_TO_SERVER = True
DEBUG = True
ROI_X_POS = 0
ROI_Y_POS = 0
ROI_WIDTH = 640
ROI_HEIGHT = 480


class Target:

    def __init__(self):
        self.capture = cv.CaptureFromCAM(0)
        if DEBUG:
            cv.NamedWindow("Target", 1)
        # set camera resolution
        cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
        cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
        
        # create a connection to the server
        if CONNECT_TO_SERVER:
            self.server = ServerConnection('localhost', 8887)
            self.server.send_resolution(ROI_WIDTH, ROI_HEIGHT)
    

    def run(self):
        # Capture first frame to get size
        frame = cv.QueryFrame(self.capture)
        cv.SetImageROI(frame, (ROI_X_POS, ROI_Y_POS, ROI_WIDTH, ROI_HEIGHT) )
        frame_size = cv.GetSize(frame)
        color_image = cv.CreateImage(cv.GetSize(frame), 8, 3)
        grey_image = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
        moving_average = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_32F, 3)
        
        THRESHOLD = 70
        
        particles = []

        first = True

        while True:
            #get a frame to work with
            color_image = cv.QueryFrame(self.capture)
            
            # Set an ROI so that we can cut the tree branches from the FOV
            cv.SetImageROI(color_image, (ROI_X_POS, ROI_Y_POS, ROI_WIDTH, ROI_HEIGHT) )

            # Smooth to get rid of false positives
            cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

            if first:
                difference = cv.CloneImage(color_image)
                temp = cv.CloneImage(color_image)
                cv.ConvertScale(color_image, moving_average, 1.0, 0.0)
                first = False
            else:
                cv.RunningAvg(color_image, moving_average, 0.020, None)

            # Convert the scale of the moving average.
            cv.ConvertScale(moving_average, temp, 1.0, 0.0)

            # Minus the current frame from the moving average.
            cv.AbsDiff(color_image, temp, difference)

            # Convert the image to grayscale.
            cv.CvtColor(difference, grey_image, cv.CV_RGB2GRAY)

            # Convert the image to black and white.
            cv.Threshold(grey_image, grey_image, THRESHOLD, 255, cv.CV_THRESH_BINARY)

            # Dilate and erode to get people blobs
            cv.Dilate(grey_image, grey_image, None, 18)
            cv.Erode(grey_image, grey_image, None, 10)
            
            #get the contours (segmented objects)
            storage = cv.CreateMemStorage(0)
            contour = cv.FindContours(grey_image, storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE)
            
            if DEBUG:
                cv.DrawContours(color_image, contour, cv.CV_RGB(255,0,0), cv.CV_RGB(0,255,0), 9, cv.CV_FILLED)
            
            centroids = []
            
            while contour:
                #get the bounding box
                bound_rect = cv.BoundingRect(list(contour))
                #assume the centre of the box is the centre of the blob (roughly true)
                centroids.append((bound_rect[0] + bound_rect[2] /2, bound_rect[1] + bound_rect[3] /2))
                contour = contour.h_next()
                
            if DEBUG:
                for i in centroids:
                    #each new centroid is an array of:
                    centroid = []
                    centroid.append(i) #the point
                    centroid.append(1) #the life
                    
                    shortest_distance = 100
                    for j in centroids:
                        if i != j:
                            if self.calculateDistance(i,j) < shortest_distance:
                                shortest_distance = self.calculateDistance(i,j)
                    colour = self.chooseColour(shortest_distance) 
                    
                    centroid.append(colour) #and the colour based on distance
                    particles.append(centroid) #and gets added to our list of particles
                
                    #cv.Circle(color_image, i, 10, self.chooseColour(), 30)
             
            #now that we have these nice coloured particles    
            """
            for i in particles:
                #if they aren't too old, draw them
                if i[1] < 20:
                    cv.Circle(color_image, i[0], i[1], i[2], -1)
                    i[1] += 2 #and age them
                else:
                    #otherwise kill them
                    particles.remove(i)
            """
            # send latest data to server
            if CONNECT_TO_SERVER:
                self.server.send_points(centroids)
            
            if DEBUG: # only show window when we are debugging
                cv.ShowImage("Target", color_image)
            

            # Listen for ESC key
            c = cv.WaitKey(10) % 0x100
            if c == 27:
                break
            # For adjustable thresholding based on ambient contrast
            elif c == 171:
                if THRESHOLD < 255:
                    THRESHOLD += 10
                else:
                    THRESHOLD = 255
            elif c == 173:
                if THRESHOLD > 0:
                    THRESHOLD -= 10
                else:
                    THRESHOLD = 0


    def calculateDistance(self, position_a, position_b):
        dist = sqrt( (position_b[0] - position_b[0])**2 + (position_b[1] - position_a[1])**2 )
        return dist
                
    def chooseColour(self, distance):
#        red = 255
#        green = 255
#        blue = 255
#        red = randint(0,255)
#        green = randint(0,255)
#        blue = randint(0,255)
#        red = 255 - randint(distance *2 - 30, distance *2 +30)
#        blue = 0 + randint(distance *2 - 30, distance *2 +30)
#        green = 0 + (randint(distance *2 - 30, distance *2 +30))
        red = 255 - (distance * 2)
        green = 0 + (distance * 2)
        blue = 0 + (distance * 2)
        return cv.CV_RGB(red, green, blue)
        

if __name__=="__main__":
    t = Target()
    t.run()
