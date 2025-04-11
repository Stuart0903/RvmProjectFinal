import logging
from typing import List, Dict, Tuple, Optional

class DecisionHelper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def determine_final_decision(self, image_results: List[Dict]) -> Tuple[Optional[str], float]:
        """
        Determine final decision based on the rules provided
        Args:
            image_results: List of dicts with keys 'label' and 'confidence'
        Returns:
            Tuple of (final_material, confidence)
        """
        # Count occurrences of each label
        labels = [res['label'] for res in image_results]
        counts = {
            'plastic': labels.count('plastic'),
            'can': labels.count('can'),
            'rejected': labels.count('rejected'),
            'no_detection': labels.count('no_detection')
        }
        
        # Get non-no_detection results
        valid_results = [res for res in image_results if res['label'] != 'no_detection']
        
        # Rule 1: If two or more of the same label appear, that label is chosen
        if counts['plastic'] >= 2:
            return 'plastic', self._get_average_confidence(image_results, 'plastic')
        if counts['can'] >= 2:
            return 'can', self._get_average_confidence(image_results, 'can')
        if counts['rejected'] >= 2:
            return 'rejected', self._get_average_confidence(image_results, 'rejected')
            
        # Rule 2: If all three are different, choose the one with highest confidence
        if len(valid_results) == 3 and len({res['label'] for res in valid_results}) == 3:
            best = max(valid_results, key=lambda x: x['confidence'])
            return best['label'], best['confidence']
            
        # Rule 3: If one image is "No Detection," base decision on other two
        if counts['no_detection'] == 1:
            if len(valid_results) == 2:
                if valid_results[0]['label'] == valid_results[1]['label']:
                    return valid_results[0]['label'], self._get_average_confidence(valid_results, valid_results[0]['label'])
                else:
                    best = max(valid_results, key=lambda x: x['confidence'])
                    return best['label'], best['confidence']
                    
        # Rule 4: If two images are "No Detection," use the remaining image
        if counts['no_detection'] == 2:
            if len(valid_results) == 1:
                return valid_results[0]['label'], valid_results[0]['confidence']
                
        # Rule 5: If two images are "Rejected," final result is "Rejected"
        if counts['rejected'] >= 2:
            return 'rejected', self._get_average_confidence(image_results, 'rejected')
            
        # Default case (shouldn't normally reach here)
        self.logger.warning("Unexpected case in decision making")
        if valid_results:
            best = max(valid_results, key=lambda x: x['confidence'])
            return best['label'], best['confidence']
        return None, 0.0
        
    def _get_average_confidence(self, results: List[Dict], label: str) -> float:
        """Calculate average confidence for a specific label"""
        confidences = [res['confidence'] for res in results if res['label'] == label]
        return sum(confidences) / len(confidences) if confidences else 0.0