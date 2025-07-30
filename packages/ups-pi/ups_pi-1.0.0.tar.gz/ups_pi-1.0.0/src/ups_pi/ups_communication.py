"""uart communication with upspack v3 devices"""

import time
import logging
import re
from typing import Tuple, Optional, Any, Union, TYPE_CHECKING
from pathlib import Path
from dataclasses import dataclass

try:
    import serial
    from serial import Serial
    SERIAL_AVAILABLE = True
except ImportError:
    serial = None  # type: ignore
    Serial = None  # type: ignore
    SERIAL_AVAILABLE = False


class UPSCommunicationError(Exception):
    """ups communication failure"""
    pass


class UPSDataError(Exception):
    """invalid ups data"""
    pass


@dataclass
class UPSStatus:
    """ups status data"""
    firmware_version: str
    power_status: str
    battery_percentage: int
    voltage_mv: int
    raw_data: str
    timestamp: float


class UPSDevice:
    """uart communication with ups device"""
    
    # UART communication constants
    DEFAULT_PORT = "/dev/ttyAMA0"
    DEFAULT_BAUDRATE = 9600
    DEFAULT_TIMEOUT = 2.0
    
    # Data validation patterns
    FIRMWARE_PATTERN = re.compile(r'^[A-Za-z0-9._\-\s\$]+$')  # Allow spaces, $ symbol
    STATUS_PATTERN = re.compile(r'^(External|Battery|Charging|Unknown)$')
    
    def __init__(
        self,
        port: str = DEFAULT_PORT,
        baudrate: int = DEFAULT_BAUDRATE,
        timeout: float = DEFAULT_TIMEOUT,
        logger: Optional[logging.Logger] = None
    ):
        """initialize ups communication"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.logger = logger or logging.getLogger(__name__)
        
        self._serial_connection = None
        self._is_open = False
        
        if not SERIAL_AVAILABLE:
            raise UPSCommunicationError(
                "pyserial library not available. Install with: pip install pyserial"
            )
    
    def __enter__(self) -> 'UPSDevice':
        """context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """context manager exit"""
        self.close()
    
    def open(self) -> None:
        """open serial connection"""
        if self._is_open:
            self.logger.warning("UPS connection already open")
            return
        
        try:
            self.logger.info(f"Opening UPS connection: {self.port} @ {self.baudrate} baud")
            
            self._serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            if not self._serial_connection.is_open:
                raise UPSCommunicationError("Failed to open serial connection")
            
            self._is_open = True
            self.logger.info("UPS connection established successfully")
            
            self._serial_connection.reset_input_buffer()
            self._serial_connection.reset_output_buffer()
            
        except serial.SerialException as e:
            raise UPSCommunicationError(f"Serial connection failed: {e}")
        except Exception as e:
            raise UPSCommunicationError(f"Unexpected error opening connection: {e}")
    
    def close(self) -> None:
        """close serial connection"""
        if not self._is_open:
            return
        
        try:
            if self._serial_connection and self._serial_connection.is_open:
                self._serial_connection.close()
                self.logger.info("UPS connection closed")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
        finally:
            self._serial_connection = None
            self._is_open = False
    
    def is_connected(self) -> bool:
        """check if device is connected"""
        return (
            self._is_open and 
            self._serial_connection is not None and 
            self._serial_connection.is_open
        )
    
    def read_status(self, retries: int = 3) -> UPSStatus:
        """read current ups status"""
        if not self.is_connected():
            raise UPSCommunicationError("UPS device not connected")
        
        last_error = None
        
        for attempt in range(retries + 1):
            try:
                self.logger.debug(f"Reading UPS status (attempt {attempt + 1})")
                
                self._serial_connection.reset_input_buffer()
                raw_data = self._serial_connection.readline()
                
                if not raw_data:
                    raise UPSCommunicationError("No data received from UPS")
                
                data_str = raw_data.decode('utf-8', errors='ignore').strip()
                
                if not data_str:
                    raise UPSDataError("Empty data received")
                
                status = self._parse_status_data(data_str)
                self.logger.debug(f"UPS status read successfully: {status}")
                return status
                
            except (UPSCommunicationError, UPSDataError) as e:
                last_error = e
                if attempt < retries:
                    self.logger.warning(f"UPS read attempt {attempt + 1} failed: {e}")
                    time.sleep(0.1)
                    continue
                break
            except Exception as e:
                last_error = UPSCommunicationError(f"Unexpected error: {e}")
                break
        
        error_msg = f"Failed to read UPS status after {retries + 1} attempts"
        if last_error:
            error_msg += f": {last_error}"
        
        self.logger.error(error_msg)
        raise UPSCommunicationError(error_msg)
    
    def _parse_status_data(self, data: str) -> UPSStatus:
        """parse raw ups data string"""
        try:
            parts = data.split(',')
            
            if len(parts) != 4:
                raise UPSDataError(f"Invalid data format: expected 4 parts, got {len(parts)}")
            
            firmware, status, battery_str, voltage_str = parts
            
            firmware = firmware.strip()
            if not firmware or not self.FIRMWARE_PATTERN.match(firmware):
                raise UPSDataError(f"Invalid firmware format: {firmware}")
            
            status = status.strip()
            if not self.STATUS_PATTERN.match(status):
                status_lower = status.lower()
                if 'ext' in status_lower or 'ac' in status_lower:
                    status = "External"
                elif 'bat' in status_lower:
                    status = "Battery"
                elif 'charg' in status_lower:
                    status = "Charging"
                else:
                    status = "Unknown"
            
            try:
                battery_percentage = int(battery_str.strip().rstrip('%'))
                if not 0 <= battery_percentage <= 100:
                    raise ValueError("Battery percentage out of range")
            except ValueError as e:
                raise UPSDataError(f"Invalid battery percentage: {battery_str}")
            
            # Parse voltage
            try:
                voltage_mv = int(voltage_str.strip())
                if voltage_mv < 0:
                    raise ValueError("Negative voltage")
            except ValueError as e:
                raise UPSDataError(f"Invalid voltage: {voltage_str}")
            
            return UPSStatus(
                firmware_version=firmware,
                power_status=status,
                battery_percentage=battery_percentage,
                voltage_mv=voltage_mv,
                raw_data=data,
                timestamp=time.time()
            )
            
        except UPSDataError:
            raise
        except Exception as e:
            raise UPSDataError(f"Failed to parse UPS data '{data}': {e}")


# Legacy compatibility - maintain interface from original ups2.py
class UPS2(UPSDevice):
    """Legacy compatibility class - use UPSDevice instead."""
    
    def __init__(self, port: str = "/dev/ttyAMA0", **kwargs):
        super().__init__(port=port, **kwargs)
        self.logger.warning("UPS2 class is deprecated, use UPSDevice instead")
    
    def decode_uart(self) -> Tuple[str, str, int, int]:
        """Legacy method - returns tuple format."""
        if not self.is_connected():
            self.open()
        
        status = self.read_status()
        return (
            status.firmware_version,
            status.power_status,
            status.battery_percentage,
            status.voltage_mv
        )
