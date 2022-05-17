# Modules should have short, all-lowercase names.
# Underscores can be used in the module name if it improves readability. 

import cv2
import numpy as np
import base64
import uuid

def get_mac_address() -> str:

    return '{:02x}'.format(uuid.getnode())

# @data: bytes data
# deocde bytes data from base64 to opencv mat
def decode_image(data):

    b64d = base64.b64decode(data)
    dBuf = np.frombuffer(b64d, dtype = np.uint8)
    dst = cv2.imdecode(dBuf, cv2.IMREAD_COLOR)
    return dst

# @image: opencv mat
# encode opencv mat into base64 bytes
def encode_image(image):

    ret, buf = cv2.imencode('.jpg', image)
    if ret != 1:
        return None

    b64e = base64.b64encode(buf)
    return b64e

def yolo_results_to_json(results):
    pass
