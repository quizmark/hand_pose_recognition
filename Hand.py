import cv2
import numpy as np
import imutils
from sklearn.metrics import pairwise

class Hand:

    def __init__(self, binary, masked, raw, frame):
        self.masked = masked
        self.binary = binary
        self.raw = raw
        self.frame = frame
        self.contours = []
        self.outline = self.draw_outline()
        self.fingertips = self.extract_fingertips()

    def draw_outline(self, min_area=10000, color=(0, 255, 0), thickness=2):
        contours = cv2.findContours(self.binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(contours)
        if len(cnts):
            cnt = max(cnts, key=cv2.contourArea)
            if cv2.contourArea(cnt)>min_area:
                self.contours = cnt
                cpy = self.frame.copy()
                cv2.drawContours(cpy, [cnt], 0, color, thickness)
                return cpy
        return self.frame
    
    def extract_fingertips(self, filter_value=50):
        cnt = self.contours
        if len(cnt) == 0:
            return cnt
        points = []
        hull = cv2.convexHull(cnt, returnPoints=False)
        defects = cv2.convexityDefects(cnt, hull)
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                end = tuple(cnt[e][0])                
                points.append(end)
            filtered = self.filter_points(points, filter_value)
            filtered.sort(key=lambda point: point[1])
            return [pt for idx, pt in zip(range(5), filtered)]
        return None

    def filter_points(self, points, filter_value):
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if points[i] and points[j] and self.dist(points[i], points[j]) < filter_value:
                    points[j] = None
        filtered = []
        for point in points:
            if point is not None:
                filtered.append(point)
        return filtered

    def get_center_of_mass(self):
        if len(self.contours) == 0:
            return None
        M = cv2.moments(self.contours)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        return (cX, cY)

    def dist(self, a, b):
        return np.sqrt((a[0] - b[0])**2 + (b[1] - a[1])**2)
