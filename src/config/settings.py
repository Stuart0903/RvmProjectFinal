import os
import platform
import serial.tools.list_ports
from datetime import datetime
from pathlib import Path

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'USB' in port.description:
            return port.device
    return 'COM3'

class Settings:
    # Convert BASE_DIR to Path object
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Hardware Configuration
    SERIAL_PORT = find_arduino_port()
    BAUD_RATE = 9600
    SERIAL_TIMEOUT = 1
    ULTRASONIC_THRESHOLD_CM = 10.0

    # Camera configuration
    CAMERA_INDEX = 0
    IMAGE_COUNT = 3
    IMAGE_DELAY = 0.5

    # AI/ML Configuration
    YOLO_MODEL_PATH = r"C:\Users\Acer\Documents\PlatformIO\Projects\RVMachine\src\rvmachine\models\best.pt"
    CONFIDENCE_THRESHOLD = 0.5
    MATERIAL_TYPES = ["plastic", "can"]

    # Image paths - now using Path objects consistently
    IMAGE_SAVE_PATH = BASE_DIR.parent / "captured_images"  # Using parent to go up one level
    DETECTED_IMAGE_PATH = BASE_DIR.parent / "detected_images"
    
    # Logging Configuration
    LOG_FILE = BASE_DIR.parent / "logs" / "detection.log"
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # QR Code Settings
    QR_CODES_DIR = BASE_DIR / "static" / "qr_codes"
    QR_CODE_SIZE = (300, 300)
    QR_CODE_EXPIRE_MINUTES = 15

    SESSION_TIMEOUT = 30 
    
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    @classmethod
    def create_directories(cls):
        """Initialize all required directories"""
        # Convert Path objects to strings for os.makedirs
        os.makedirs(str(cls.IMAGE_SAVE_PATH), exist_ok=True)
        os.makedirs(str(cls.DETECTED_IMAGE_PATH), exist_ok=True)
        os.makedirs(str(cls.LOG_FILE.parent), exist_ok=True)
        os.makedirs(str(cls.QR_CODES_DIR), exist_ok=True)
        
        # Create material-specific directories
        for material in cls.MATERIAL_TYPES:
            os.makedirs(str(cls.IMAGE_SAVE_PATH / material), exist_ok=True)
            os.makedirs(str(cls.DETECTED_IMAGE_PATH / material), exist_ok=True)