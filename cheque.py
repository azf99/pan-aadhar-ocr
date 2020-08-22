## All neccessary imports ##
import cv2
import re
import imutils
import numpy as np
import pytesseract as pyt
from imutils import contours
from skimage.segmentation import clear_border
from skimage.filters import threshold_local


def crop_transform(img):
    ratio = img.shape[0] / 500.0
    #img = cv2.resize(img,(500,500))
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(gray,127,255,0)
    #thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,11)
    contours = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:5]

    for cnt in contours:
        if cv2.contourArea(cnt)>50000:  # remove small areas like noise etc
            hull = cv2.convexHull(cnt)    # find the convex hull of contour
            hull = cv2.approxPolyDP(hull,0.1*cv2.arcLength(hull,True),True)
            if len(hull)==4:
                #cv2.drawContours(img,[hull],0,(0,255,0),3)
                
                x, y, w, h = cv2.boundingRect(cnt)
                
                warped = img[y:y+h, x:x+w]
                #warped = four_point_transform(img, hull.reshape(4, 2))
                warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                T = threshold_local(warped, 23, offset = 11, method = "gaussian")
                warped = (warped > T).astype("uint8") * 255
                return(warped)
                '''
                print(pytesseract.image_to_string(warped).split("\n"))

                cv2.imshow('img',imutils.resize(warped, height = 650))
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                '''

def get_name(arr):
    '''
    From the array of text, searches for the person names using specific pattern

    TODO: Improvements
    '''
    try:
        arr = arr[-5:]
        names = []
        for i in arr:
            flag = False
            for j in i:
                if not ((j >= "A" and j <= "Z") or j == " "):
                    flag = True
                    break
            if not flag and i != "":
                names.append(i)
        return(names[-1])
    except:
        return("Name not found!")

## New MICR Method ##
def get_micrcode(image_name):
    try:
        image = cv2.imread(image_name)
        image = crop_transform(image)
        #image = cv2.resize(image, (1920,1080))

        (h,w,) = image.shape[:2]
        delta = int(h - (h*0.1))
        bottom = image[delta:h, 0:w]

        thresh = cv2.threshold(bottom, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        text = pyt.image_to_string(thresh, lang='mcr')
        #print("MICR:", text)
        a, b, c, d = text.split()[:4]

        res = {"MICR": b[:-2], "city_code": b[:3], "bank_code": b[3:6], "branch_code": b[6:9]}

        return(res)
        '''
        if len(b) > 10:
            b = b[0:9]
            b += 'a'
        return(a + ' ' + b + ' ' + c + ' ' + d)
        '''
    except Exception as e:
        print(e)
        return('MICR Not Found')
## New MICR End ##

#### IFSC #####
def get_ifsc(image):
    
    banks = {"ALLA": "Allahabad Bank", "YESB": "Yes Bank", "HDFC": "HDFC Bank"}
    def replace(text):
        return text.replace('?', '7')
    
    img = cv2.imread(image)
    text = pyt.image_to_string(img, config=('--oem 1 --psm 3'))
    
    ifsc = text.find('IFSC')
    new_text = text[ifsc : ifsc + 30]
    new_text = replace(new_text)
    
    try:
        code = re.findall(r'[A-Z0-9]{11}', new_text)[0]
    except:
        return("IFSC not found")
    
    bank = ""
    for i in banks.keys():
        if i == code[:4]:
            bank = banks[i]
    
    return {"IFSC": code, "bank": bank}

#### Account No ####
def get_acc(image_path):
    # Read image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (1920,1080))
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    luminance, a, b = cv2.split(lab)
    
    hist,bins = np.histogram(luminance,256,[0,256])

    mean = int((np.argmax(hist) + np.argmin(hist)) / 2)

    luminance[luminance > mean] = 255
    luminance[luminance <= mean] = 0
    
    # Read template
    template = cv2.imread('templates/template_acc.jpg', 0)
    
    thresh = cv2.threshold(template, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Set difference
    diff = cv2.subtract(luminance, template)
    
    text = pyt.image_to_string(diff, config=('--oem 1 --psm 3'))
    
    if '-' in list(text):
        
        text = text.replace('-', '')
        
    try:
        acc_no = re.findall(r'[0-9]{9,18}',text)[0]
    except:
        text = pyt.image_to_string(luminance, config=('--oem 1 --psm 3'))
        if '-' in list(text):
            
            text = text.replace('-', '')
        try:
            acc_no = re.findall(r'[0-9]{9,18}',text)[0]
        except:
            return 0
    return acc_no
    
def get_acc2(cheque_img):
    img = cv2.imread(cheque_img)
    
    text = pyt.image_to_string(img, config=('--oem 1 --psm 3'))
    
    if '-' in list(text):
        text = text.replace('-', '')
    try:
        text = re.findall(r'[0-9]{9,18}', text)[0]
    except:
        return 0
    return text


def ensemble_acc_output(cheque_img):
    acc1 = get_acc(cheque_img)
    acc2 = get_acc2(cheque_img)
    acc = [acc1, acc2]
    
    
    if acc1 == 0 and acc2 == 0:
        return 'Account Number Not Found'
    else:
        for no in acc:
            if no != 0:
                return no
        return 'Account Number Not Found'
#### Account No END ####