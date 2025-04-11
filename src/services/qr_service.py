import qrcode
import logging
import time
import uuid
from PIL import Image
from typing import Optional, Tuple
from pathlib import Path
import json

class QRService:
    def __init__(self, settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(getattr(settings, 'QR_OUTPUT_DIR', 'qr_codes'))
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_qr_image(self, data: dict) -> Tuple[Optional[Image.Image], Optional[str]]:
        """Generate QR code image from recycling data"""
        try:
            # Generate a unique UUID for this QR code
            qr_id = str(uuid.uuid4())
            
            # Format the data as a JSON array with one object containing qr_id and items
            qr_data = [{
                "qr_id": qr_id,
                "items": []
            }]
            
            if data.get('plastic_count', 0) > 0:
                qr_data[0]["items"].append({"class": "plastic", "count": data["plastic_count"]})
            
            if data.get('can_count', 0) > 0:
                qr_data[0]["items"].append({"class": "can", "count": data["can_count"]})
            
            # Convert to nicely formatted JSON string
            qr_text = json.dumps(qr_data, indent=2)
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            return qr.make_image(fill_color="black", back_color="white"), qr_id
            
        except Exception as e:
            self.logger.error(f"Error generating QR code: {str(e)}")
            return None, None
            
    def generate_qr_code(self, data: dict) -> Tuple[Path, str]:
        """Generate QR code and save to file, returning the file path and qr_id"""
        qr_image, qr_id = self.generate_qr_image(data)
        if qr_image and qr_id:
            # Create a filename based on timestamp and qr_id
            timestamp = int(time.time())
            filename = self.output_dir / f"recycling_qr_{timestamp}_{qr_id[:8]}.png"
            
            # Save the image
            qr_image.save(filename)
            self.logger.info(f"QR code saved to {filename}")
            return filename, qr_id
        else:
            raise ValueError("Failed to generate QR code image")