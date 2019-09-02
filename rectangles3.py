#!/usr/bin/env python

import numpy as np
import sys
import os
import cv2
import argparse 

parser = argparse.ArgumentParser(description='Get bounding box')

parser.add_argument('filename', type=str, nargs='?', default='Anglia/work/pg_0445.png', help='name of image-file')
#parser.add_argument('filename', type=str, nargs='?', default='pg_0666.png', help='name of image-file')

parser.add_argument('--seq', dest='seq', action='store_true', help='continue file number sequence')

args = parser.parse_args()
filepath = args.filename
filename = os.path.basename(filepath)

def outer_rectangle(img):
    cannied = cv2.Canny(img, threshold1=50, threshold2=200, apertureSize=7)
    return cv2.findContours(cannied, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

def all_rectangles(img):
    cannied = cv2.Canny(img, threshold1=50, threshold2=200, apertureSize=7)
    return cv2.findContours(cannied, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

def get_cut(img, p1, p2):    
    return img[p1[1]:p2[1], p1[0]:p2[0]]

def get_columns(img, minLen=8):
    cannied = cv2.Canny(img, threshold1=50, threshold2=200, apertureSize=7)
    return cv2.HoughLinesP(cannied, rho=1, theta=(np.pi / 180), threshold=280, minLineLength=minLen, maxLineGap=50)

def output(*u):
    print('"{}"'.format(','.join([str(i) for i in u])))

img = cv2.imread(filepath)
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

(h2, w2, _) = img.shape

_, thresh = cv2.threshold(grey, 250, 255, cv2.THRESH_BINARY)
contours, _ = outer_rectangle(thresh)

area = 0
m = 0
for i, contour in enumerate(contours):
    (x, y, w, h) = cv2.boundingRect(contour)
    a = (w - 1) * (h -1)
    if a > area:
        m = i
        area = a

(x1, y1, w1, h1) = cv2.boundingRect(contours[m])
y2 = y1 + h1 - 1
x4 = x1 + w1 - 1
#cv2.rectangle(img, (x1, y1), (x1 + w1 - 1, y2), BLUE, 2)
#cv2.imwrite('E.png', img)

if area < 1024:
    sys.stderr.write('ERROR rectangles3.py: can\'t match columns in "{}"\n'.format(filepath)) 
    sys.exit(1)

(x1, y1, w1, h1) = cv2.boundingRect(contours[m])
y2 = y1 + h1 + 1
x4 = x1 + w1 - 1

#cv2.rectangle(img, (x1, y1), (x1 + w1 - 1, y2), BLUE, 2)
#cv2.imwrite('A.png', img)

iout = get_cut(img, (0, y1 - 2), (w2, y2 + 2))
grey = get_cut(grey, (0, y1 - 2), (w2, y2 + 2))

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

grey = cv2.dilate(grey, kernel, iterations = 3)
#cv2.imwrite('B.png', grey)

contours, _ = outer_rectangle(grey)

area = 0
m = 0
for i, contour in enumerate(contours):
    (x, y, w, h) = cv2.boundingRect(contour)
    a = (w - 1) * (h -1)
    if a > area:
        m = i
        area = a

if area < 1024:
    sys.stderr.write('WARNING rectangles3.py: can\'t match columns in "{}"\n'.format(filepath))
    #cv2.imwrite('D.png', img)
    output(y1, x1, y2, x4)
    sys.exit(1)
        
(p1, q1, p2, q2) = cv2.boundingRect(contours[m])
x2 = p1
x3 = p1 + p2 - 1

#cv2.rectangle(img, (x2, y1), (x3, y2), GREEN, 2)
#cv2.imwrite('D.png', img)

output(y1, x1 - 1, y2, x2 + 1)
output(y1, x2 - 1, y2, x3 + 1)
output(y1, x3, y2, x4 + 1)
