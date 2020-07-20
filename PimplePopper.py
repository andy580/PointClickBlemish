import cv2
import math
import numpy as np
import tkinter

# Prevents root window from opening after file is selected
from tkinter import Tk
root = Tk()
root.withdraw()
# Select image to remove blemish
from tkinter.filedialog import askopenfilename
filename = askopenfilename()
 
image = cv2.imread(filename)
output = image.copy()


def sizeChange(*args):
    global pimpleSize
    pimpleSize = args[0]

# Function to select and replace skin patch
def blemishRemover(action, x, y, flags, userdata):
    global image
    global output
    global pimpleSize

    # View bounding box to remove blemish
    tempImage = image.copy()
    cv2.rectangle(tempImage, ((x-pimpleSize),(y-pimpleSize)),((x+pimpleSize),y+pimpleSize), (255,255,255), 2)
    cv2.imshow(windowName, tempImage)

    # Selecting blemish: set temporary patch to 16x16 pixels
    if action == cv2.EVENT_LBUTTONDOWN:
        blemish = image[y-pimpleSize:y+pimpleSize, x-pimpleSize:x+pimpleSize].copy()
        blemish = cv2.cvtColor(blemish, cv2.COLOR_BGR2GRAY)
        
        distFromBlemish = 20
        boundaryDict = {}
        smoothnessDict = {}
        optimalDict = {}

        # Boundary array used to compare adjacent skin patches
        boundary = np.zeros((2*pimpleSize,2*pimpleSize))
        boundary[:,0] = boundary[0,:] = boundary[:,-1] = boundary[-1,:] = 1
        boundary = np.uint8(boundary)

        # Look for adjacent skin patches to replace blemish
        # Adjacent skin patch with the most similar boundary selected
        for theta in range(0, 360, 5):
            xoff = int(distFromBlemish * math.cos(np.deg2rad(theta)))+x
            yoff = int(distFromBlemish * math.sin(np.deg2rad(theta)))+y

            blemishBoundary = image[yoff-pimpleSize:yoff+pimpleSize, xoff-pimpleSize:xoff+pimpleSize].copy()
            blemishBoundary = cv2.cvtColor(blemishBoundary, cv2.COLOR_BGR2GRAY)

            # Retrieving boundaries of adjacent skin patch
            adjBlemishBoundary = blemishBoundary * boundary
            blemishBoundary = blemish * boundary

            boundaryDiff = abs(adjBlemishBoundary - blemishBoundary)
            boundaryDiff = boundaryDiff.flatten()
            boundaryDiffSum = sum(boundaryDiff)

            #Retrieving smoothness of adjacent skin patches
            sobelx = cv2.Sobel(blemish, cv2.CV_32F, 1,0)
            sobely = cv2.Sobel(blemish, cv2.CV_32F, 0,1)
            sobel2 = abs(np.mean(sobelx)+np.mean(sobely))

            # Store values to dictionaries
            boundaryDict[theta] = boundaryDiffSum
            smoothnessDict[theta] = sobel2

        # get max value of each dictionary
        maxBoundary = max(boundaryDict.values())
        maxSmoothness = max(smoothnessDict.values())
        alpha = 0.8
        for theta in boundaryDict.keys(): 
            optimalDict[theta] = alpha*boundaryDict[theta]/maxBoundary + (1-alpha)*smoothnessDict[theta]/maxSmoothness
        optimalTheta = min(optimalDict, key=optimalDict.get)    

        # Seamlessly clone best skin patch onto blemish
        xoff = int(distFromBlemish * math.cos(np.deg2rad(optimalTheta)))+x
        yoff = int(distFromBlemish * math.sin(np.deg2rad(optimalTheta)))+y
        bestSkinPatch = image[yoff-pimpleSize:yoff+pimpleSize, xoff-pimpleSize:xoff+pimpleSize].copy()

        # mask = np.ones(bestSkinPatch.shape[0:2], bestSkinPatch.dtype)*255
        mask = np.ones((2*pimpleSize,2*pimpleSize), float)
        # print(mask)
        for i in range(5,-1,-1):
            mask[:,i] = mask[i,:] = mask[:,-(i+1)] = mask[-(i+1),:] = (i/5)
            
        maskInv = 1-mask
        patch = image[y-pimpleSize:y+pimpleSize, x-pimpleSize:x+pimpleSize]
        
        mask = cv2.merge((mask,mask,mask))
        maskInv = cv2.merge((maskInv,maskInv,maskInv))

        bestSkinPatch = np.uint8(bestSkinPatch*mask)
        patch = np.uint8(patch*maskInv)
        
        outputPatch = bestSkinPatch + patch

        output = cv2.addWeighted(image[y-pimpleSize:y+pimpleSize, x-pimpleSize:x+pimpleSize],0.3, outputPatch,0.7,0.0)
        image[y-pimpleSize:y+pimpleSize, x-pimpleSize:x+pimpleSize] = output
        cv2.medianBlur(image[y-20:y+20, x-20:x+20],5)

        cv2.imshow(windowName, image)

# Creating trackbar for window
windowName = "Blemish Remover"
maxSize = 100
trackbarValue = "Size"
pimpleSize = 8


# Displaying Window     
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.imshow(windowName, image)
# cv2.imshow("output", bestSkinPatch)
cv2.setMouseCallback(windowName, blemishRemover)
cv2.createTrackbar(trackbarValue, windowName, pimpleSize, maxSize, sizeChange)


while True:
    c = cv2.waitKey(100)
    if c ==27:
        break
cv2.destroyAllWindows()