import cv2
import numpy as np
import base64
import os
import time
import sys

def save_byte_file(b, videoName):
    with open(videoName, "wb") as f:
        f.write(b)

def gray(videoName, videoData):
    tmp_file_name = f"tmp_{time.time()}_{videoName}"
    save_byte_file(videoData, tmp_file_name)
    
    cap = cv2.VideoCapture(tmp_file_name)
    output_file_name = f"tmp_{time.time()}_{videoName}"
    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
    size = (frame_width, frame_height)
    
    out = cv2.VideoWriter(output_file_name, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, size, 0)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out.write(gray_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    f = open(output_file_name, "rb")
    output = f.read()

    os.remove(tmp_file_name)
    os.remove(output_file_name)

    print("got gray output", sys.getsizeof(output))

    return output
