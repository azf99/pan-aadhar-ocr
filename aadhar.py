import cv2
import re
import numpy as np

# extract labels from aadhar image
def get_labels_from_aadhar(temp):
    imp = {}

    # reverse list to parse through it starting from the aadhar number
    temp = temp[::-1]
    # parse through the list
    for idx in range(len(temp)):
        
        try:
            # if string similar to aadhar number is found, use it as a hook to find other details
            if re.search(r"[0-9]{4}\s[0-9]{4}\s[0-9]{4}", temp[idx]):
                try:
                    imp['Aadhar No'] = re.findall(r"[0-9]{4}\s[0-9]{4}\s[0-9]{4}", temp[idx])[0]
                except Exception as _:
                    imp['Aadhar No'] = "Not Found"
                if temp[idx + 1].endswith("Female") or temp[idx + 1].endswith("FEMALE"):
                    imp["Gender"] = "Female"
                elif temp[idx + 1].endswith("Male") or temp[idx + 1].endswith("MALE"):
                    imp["Gender"] = "Male"
                elif temp[idx + 2].endswith("Female") or temp[idx + 2].endswith("FEMALE"):
                    imp["Gender"] = "Female"
                elif temp[idx + 2].endswith("Male") or temp[idx + 2].endswith("MALE"):
                    imp["Gender"] = "Male"
                elif temp[idx + 3].endswith("Female") or temp[idx + 3].endswith("FEMALE"):
                    imp["Gender"] = "Female"
                elif temp[idx + 3].endswith("Male") or temp[idx + 3].endswith("MALE"):
                    imp["Gender"] = "Male"

            elif re.search(r"[0-9]{2}\-|/[0-9]{2}\-|/[0-9]{4}", temp[idx]):
                # if string similar to date is found, use it as a hook to find other details
                try:
                    imp["Date of Birth"] = re.findall(r"[0-9]{2}\-[0-9]{2}\-[0-9]{4}", temp[idx])[0]
                except Exception as _:
                    imp["Date of Birth"] = re.findall(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", temp[idx])[0]
                imp["Name"] = temp[idx + 1]
            
            elif "Year of Birth" in temp[idx]:
                # handle variation of 'Year of Birth' in place of DOB
                try:
                    imp["Year of Birth"] = re.findall(r"[0-9]{4}", temp[idx])[0]
                except Exception as _:
                    imp["Year of Birth"] = "Not Found"
                imp["Name"] = temp[idx + 1]
            
            elif re.search(r"[0-9]{4}", temp[idx]):
                # handle exception if Year of Birth is not found but string similar to year is found
                try:
                    imp["Year of Birth"] = re.findall(r"[0-9]{4}", temp[idx])[0]
                except Exception as _:
                    imp["Year of Birth"] = "Not Found"
                imp["Name"] = temp[idx + 1]
            
            elif len(temp[idx].split(' ')) > 2:
                # following text will be name, ignore line if it includes GOVERNMENT OF INDIA
                if 'GOVERNMENT' in temp[idx].upper() or 'OF' in temp[idx].upper() or 'INDIA' in temp[idx].upper():
                    continue
                else:
                    imp["Name"] = temp[idx]
        except Exception as _:
            pass
    return imp


# function to crop aadhar back image
def crop_aadhar(image_path, crop_path):
    image = cv2.imread(image_path, 0)
    height, width = image.shape
    image = image[int(height * (15 / 100)):int(height * (70 / 100)), int(width * (40 / 100)):]
    cv2.imwrite(crop_path, image)


def get_address(details):
    imp = {'Address': ''}

    try:
        if 'Address' in details[0]:
            if details[0].split('Address', 1)[1].strip() != '':
                imp["Address"] = details[0].split('Address', 1)[1].strip()
            for line in details[1:]:
                imp["Address"] += '\n' + line
            imp['Address'] = imp['Address'].strip()
                
        elif 'Address' in details[1]:
            if details[1].split('Address', 1)[1].strip() != '':
                imp["Address"] = details[1].split('Address', 1)[1].strip()
            for line in details[2:]:
                imp["Address"] += '\n' + line
            imp['Address'] = imp['Address'].strip()
        
        elif 'Address' in details[2]:
            if details[2].split('Address', 1)[1].strip() != '':
                imp["Address"] = details[2].split('Address', 1)[1].strip()
            for line in details[3:]:
                imp["Address"] += '\n' + line
            imp['Address'] = imp['Address'].strip()
        
        else:
            imp["Address"] = 'Failed to read Address'
    except Exception as _:
        imp["Address"] = 'Failed to read Address'

    return imp
    