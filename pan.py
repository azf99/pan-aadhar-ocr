import re
import string
from processing import clean_text
def clean_gibbersh(arr):
    '''
    From an input array of OCR text, removes the gibberish and noise, such as,
    symbols and empty strings
    '''

    arr = [x for x in arr if len(x) > 3]
    t = 0
    d = 0
    for i in range(len(arr)):

        if "india" in arr[i].lower():
            d = i
            
        if "income" in arr[i].lower() or "tax" in arr[i].lower():
            t = i
            
    del arr[:max([d, t])+1]
    print("d= ", d, t)
    print(arr)
    for i in range(len(arr)):
        arr[i] = arr[i].replace("!", "i")
        arr[i] = clean_text(arr[i])
        
        temp = list(arr[i])
        for j in range(len(temp)):
            #if not ((j >= "A" and j <= "Z") or j == " "):
            #    arr[i].replace(j, "")
            
            
            if (temp[j] in string.punctuation) and (temp[j] not in ",/-" ):
                #arr[i].replace(j, "")
                temp[j] = ""
        arr[i] = "".join(temp).strip()
                
    
    return (arr)


def extract_pan(text_in):
    '''
    From the array of text, searches for the PAN number using regex
    '''

    try:
        pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        # pan = re.compile(pan_regex)

        for i in text_in:
            # print(i)
            pan = re.findall(pan_regex, i)
            if len(pan) > 0:
                return (pan[0])
    except:
        print("Error in PAN Number Extraction")


def extract_dob(text_in):
    '''
    From the array of text, searches for the Data of Birth using regex
    '''

    try:
        # pan = re.compile(pan_regex)
        dob_regex = r"\d{1,2}\/\d{1,2}\/\d{4}"
        for i in text_in:
            # print(i)
            dob = re.findall(dob_regex, i)
            if len(dob) > 0:
                return (dob[0])
    except:
        print("Error in DOB extraction")


def check_names(arr):
    '''
    From the array of text, searches for the person names using specific pattern

    TODO: Improvements
    '''

    names = []
    for i in arr:
        flag = False
        for j in i:
            if not ((j >= "A" and j <= "Z") or j == " "):
                flag = True
                break
        if not flag and i != "":
            names.append(i)
    return (names)


def get_labels_from_pan(text_in):

    imp = {}

    text_in = clean_gibbersh(text_in)

    # print(text_in)
    imp["PAN No"] = extract_pan(text_in)
    imp["Date Of Birth"] = extract_dob(text_in)
    names = check_names(text_in)

    imp["Name"] = names[0]

    try:
        imp["Father's Name"] = names[1]
    except:
        pass

    return(imp)

