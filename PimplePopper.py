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


# Function to select and replace skin patch
def blemishRemover(action, x, y, flags, userdata):
    # Selecting blemish: set temporary patch to 16x16 pixels
    if action == cv2.EVENT_LBUTTONDOWN:
        blemish = image[y-8:y+8, x-8:x+8].copy()
        blemish = cv2.cvtColor(blemish, cv2.COLOR_BGR2GRAY)
        
        distFromBlemish = 20

        # Boundary array used to compare adjacent skin patches
        boundary = np.zeros((16,16))
        boundary[:,0] = boundary[0,:] = boundary[:,-1] = boundary[-1,:] = 1
        boundary = np.uint8(boundary)

        # Look for adjacent skin patches to replace blemish
        # Adjacent skin patch with the most similar boundary selected
        for theta in range(0, 360, 90):
            xoff = int(distFromBlemish * math.cos(np.deg2rad(theta)))+x
            yoff = int(distFromBlemish * math.sin(np.deg2rad(theta)))+y

            blemishBoundary = image[yoff-8:yoff+8, xoff-8:xoff+8].copy()
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


# Displaying Window     
windowName = "Blemish Remover"
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
cv2.imshow(windowName, image)
cv2.setMouseCallback(windowName, blemishRemover)


while True:
    c = cv2.waitKey(100)
    if c ==27:
        break
cv2.destroyAllWindows()