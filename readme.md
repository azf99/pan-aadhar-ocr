# Document OCR
By- Azfar Lari

## Requirements

Python 3

## Setup:
1. Install the dependencies on linux

$ sudo apt install tesseract-ocr
(Install Tesseract-OCR engine as given in the instructions: https://github.com/tesseract-ocr/tesseract)

2. Install python dependencies:

pip3 install -r requirements.txt


## Usage:
1. Use: python3 app.py to start the flask server

2. The file types are: "Aadhar Front", "Aadhar Back", "Cheque", "PAN"

3. It returns a JSON containing all the data

## Note
Have provided Separate API for face matching.
