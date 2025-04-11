import logging
from typing import Dict

class RecyclingSession:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reset_session()

    def reset_session(self):
        """Reset all counts for a new session"""
        self.plastic_count = 0
        self.can_count = 0
        self.rejected_count = 0
        self.no_detection_count = 0
        self.total_count = 0
        self.logger.debug("Recycling session reset")

    def add_item(self, material_type: str):
        """Add a detected item to the session"""
        if not material_type:
            self.logger.warning("Attempted to add item with no material type")
            return
            
        material_type = material_type.lower()
        
        if material_type == "plastic":
            self.plastic_count += 1
            self.total_count += 1
        elif material_type == "can":
            self.can_count += 1
            self.total_count += 1
        elif material_type == "rejected":
            self.rejected_count += 1
            # Note: rejected items don't count toward total_count
        elif material_type == "no_detection":
            self.no_detection_count += 1
            # Note: no_detection items don't count toward total_count
        else:
            self.logger.warning(f"Unknown material type detected: {material_type}")
            return
            
        self.logger.debug(f"Added {material_type} item. Current counts - "
                         f"Plastic: {self.plastic_count}, "
                         f"Can: {self.can_count}, "
                         f"Rejected: {self.rejected_count}, "
                         f"No Detection: {self.no_detection_count}")

    def get_session_data(self) -> Dict:
        """Get current session data as a dictionary"""
        return {
            'plastic_count': self.plastic_count,
            'can_count': self.can_count,
            'rejected_count': self.rejected_count,
            'no_detection_count': self.no_detection_count,
            'total_count': self.total_count
        }