import cv2
import pytesseract as pyt
import re
from ctpn.demo_pb import get_coords
import numpy as np
import tensorflow as tf
from skimage.filters import threshold_local


def preprocess_img(image_path, new_path):

    image =cv2.imread(image_path)
    warped = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    T = threshold_local(warped, 31, offset = 11, method = "gaussian")
    warped = (warped > T).astype("uint8") * 255

    cv2.imwrite(new_path, warped)

# function to recognise text from image
def recognise_text(image_path, photo_path, orig_path, sign = ""):
    
    # read image and convert to grayscale
    image = cv2.imread(image_path, 0)

    # get coordinates of text using ctpn
    coordinates = get_coords(image_path)

    detected_text = []

    # sorting coordinates from top to bottom
    coordinates = sorted(coordinates, key = lambda coords: coords[1])
    
    # looping through all the text boxes
    for coords in coordinates:
        # x, y, width, height of the text box
        x, y, w, h = coords

        # cropping image based on the coordinates
        temp = image[y:h, x:w]

        # padding the image with 10 pixels for better prediction with tesseract
        thresh = cv2.copyMakeBorder(temp, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        
        # get text from the image, lang = english, config = use lstm for prediction
        text = pyt.image_to_string(thresh, lang="eng", config=('--oem 1 --psm 3'))
        
        # clean text and remove noise
        text = clean_text(text)

        if "signa" in text.lower():
            get_sign(image_path, sign, x, y, w, h)
        # ignore text if the length of text is less than 3 as it would only be noise
        if len(text) < 3:
            continue
        detected_text.append(text)

    # find face in the image
    face, found = get_photo(orig_path)

    # if a face is found save it to faces directory
    if found:
        cv2.imwrite(photo_path, face)
    else:
        photo_path = face
    
    # return detected text and the face path
    return detected_text, photo_path


# function to remove noise and unnecessary characters from string
def clean_text(text):
    if text != ' ' or text != '  ' or text != '':
        text = re.sub('[^A-Za-z0-9-/,.() ]+', '', text)
        text = text.strip()
        text = re.sub(r'\s{2,}', ' ', text) 
        
    return text

# function to find face in the image
def get_photo(image_path):

    image = cv2.imread(image_path)

    # Image Should be 1920 x 1080 pixels
    scale_factor = 1.1
    min_neighbors = 3
    min_size = (150, 150)
    flags = cv2.CASCADE_SCALE_IMAGE

    # using frontal face haar cascade
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # detect faces of different sizes
    faces = face_cascade.detectMultiScale(image, scaleFactor = scale_factor, minNeighbors = min_neighbors,
                                          minSize = min_size, flags = flags)
    
    # crop the face if found
    try:
        x, y, w, h = faces[0]
        face = image[y-50:y+h+40, x-10:x+w+10]
        return face, True
    except Exception as _:
        return "Photo not found!", False

# function to crop the signature
def get_sign(image, filename, xmin, ymin, xmax, ymax):
    img = cv2.imread(image)
    width = abs(xmin - xmax)
    height = abs(ymin - ymax)

    x1 = int(xmin - (0.17*width))
    x2 = int(xmax + (0.17*width))

    y1 = int(ymin - (2*height))
    y2 = ymin

    signature = img[y1:y2, x1:x2]

    cv2.imwrite(filename, signature)