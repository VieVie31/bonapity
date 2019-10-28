import os
import time
import glob
import json
import base64

import cv2
import numpy as np

from io import BytesIO

from PIL import Image
from tqdm import tqdm
from bonapity import bonapity

OUT_FACES_SIZE = (128, 128)

detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def extract_face(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(img, 1.3, 5)
    # Take the bigest face : 
    indices_by_size = np.array([w * h for (_, _, w, h) in faces]).argsort()
    if not len(faces):
        raise ValueError("No face found !")
    (x, y, w, h) = faces[indices_by_size[-1]]
    return cv2.resize(img[y:y + h, x:x + w], OUT_FACES_SIZE)


@bonapity(json_encoder=None)
def process_face(base64_string):
    base64_string = base64_string.split("base64,")[1]

    # Load image from base64
    sbuf = BytesIO()
    sbuf.write(base64.b64decode(base64_string))
    pimg = Image.open(sbuf)
    img = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

    # Extract the main face
    face = extract_face(img)

    # Convert extracted face into base64 (the hard part…)
    img = Image.fromarray(face, 'L')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    img_str = bytes("data:image/jpeg;base64,", encoding='utf-8') + img_str
    return img_str.decode()





if __name__ == "__main__":
    bonapity.serve(port=1234, index="upload.html")

