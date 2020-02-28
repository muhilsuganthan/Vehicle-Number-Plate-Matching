import cv2
import imutils
import numpy as np
import pytesseract
import re
import mysql.connector
from PIL import Image


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="project_asha"
)


img = cv2.imread('images/1.jpg',cv2.IMREAD_COLOR)
img = cv2.resize(img, (620,480) )

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
edged = cv2.Canny(gray, 30, 200)

cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
screenCnt = None


for c in cnts:
 peri = cv2.arcLength(c, True)
 approx = cv2.approxPolyDP(c, 0.018 * peri, True)

 if len(approx) == 4:
  screenCnt = approx
  break

if screenCnt is None:
 detected = 0
 print ("No contour detected")
else:
 detected = 1

if detected == 1:
 cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

mask = np.zeros(gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[screenCnt],0,255,-1)
new_image = cv2.bitwise_and(img,img,mask=mask)

(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x), np.min(y))
(bottomx, bottomy) = (np.max(x), np.max(y))
Cropped = gray[topx:bottomx+1, topy:bottomy+1]

text = pytesseract.image_to_string(Cropped, config='--psm 11')
text = re.sub('[^A-Za-z0-9]+', '', text)
#print (text)

mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM whitelisted_vehicles WHERE vehicle_no LIKE %s LIMIT 1", ("%" + text + "%",))
myresult = mycursor.fetchall()

if mycursor.rowcount == 1:
	print ("ALLOWED")
else:
	print ("NOT ALLOWED")