import sys
import cv2
import sqlite3

from itertools import izip

def on_mouse(event, x, y, flag, params):
    global is_drawing, marks
    if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
        is_drawing = True
    if event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP:
        is_drawing = False
    if event == cv2.EVENT_LBUTTONDOWN:
        marks.append((x, y, 'r'))
    elif event == cv2.EVENT_RBUTTONDOWN:
        marks.append((x, y, 'l'))
    elif event == cv2.EVENT_MOUSEMOVE and is_drawing:
        _, _, shape = marks[-1]
        if len(marks) % 2 == 0:
            marks.pop()
        marks.append((x, y, shape))

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

def save_all(img_id, seq_id, marks, labels, store):
    c = store.cursor()
    
    objects = list()
    for (p0, p1, p2, p3),label in izip(grouped(marks,4), labels):
        x0, y0, shape = p0
        x1, y1, _     = p1
        x2, y2, _     = p2
        x3, y3, _     = p3
        if shape == 'r':
            objects.append((img_id,seq_id,x0,y0,x1,y1,x2,y2,x3,y3,label))
        elif shape == 'l':
            objects.append((img_id,seq_id,x2,y2,x3,y3,x0,y0,x1,y1,label))

    c.executemany("""INSERT INTO Objects VALUES (?,?,?,?,?,?,?,?,?,?,?)""", objects)
    store.commit()
    print "Saved!"

marks = list()
is_drawing = False

if __name__=="__main__":
    window_name = "Object Marker v0.1"
    input_path  = raw_input("Enter path to input directory: ")
    sequence_id = raw_input("Enter sequence's id: ")
    output_path = raw_input("Enter path to output database: ")
    
    cap     = cv2.VideoCapture(input_path)
    store   = sqlite3.connect(output_path)
    cursor  = store.cursor()
    labels  = list()
    counter = 0

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, on_mouse, None)
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS Objects( 
                                           img_id INT NOT NULL,
                                           seq_id INT NOT NULL,
                                           box_sx REAL, box_sy REAL, 
                                           box_ex REAL, box_ey REAL, 
                                           line_sx REAL, line_sy REAL, 
                                           line_ex REAL, line_ey REAL, 
                                           label INT)""")
    store.commit()
    
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
                marks  = []
                labels = []
            elif key == ord('s'): # Save all
                save_all(counter, sequence_id, marks, labels, store)
                img    = marked
                marks  = []
                labels = []
            elif key == ord(' '): # Save all and next
                save_all(counter, sequence_id, marks, labels, store)
                break
            elif key-48 in range(0,10): # Labeling last object
                print "Last object is of type %d" % (key-48)
                labels.append(key-48)
        counter += 1
    store.close()
