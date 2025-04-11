import cv2
import time
import os
import logging
from typing import List
from ..config.settings import Settings

class CameraController:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.camera = cv2.VideoCapture(settings.CAMERA_INDEX, cv2.CAP_DSHOW)
        os.makedirs(settings.IMAGE_SAVE_PATH, exist_ok=True)

    def capture_images(self) -> List[str]:
        images = []
        for i in range(self.settings.IMAGE_COUNT):
            ret, frame = self.camera.read()
            if ret:
                path = os.path.join(
                    self.settings.IMAGE_SAVE_PATH,
                    f"img_{self.settings.get_timestamp()}_{i}.jpg"
                )
                cv2.imwrite(path, frame)
                images.append(path)
                time.sleep(self.settings.IMAGE_DELAY)
        return images

    def release(self):
        if hasattr(self, 'camera'):
            self.camera.release()