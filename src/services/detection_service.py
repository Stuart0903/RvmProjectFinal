import logging
from typing import Tuple, List, Dict
from pathlib import Path
from collections import Counter

from utils.detection_helper import DecisionHelper

from ..config.settings import Settings
from ..models.object_detector import ObjectDetector

class DetectionService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.detector = ObjectDetector(settings)
        self.decision_helper = DecisionHelper()  # Add this line
        self.CONFIDENCE_THRESHOLD = settings.CONFIDENCE_THRESHOLD
        self.REJECTION_THRESHOLD = 0.85  # Minimum confidence to accept a detection
        
    def process_images(self, image_paths: List[str]) -> Tuple[bool, str]:
        """
        Process multiple images and determine the final classification
        Returns tuple of (detection_made, summary)
        """
        # Track detections across all images
        all_image_results = []  # Changed from all_image_detections
        material_counts = {"plastic": 0, "can": 0, "rejected": 0, "no_detection": 0}
        confidence_sums = {"plastic": 0.0, "can": 0.0}
        
        # Process each image
        for i, image_path in enumerate(image_paths):
            try:
                self.logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
                
                # Get detection results for this image
                results = self.detector.detect_objects(image_path)
                
                # Store the best detection for this image
                image_result = None
                
                # Process each detection in this image
                for result in results:
                    for box in result.boxes:
                        cls = int(box.cls[0])  # class index
                        conf = float(box.conf[0])  # confidence score
                        label = result.names[cls]  # class name
                        
                        # Only consider detections that match our material types
                        if label.lower() in self.settings.MATERIAL_TYPES:
                            # Track the best detection in this image
                            if image_result is None or conf > image_result['confidence']:
                                image_result = {
                                    'label': label.lower(),
                                    'confidence': conf,
                                    'class_id': cls
                                }
                
                # Handle the detection logic for this image
                if image_result is None:
                    # No objects detected in this image
                    image_result = {'label': 'no_detection', 'confidence': 0.0}
                    material_counts["no_detection"] += 1
                    self.logger.info(f"Image {i+1}: No detection")
                else:
                    # Check if the detection meets the rejection threshold
                    if image_result['confidence'] < self.REJECTION_THRESHOLD:
                        image_result['label'] = 'rejected'
                        material_counts["rejected"] += 1
                        self.logger.info(f"Image {i+1}: Rejected (confidence: {image_result['confidence']:.2f})")
                    else:
                        # Valid detection
                        material = image_result['label']
                        material_counts[material] += 1
                        confidence_sums[material] += image_result['confidence']
                        self.logger.info(f"Image {i+1}: Detected {material} (confidence: {image_result['confidence']:.2f})")
                
                # Add this image's result to our collection
                all_image_results.append(image_result)
                
            except Exception as e:
                self.logger.error(f"Error processing {image_path}: {str(e)}", exc_info=True)
                all_image_results.append({'label': 'rejected', 'confidence': 0.0})
                material_counts["rejected"] += 1
        
        # Determine final classification using the helper
        final_material, final_confidence = self.decision_helper.determine_final_decision(all_image_results)
        
        # Consider detection successful if we have a valid material and good confidence
        detection_made = final_material is not None and final_material not in ['rejected', 'no_detection'] and final_confidence >= self.CONFIDENCE_THRESHOLD
        
        # Generate detailed summary
        summary = self._generate_summary(all_image_results, material_counts, 
                                       final_material, final_confidence)
        
        return detection_made, summary
    
    def _generate_summary(self, 
                         all_image_results: List[Dict], 
                         material_counts: Dict[str, int],
                         final_material: str,
                         final_confidence: float) -> str:
        """Generate a detailed summary of all detections and final classification"""
        summary = "Detection Results:\n"
        
        # Per-image summary
        for i, image_result in enumerate(all_image_results):
            summary += f"\nImage {i+1}:\n"
            summary += f"  - {image_result['label']} (confidence: {image_result['confidence']:.2f})\n"
        
        # Summary statistics
        summary += "\nDetection Statistics:\n"
        summary += f"  - Plastic detections: {material_counts['plastic']}\n"
        summary += f"  - Can detections: {material_counts['can']}\n"
        summary += f"  - Rejected detections: {material_counts['rejected']}\n"
        summary += f"  - No detections: {material_counts['no_detection']}\n"
        
        # Final classification
        if final_material:
            summary += f"\nFINAL CLASSIFICATION: {final_material.upper()} (confidence: {final_confidence:.2f})\n"
        else:
            summary += "\nFINAL CLASSIFICATION: NO VALID DETECTION\n"
            
        return summary