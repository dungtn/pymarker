import cv2
import sqlite3

classes = ['Others', 'Motobike', 'Pedestrian', 'Car', 'Truck', 'Bus', 'Bicycle']
font = cv2.FONT_HERSHEY_PLAIN

im_path = raw_input("Enter path to image directory: ")
cap     = cv2.VideoCapture(im_path)

gt_path = raw_input("Enter path to groundtruth DB: ")
store   = sqlite3.connect(gt_path)
cursor  = store.cursor()

counter = 0
key     = ord('n')
while True:
    if key == ord('n'):
        img = cap.read()[1]
    
        cursor.execute("SELECT * FROM Objects WHERE img_id=:id", {"id":counter})
        objs = cursor.fetchall()

        for obj in objs:
            obj = map(int, obj)
            cv2.rectangle(img, (obj[2], obj[3]), (obj[4], obj[5]), (0,255,255))
            cv2.line(img, (obj[6], obj[7]), (obj[8], obj[9]), (0,255,255))
            cv2.putText(img, classes[obj[10]], (obj[2],obj[3]), font, 0.8, (255,0,0), 1, cv2.CV_AA)

        counter += 1

    cv2.imshow("Object Marker v0.1", img)
    
    key = cv2.waitKey(100) & 0xff
    if key == 27 or not cap:
        break

cap.release()
cv2.destroyWindow("Object Marker v0.1")
