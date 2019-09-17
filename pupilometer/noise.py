import numpy as np
import cv2


class Noise:
    def __init__(self, min_area):
        self.min_area = min_area

    def remove_noise(self, frame, contours):
        if frame is None:
            raise Exception("Frame is none!")

        line, col = frame.shape
        new_frame = np.copy(frame)

        cv2.drawContours(new_frame, contours, -1, (0, 0, 0), 10)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)


            # if w * h < self.min_area:
            #     for i in range(w):
            #         for j in range(h):
            #             position = x+i
            #             position2 = y+j
            #
            #             if position >= line or position2 >= col:
            #                 break
            #
            #             if new_frame[position, position2] == 255:
            #                 new_frame[position, position2] = 0
            #             else:
            #                 new_frame[position, position2] = 255

        return new_frame
