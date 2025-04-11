import time
import logging
import threading
from queue import Queue, Empty
from pathlib import Path

from controllers.recycling_controller import RecyclingSession
from services.qr_service import QRService
from ui.main_ui import RVMachineUI
from .config.settings import Settings
from .controllers.camera_controller import CameraController
from .controllers.serial_controller import SerialController
from .services.detection_service import DetectionService
from .services.logging_service import setup_logging

class MainController:
    def __init__(self, settings: Settings):
        self.settings = settings
        setup_logging(settings)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Reverse Vending Machine System")
        
        # Initialize hardware controllers
        self.camera = CameraController(settings)
        self.serial = SerialController(settings)
        self.detector = DetectionService(settings)
        
        # Initialize recycling session and QR service
        self.recycling_session = RecyclingSession()
        self.qr_service = QRService(settings)
        
        # Communication queues with UI
        self.ui_command_queue = Queue()
        self.ui_response_queue = Queue()
        
        # System state variables
        self.processing = False
        self.detection_count = 0
        self.servo_activations = 0
        self.session_active = False
        self.last_detection_time = 0
        self.should_exit = False

    def run(self):
        self.logger.info("RVMachine system started")
        
        # Start the UI in a separate thread

        ui_thread = threading.Thread(
            target=self._run_ui,
            args=(self.ui_command_queue, self.ui_response_queue),
            daemon=True
        )
        ui_thread.start()
        
        try:
            # Initial delay to let Arduino initialize
            time.sleep(3)
            
            while not self.should_exit:
                self._check_session_timeout()
                self._process_ui_commands()
                
                # Read serial messages
                message = self.serial.read_line()
                if message:
                    self.logger.info(f"Arduino message: {message}")
                    
                    # Process detection during active session
                    if "OBJECT_DETECTED" in message and self.session_active and not self.processing:
                        self.detection_count += 1
                        self.logger.info(f"Detection #{self.detection_count}")
                        
                        self.processing = True
                        self._handle_detection()
                        self.processing = False
                
                # Small delay to prevent CPU hogging
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down system")
            self.ui_response_queue.put("SYSTEM_SHUTDOWN")
        finally:
            self.camera.release()
            self.serial.close()
            self.should_exit = True

    def _run_ui(self, command_queue, response_queue):
        """Run the UI in the main thread (required for Tkinter)"""

        ui = RVMachineUI(command_queue, response_queue)
        ui.run()

    def _process_ui_commands(self):
        """Process commands from the UI"""
        try:
            command = self.ui_command_queue.get_nowait()
            
            if command == "START_SESSION":
                self._start_new_session()
            elif command == "END_SESSION":
                self._end_session()
            elif command == "QUIT":
                self.should_exit = True
            
        except Empty:
            pass

    def _start_new_session(self):
        """Start a new recycling session"""
        self.session_active = True
        self.recycling_session.reset_session()
        self.last_detection_time = time.time()
        self.detection_count = 0
        self.logger.info("New recycling session started")
        self.ui_response_queue.put("SESSION_STARTED")

    def _handle_detection(self):
        """Handle the complete detection pipeline"""
        try:
            self.last_detection_time = time.time()
            
            # Capture images
            self.logger.info("Capturing images")
            image_paths = self.camera.capture_images()
            if not image_paths:
                self.logger.warning("No images captured")
                return
            
            # Process detection
            self.logger.info("Processing images with AI model")
            detection_made, summary = self.detector.process_images(image_paths)
            print(f"\n{summary}")  # Keep the detailed summary output
            
            # Determine material type from detection results
            material = self._determine_material(summary, detection_made)
            result_text = ""
            
            if not detection_made:
                if "NO VALID DETECTION" in summary:
                    result_text = "Item rejected: Confidence too low"
                    material = "rejected"
                else:
                    result_text = "No object detected"
                    material = "no_detection"
            else:
                result_text = f"Item accepted: {material}"
            
            # Update session counts with the detected material
            if material:
                self.recycling_session.add_item(material)
                
                # Only activate servo for valid materials (plastic or can)
                if material in ["plastic", "can"]:
                    # Activate servo
                    self.servo_activations += 1
                    self.serial.write("ACTIVATE_SERVO")
                    
                    # Wait for servo confirmation
                    if not self._wait_for_servo_confirmation():
                        result_text = "Error processing item"
                        self.logger.warning("Servo activation not confirmed")
            
            # Update UI with detection result and latest counts
            self.ui_response_queue.put(f"DETECTION_RESULT:{result_text}")
            
            # Get updated counts and send to UI
            counts = self.recycling_session.get_session_data()
            self.ui_response_queue.put(f"SESSION_DATA:{counts}")
            
            # System stabilization delay
            time.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Detection error: {str(e)}", exc_info=True)
            self.ui_response_queue.put(f"DETECTION_RESULT:Error: {str(e)}")

    def _determine_material(self, summary: str, detection_made: bool) -> str:
        """Determine material type from detection summary"""
        if not detection_made:
            if "NO VALID DETECTION" in summary:
                return "rejected"
            return "no_detection"
            
        # Extract material from the FINAL CLASSIFICATION line
        summary_lines = summary.split('\n')
        for line in summary_lines:
            if "FINAL CLASSIFICATION:" in line:
                if "PLASTIC" in line:
                    return "plastic"
                elif "CAN" in line:
                    return "can"
        
        # If we can't determine from FINAL CLASSIFICATION, fall back to old method
        summary_lower = summary.lower()
        if "plastic" in summary_lower:
            return "plastic"
        elif "can" in summary_lower:
            return "can"
            
        return "rejected"

    def _wait_for_servo_confirmation(self, timeout: float = 3.0) -> bool:
        """Wait for servo activation confirmation"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.serial.read_line()
            if response and "SERVO_ACTIVATED" in response:
                return True
            time.sleep(0.1)
        return False

    def _end_session(self):
        """End the current recycling session"""
        if not self.session_active:
            return
            
        self.logger.info("Ending recycling session")
        
        # Get session data
        counts = self.recycling_session.get_session_data()
        
        try:
            # Generate QR image and get qr_id
            qr_image, qr_id = self.qr_service.generate_qr_image(counts)
            
            if qr_image and qr_id:
                # Save the QR code to file (optional)
                qr_path = self.qr_service.generate_qr_code(counts)
                
                # Tell UI to display QR window with all required data
                self.ui_response_queue.put("DISPLAY_QR")
                self.ui_response_queue.put((qr_image, counts, qr_id))
            else:
                self.logger.error("QR image generation failed")
                self.ui_response_queue.put("QR_GENERATION_FAILED")
        except Exception as e:
            self.logger.error(f"QR generation failed: {str(e)}")
            self.ui_response_queue.put("QR_GENERATION_FAILED")
        
        # Reset for next user
        self.session_active = False
        self.recycling_session.reset_session()
        self.serial.write("SESSION_ENDED")

    def _check_session_timeout(self):
        """Check if session should timeout due to inactivity"""
        if (self.session_active and 
            time.time() - self.last_detection_time > self.settings.SESSION_TIMEOUT):
            self.logger.info("Session timeout - ending session")
            self._end_session()

if __name__ == "__main__":
    settings = Settings()
    controller = MainController(settings)
    controller.run()