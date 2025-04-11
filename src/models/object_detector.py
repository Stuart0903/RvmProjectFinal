from ultralytics import YOLO
import logging
from ..config.settings import Settings

class ObjectDetector:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.model = YOLO(settings.YOLO_MODEL_PATH)

    def detect_objects(self, image_path: str):
        return self.model(image_path, conf=self.settings.CONFIDENCE_THRESHOLD)