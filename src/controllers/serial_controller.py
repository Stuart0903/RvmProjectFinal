import time
import serial
import logging
from typing import Optional, Union
from ..config.settings import Settings

class SerialController:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.serial_conn = None
        self.input_buffer = ""
        self._initialize_serial()

    @property
    def is_connected(self) -> bool:
        """Check if serial connection is active"""
        return self.serial_conn is not None and self.serial_conn.is_open

    @property
    def in_waiting(self) -> int:
        """Return the number of bytes in the input buffer"""
        return self.serial_conn.in_waiting if self.is_connected else 0

    def _initialize_serial(self):
        """Initialize serial connection with error handling and retry logic"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                self.serial_conn = serial.Serial(
                    port=self.settings.SERIAL_PORT,
                    baudrate=self.settings.BAUD_RATE,
                    timeout=self.settings.SERIAL_TIMEOUT,
                    write_timeout=self.settings.SERIAL_TIMEOUT
                )
                # Flush any pending data
                self.serial_conn.reset_input_buffer()
                self.serial_conn.reset_output_buffer()
                self.logger.info(f"Serial connection established on {self.settings.SERIAL_PORT}")
                return
            except serial.SerialException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"Failed to initialize serial after {max_retries} attempts")
                    raise

    def read_line(self) -> Optional[str]:
        """Read a complete line from serial with improved reliability"""
        if not self.is_connected:
            self.logger.warning("Cannot read - serial connection not established")
            return None

        try:
            # Read all available bytes
            while self.in_waiting > 0:
                byte = self.serial_conn.read(1).decode('utf-8', errors='ignore')
                if byte == '\n':
                    line = self.input_buffer.strip()
                    self.input_buffer = ""
                    if line:
                        self.logger.debug(f"Received: {line}")
                        return line
                else:
                    self.input_buffer += byte
        except Exception as e:
            self.logger.error(f"Serial read error: {str(e)}")
            # Attempt to recover connection
            self._reconnect()
        
        return None

    def write(self, data: Union[str, bytes]):
        """Write data to serial with enhanced error handling"""
        if not self.is_connected:
            self.logger.warning("Cannot write - serial connection not established")
            return False

        try:
            # Convert to bytes if needed
            if isinstance(data, str):
                if not data.endswith('\n'):
                    data = f"{data}\n"
                data = data.encode('utf-8')
            
            self.serial_conn.write(data)
            self.serial_conn.flush()
            self.logger.debug(f"Sent: {data.decode('utf-8').strip()}")
            return True
        except serial.SerialTimeoutException:
            self.logger.warning("Write timeout - data not sent")
            return False
        except Exception as e:
            self.logger.error(f"Serial write error: {str(e)}")
            self._reconnect()
            return False

    def _reconnect(self):
        """Attempt to reconnect to serial port"""
        self.close()
        self.logger.info("Attempting to reconnect to serial port...")
        try:
            self._initialize_serial()
            if self.is_connected:
                self.logger.info("Serial connection reestablished")
            else:
                self.logger.error("Failed to reconnect to serial port")
        except Exception as e:
            self.logger.error(f"Reconnection failed: {str(e)}")

    def close(self):
        """Close serial connection safely"""
        if self.is_connected:
            try:
                self.serial_conn.close()
                self.logger.info("Serial connection closed")
            except Exception as e:
                self.logger.error(f"Error closing serial connection: {str(e)}")
            finally:
                self.serial_conn = None
                self.input_buffer = ""