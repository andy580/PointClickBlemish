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

# Displaying Window     
windowName = "Blemish Remover"
cv2.namedWindow(windowName, cv2.WINDOW_AUTOSIZE)
cv2.imshow(windowName, image)


while True:
    c = cv2.waitKey(100)
    if c ==27:
        break
cv2.destroyAllWindows()