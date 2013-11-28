import cv2
import sqlite3

class Marker(object):
    
    def __init__(self):
        self.rect = ((0,0),(0,0))
        self.line = ((0,0),(0,0))
        
        self.objs = list()
        
    def set_img(self, img):
        self.img     = img
        self.overlay = img.copy()
    
    def on_mouse(self, event, x, y, flag, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.rect[0] = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing is True:
                cv2.rectangle(self.overlay, self.rect[0], self.rect[1], (0,255,255))
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.rect[1] = (x, y)
            cv2.rectangle(self.overlay, self.rect[0], self.rect[1], (0,255,255))
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.drawing = True
            self.line[0] = (x, y)
        elif event == cv2.EVENT_RBUTTONUP:
            self.drawing = False
            self.line[1] = (x, y)
            cv2.line(self.overlay, self.line[0], self.line[1], (0,255,255))
            
    def clear(self):
        self.rect = ((0,0),(0,0))
        self.line = ((0,0),(0,0))
        
    def clear_all(self):
        self.objs = list()
            
if __name__=="__main__":
    window_name = "Object Marker v0.1"
    input_path  = raw_input("Enter path to input directory: ")
    output_path = raw_input("Enter path to output database: ")
    
    cap     = cv2.VideoCapture(input_path)
    db      = sqlite3.connect(output_path)
    counter = 0

    marker  = Marker()
    cv2.setMouseCallback(window_name, marker.on_mouse, None)
    
    while True:
        buf = cap.read()[1]

        img = buf.copy()
        cv2.imshow(window_name, img)
        marker.set_img(img)
        
        key = cv2.waitKey(100) & 0xff
        if key == 27:         # Stop if ESC is pressed
            break
        elif key == ord('s'): # Skip this image
            print "Skip frame no. " + counter
        elif key == ord('l'): # Add object marked line
            pass
        elif key == ord('r'): # Add object marked rectangle
            pass
        elif key == ord('z'): # Clear all unsaved
            marker.clear()
        elif key == ord('c'): # Clear all
            marker.clearall()
        elif key == ord(' '): # Save all and next
            pass
        elif int(key) in range(0,10): # Labeling last marked object
            pass
        counter += 1