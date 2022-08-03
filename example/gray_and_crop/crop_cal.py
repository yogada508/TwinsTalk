import os
import time
import cv2
import time
from numpy import save
import sys

def save_byte_file(b, videoName):
    with open(videoName, "wb") as f:
        f.write(b)

def rescale_frame(frame_input, percent=10):
    width = int(frame_input.shape[1] * percent / 100)
    height = int(frame_input.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame_input, dim, interpolation=cv2.INTER_AREA)

def crop(videoData):
    tmp_file = f"tmp_{time.time()}.mp4"
    output_file = f"tmp_{time.time()}.mp4"
    save_byte_file(videoData, tmp_file)
    
    cap = cv2.VideoCapture(tmp_file)
    ret, frame = cap.read()
    rescaled_frame = rescale_frame(frame)
    (h, w) = rescaled_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_file, fourcc, 30.0, (w, h), True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rescaled_frame = rescale_frame(frame)
        writer.write(rescaled_frame)

    cv2.destroyAllWindows()
    cap.release()
    writer.release()

    f = open(output_file, "rb")
    output = f.read()

    os.remove(tmp_file)
    os.remove(output_file)

    print("got crop output", sys.getsizeof(output))

    return output

# if __name__ == '__main__':
#     o = crop("hello.mp4", open("input_video.mp4", "rb").read())
#     with open("result.mp4", "wb") as f:
#         f.write(o)