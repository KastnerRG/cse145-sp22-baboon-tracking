import cv2
import numpy as np
import math
import cmath
import skimage
import time
import multiprocessing
import sys

from collections import deque
from registration import register

from foreground_extraction import *
from blob_detection import *

from config import *

def main():
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    cap = cv2.VideoCapture(INPUT_MASK)

    # Check if camera opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
        sys.exit()

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter(OUTPUT_MASK_BLOB_DETECTION, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=cpus)

    start = time.clock()
    # Read until video is completed
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            moving_foreground = gray

            moving_foreground = remove_noise(moving_foreground)
            frame_with_detected_blobs = detect_blobs(moving_foreground, frame)

            # Display the resulting frame
            cv2.imshow('moving_foreground', cv2.resize(moving_foreground, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            cv2.imshow('detected_blobs', cv2.resize(frame_with_detected_blobs, (DISPLAY_WIDTH, DISPLAY_HEIGHT)))
            #out.write(cv2.cvtColor(moving_foreground, cv2.COLOR_GRAY2BGR))

            # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        # Break the loop
        else:
            break

    # When everything done, release the video capture object
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
