import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):

    done = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__(None)
        self.image = None
        self.opacity = 0
        self.radius = 0
        self.sample_radius = 0
        self.x = 0
        self.y = 0

    # OLD METHOD (FASTER but creates sharp edges)
    # def healImage(self, x, y):
    #     if self.image is not None:
    #         mask = np.zeros_like(self.image)
    #         cv2.circle(mask, (x, y), self.radius, (255, 255, 255), -1)
    #         source_area = cv2.inpaint(
    #             self.image, mask[:, :, 0], self.sample_radius, cv2.INPAINT_TELEA
    #         )
    #         radius_y, radius_x = self.radius, self.radius

    #         self.image[y - radius_y:y + radius_y, x - radius_x:x + radius_x] = source_area[y - radius_y:y + radius_y, x - radius_x:x + radius_x]

    #         self.done.emit(self.image)    

    def healImage(self, x, y, opacity=0.5):
        if self.image is None:
            return
        
        mask = np.zeros_like(self.image)

        # Create a feathered mask for smoother blending
        cv2.circle(mask, (x, y), self.radius, (255, 255, 255), -1)
        mask = cv2.GaussianBlur(mask, (0, 0), self.radius * 0.6) # you can adjust the last value


        # inpainting to get source area
        source_area = cv2.inpaint(
            self.image, mask[:, :, 0], self.sample_radius, cv2.INPAINT_TELEA
        )

        radius_x, radius_y = self.radius, self.radius

        # perform poisson blender for smoother transition
        blended_image = cv2.seamlessClone(
            source_area,
            self.image,
            mask[:, :, 0],
            (x, y),
            cv2.NORMAL_CLONE
        )

        self.image[y - radius_y:y + radius_y, x - radius_x:x + radius_x] = (
            opacity * blended_image[y - radius_y: y + radius_y, x - radius_x:x + radius_x] + 
            (1 - opacity) * self.image[y - radius_y:y + radius_y, x - radius_x:x + radius_x]
        )

        self.done.emit(self.image)

    def run(self):
        self.healImage(self.x, self.y, self.opacity)

    def set_and_run(self, img, x, y, radius, sample_radius, opacity):
        self.image = img
        self.x = x
        self.y = y
        self.radius = radius
        self.sample_radius = sample_radius
        self.opacity = opacity
        self.start() # starts the thread which auto calls run method
                
