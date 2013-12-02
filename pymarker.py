import sys
import cv2
import sqlite3

from itertools import izip

def on_mouse(event, x, y, flag, params):
    global is_drawing, marks
    if event == cv2.EVENT_MBUTTONDOWN:
        is_drawing = True
    if event == cv2.EVENT_MBUTTONUP:
        is_drawing = False
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_LBUTTONUP:
        marks.append((x, y, 'r'))
    elif event == cv2.EVENT_MOUSEMOVE and is_drawing:
        if len(marks) % 2 == 0:
            _, _, shape = marks.pop()
            marks.append((x, y, shape))
    elif event == cv2.EVENT_RBUTTONDOWN or event == cv2.EVENT_RBUTTONUP:
        marks.append((x, y, 'l'))

def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)

def grouped(iterable, n):
    return izip(*[iter(iterable)]*n)

def mark_img(img, marks):
    buf = img.copy()
    for (x0, y0, shape), (x1, y1, shape) in pairwise(marks):
        if shape == 'r':
            cv2.rectangle(buf, (x0, y0), (x1, y1), (0,255,255))
        elif shape == 'l':
            cv2.line(buf, (x0, y0), (x1, y1), (0,255,255))
    return buf

def save_all(img_id, marks, labels, store):
    c = store.cursor()
    
    objects = list()
    for (p0, p1, p2, p3),label in zip(grouped(marks,4), labels):
        x0, y0, shape = p0
        x1, y1, _     = p1
        x2, y2, _     = p2
        x3, y3, _     = p3
        if shape == 'r':
            list.append((img_id,x0,y0,x1,y1,x2,y2,x3,y3,label))
        elif shape == 'l':
            list.append((img_id,x2,y2,x3,y3,x0,y0,x1,y1,label))

    c.executemany("INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?,?)", objects)
    store.commit()

marks = list()
is_drawing = False

if __name__=="__main__":
    window_name = "Object Marker v0.1"
    input_path  = raw_input("Enter path to input directory: ")
    output_path = raw_input("Enter path to output database: ")
    
    cap     = cv2.VideoCapture(input_path)
    store   = sqlite3.connect(output_path)
    labels  = list()
    counter = 0

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse, None)

    while True:
        img    = cap.read()[1]
        marks  = []
        labels = []
        
        is_drawing = False
        
        while True:
            marked = mark_img(img, marks)
            cv2.imshow(window_name, marked)
            
            key = cv2.waitKey(100) & 0xff
            if key == 27:         # Stop if ESC is pressed
                sys.exit()
            elif key == ord('x'): # Skip this image
                print "Skip frame no. %d" % counter
                break
            elif key == ord('d'): # Delete last mark
                marks = marks[:-2]
            elif key == ord('r'): # Remove last label
                labels  = labels[:-1]
            elif key == ord('c'): # Clear all
                marks = []
                labels  = []
            elif key == ord('s'): # Save all
                save_all(counter, marks, labels, store)
                img = marked
                marks = []
            elif key == ord(' '): # Save all and next
                save_all(counter, marks, labels, store)
                break
            elif int(key) in range(0,10): # Labeling last object
                labels.append(int(key))
        counter += 1
    store.close()
