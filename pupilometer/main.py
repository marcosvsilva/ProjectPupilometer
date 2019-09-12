import numpy as np
import cv2
import os
import time

# semicircle_positions = ('northeast', 'southwest', 'east', 'south', 'southeast')
semicircle_positions = ('east', 'west', 'south')


class Main:
    def __init__(self):
        # Paths parameters
        self.dataset_path = os.getcwd() + "/dataset"
        self.output_path = os.getcwd() + "/identified"
        self.threshold_path = os.getcwd() + "/threshold"
        self.name_output = "frame"
        self.threshold_output = "threshold"
        self.exams = os.listdir(self.dataset_path)

        # Filters parameters
        self.whitening = 0.2
        self.size_filter_gaussian = (9, 9)
        self.type_gaussian = 0
        self.size_median = 3
        self.thresh_threshold = 25
        self.maxvalue_threshold = 255

        # Selection best ellipse parameters
        self.best_area_height = (50, 300)
        self.best_area_width = (50, 300)
        self.radius_size = (30, 80)
        self.edge_threshold = 200
        self.radius_validate_threshold = 3

        # Circle draw parameters
        self.color_circle = (255, 255, 0)
        self.thickness_circle = 3

        # Others parameters
        self.save_output = False
        self.save_threshold_output = False
        self.sleep_pause = 3

    def start_process(self):
        for exam in self.exams:
            video = cv2.VideoCapture("{}/{}".format(self.dataset_path, exam))
            self.pupillary_analysis(video)

    def pupillary_analysis(self, exam):
        number_frame = 0
        while exam.isOpened():
            ret, frame = exam.read()
            rows, cols, _ = frame.shape
            number_frame += 1

            name_image = "%s_%03d.png" % (self.name_output, number_frame)
            if name_image == 'frame_023.png':
                print("pause")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gaussian = cv2.GaussianBlur(gray, self.size_filter_gaussian, self.type_gaussian)
            median = cv2.medianBlur(gaussian, self.size_median)

            kernel_one = np.ones((5, 5), np.uint8)
            erode_one = cv2.erode(median, kernel=kernel_one, iterations=1)
            dilate_one = cv2.dilate(erode_one, kernel=kernel_one, iterations=1)
            threshold_one = cv2.threshold(dilate_one, self.thresh_threshold,
                                          self.maxvalue_threshold, cv2.THRESH_BINARY_INV)[1]

            kernel_two = np.ones((7, 7), np.uint8)
            erode_two = cv2.erode(threshold_one, kernel=kernel_two, iterations=1)
            dilate_two = cv2.dilate(erode_two, kernel=kernel_two, iterations=1)
            threshold_two = cv2.threshold(dilate_two, self.thresh_threshold,
                                          self.maxvalue_threshold, cv2.THRESH_BINARY_INV)[1]

            final = np.copy(gray)

            contours = cv2.findContours(dilate_two, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[1]
            contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

            img_center, center, radius = self.best_center(image=dilate_two, contours=contours)

            if center is not None and radius > 0:
                cv2.circle(final, center, radius, self.color_circle, self.thickness_circle)

            img_final1 = cv2.hconcat([self.resize(gray), self.resize(gaussian), self.resize(median)])
            img_final2 = cv2.hconcat([self.resize(erode_one), self.resize(dilate_one), self.resize(threshold_one)])
            img_final3 = cv2.hconcat([self.resize(erode_two), self.resize(dilate_two), self.resize(final)])
            img_final = cv2.vconcat([img_final1, img_final2, img_final3])

            cv2.namedWindow('Training', cv2.WINDOW_NORMAL)
            cv2.imshow('Training', img_final)

            if self.save_output:
                name_output = "%s/%s_%03d.png" % (self.output_path, self.name_output, number_frame)
                cv2.imwrite(name_output, img_final)

            if self.save_threshold_output:
                threshold_output = "%s/%s_%03d.png" % (self.threshold_path, self.threshold_output, number_frame)
                cv2.imwrite(threshold_output, threshold_two)

            if cv2.waitKey(1) & 0xFF == ord('p'):  # Pause
                time.sleep(self.sleep_pause)

        exam.release()
        cv2.destroyAllWindows

    def best_center(self, image, contours):
        center = None
        rad = 0
        new_image = np.copy(image)
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            center = (x + int(w / 2), y + int(h / 2))
            lin, col = image.shape
            if center[0] < lin and center[1] < col:
                cv2.circle(new_image, center, 9, (0, 0, 0), self.thickness_circle)

                radius = []
                for direction in semicircle_positions:
                    new_image, radio = self.calculate_radius(image=new_image, center=center, direction=direction)
                    radius.append(radio)

                if self.validate_radius(radius):
                    rad = int(np.array(radius).max())
                    break
        return new_image, center, rad

    def validate_radius(self, radius):
        validate = 0
        for rad in radius:
            if rad in range(self.radius_size[1])[slice(*self.radius_size)]:
                validate += 1
        return validate >= self.radius_validate_threshold

    def calculate_radius(self, image, center, direction):
        new_image = np.copy(image)
        lin, col = image.shape
        x, y = center
        radius = calc_radius = 0
        init = int(image[x][y])

        while (1 < x < lin-1) and (1 < y < col-1):
            if direction == 'east':
                x += 1
            elif direction == 'west':
                x -= 1
            elif direction == 'north':
                y -= 1
            elif direction == 'south':
                y += 1

            cv2.circle(new_image, (x, y), 3, (0, 0, 0), self.thickness_circle)

            calc_radius += 1
            if abs(int(image[x][y]) - init) > self.edge_threshold:
                radius = calc_radius
                break

        return new_image, radius

    @staticmethod
    def resize(figure):
        return cv2.resize(figure, (0, 0), fx=0.5, fy=0.5)


if __name__ == '__main__':
    main = Main()
    main.start_process()
