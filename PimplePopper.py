import cv2
import math
import numpy as np

image = cv2.imread("blemish.png")

# Displaying Window     
windowName = "Blemish Remover"
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
cv2.imshow(windowName, image)

while True:
    c = cv2.waitKey(100)
    if c ==27:
        break
cv2.destroyAllWindows();