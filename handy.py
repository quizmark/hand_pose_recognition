from imutils.video import VideoStream
import cv2
import imutils
import time
from Hand import Hand

def capture_histogram(cap):
    while True:
        frame = cap.read()
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (600, 600))

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "Place the hand inside box and press `A`",
                    (5, 50), font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.rectangle(frame, (250, 250), (350, 350), (255, 255, 255), 2)
        box = frame[255:345, 255:345]

        cv2.imshow("Capture Histogram", frame)
        key = cv2.waitKey(1)
        if key == 97:
            object_color = box
            break
        if key == 27:
            return None
    
    object_color_hsv = cv2.cvtColor(object_color, cv2.COLOR_BGR2HSV)
    object_hist = cv2.calcHist([object_color_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
    cv2.normalize(object_hist, object_hist, 0, 255, cv2.NORM_MINMAX)
    return object_hist
    
def locate_object(frame, object_hist):
    frame = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    object_segment = cv2.calcBackProject(
        [hsv_frame], [0, 1], object_hist, [0, 180, 0, 256], 1)

    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    cv2.filter2D(object_segment, -1, disc, object_segment)

    _, segment_thresh = cv2.threshold(
        object_segment, 70, 255, cv2.THRESH_BINARY)

    # improve image quality
    kernel = None
    eroded = cv2.erode(segment_thresh, kernel, iterations=2)
    dilated = cv2.dilate(eroded, kernel, iterations=2)
    closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

    # masking
    masked = cv2.bitwise_and(frame, frame, mask=closing)

    return closing, masked, segment_thresh


def detect_hand(frame, hist):
    detected_hand, masked, raw = locate_object(frame, hist)
    return Hand(detected_hand, masked, raw, frame)
