"""
Centralized Logging Utilities for the DPI System.

This module provides a LoggingManager to create and manage loggers for all
system components, including module-specific file logging for metadata.
"""
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from src.core.packet import Packet


class JSONOnlyLogger:
    """
    Logger that only writes JSON data to files, no info/debug messages.
    Used for module log files that should only contain per-packet JSON logs.
    """
    
    def __init__(self, log_file: str, max_size_mb: int = 10, backup_count: int = 5):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.backup_count = backup_count
        
    def log_json(self, data: Dict[str, Any]) -> None:
        """Write JSON data to log file with rotation"""
        try:
            # Check if rotation is needed
            if self.log_file.exists() and self.log_file.stat().st_size > self.max_size_bytes:
                self._rotate_log()
            
            with open(self.log_file, "a", encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
        except Exception as e:
            # Fallback to console if file logging fails
            print(f"JSON logging error: {e}")
    
    def _rotate_log(self) -> None:
        """Rotate log files"""
        try:
            for i in range(self.backup_count - 1, 0, -1):
                old_file = self.log_file.with_suffix(f".{i}")
                new_file = self.log_file.with_suffix(f".{i + 1}")
                if old_file.exists():
                    old_file.rename(new_file)
            
            if self.log_file.exists():
                self.log_file.rename(self.log_file.with_suffix(".1"))
        except Exception as e:
            print(f"Log rotation error: {e}")


class LoggingManager:
    """
    Centralized logging manager for the DPI system.
    Provides three main log files: system.log, packet_capture.log, dpi_engine.log.
    Use get_logger(component_name) to get the correct logger for any module or submodule.
    """
    LOG_FILE_MAP = {
        # DPI Engine and submodules
        'dpi_engine': 'dpi_engine',
        'DPIEngine': 'dpi_engine',
        'ProtocolIdentifier': 'dpi_engine',
        'EncryptedAnalyzer': 'dpi_engine',
        'SignatureMatcher': 'dpi_engine',
        # Packet Capture and submodules
        'packet_capture': 'packet_capture',
        'LivePacketCapture': 'packet_capture',
        'MulticastListener': 'packet_capture',
        'FilterEngine': 'packet_capture',
        'PacketBuffer': 'packet_capture',
        # System
        'system': 'system',
        'MulticastDPISystem': 'system',
        'SystemManager': 'system',
        # Traffic Classification
        'TrafficClassifier': 'traffic_classification',

        # Policy Manager
        'policy_manager': 'policy_manager',
        'PolicyManager': 'policy_manager',
        
        # Config Generator
        'config_generator': 'config_generator',
        'CiscoConfigGenerator': 'config_generator',
    }

    def __init__(self, config: Dict[str, Any]):
        self.log_dir = Path(config.get('log_directory', 'logs'))
        self.log_dir.mkdir(exist_ok=True)
        self.log_level = config.get('level', 'INFO').upper()
        self.max_size_mb = config.get('max_file_size_mb', 10)
        self.backup_count = config.get('rotation', 5)
        self._loggers: Dict[str, logging.Logger] = {}
        self._json_loggers: Dict[str, JSONOnlyLogger] = {}
        self._setup_console_logger()

    def _setup_console_logger(self):
        console_logger = logging.getLogger('console')
        if not console_logger.handlers:
            console_logger.setLevel(self.log_level)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)-5.5s] --- %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            console_logger.addHandler(handler)
        self._loggers['console'] = console_logger

    def get_logger(self, component_name: str) -> logging.Logger:
        log_file_key = self.LOG_FILE_MAP.get(component_name, 'system')
        
        # For module log files (packet_capture, dpi_engine), return console-only logger
        if log_file_key in ['packet_capture', 'dpi_engine']:
            # Return console logger for info/debug messages
            return self._loggers['console']
        
        # For system logs, return normal file logger
        if log_file_key in self._loggers:
            return self._loggers[log_file_key]
        logger = logging.getLogger(log_file_key)
        logger.setLevel(self.log_level)
        logger.propagate = False
        log_file = self.log_dir / f"{log_file_key}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_size_mb * 1024 * 1024,
            backupCount=self.backup_count
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self._loggers[log_file_key] = logger
        return logger

    def get_json_logger(self, component_name: str) -> JSONOnlyLogger:
        """Get JSON-only logger for module log files"""
        log_file_key = self.LOG_FILE_MAP.get(component_name, 'system')
        
        if log_file_key not in self._json_loggers:
            log_file = self.log_dir / f"{log_file_key}.log"
            self._json_loggers[log_file_key] = JSONOnlyLogger(
                str(log_file),
                max_size_mb=self.max_size_mb,
                backup_count=self.backup_count
            )
        
        return self._json_loggers[log_file_key]

    def get_console_logger(self) -> logging.Logger:
        return self._loggers['console']


class PacketLogger:
    """Dedicated packet logger for raw packet data (not module logs)."""
    def __init__(self, log_file: str = "logs/packet_capture.log", format_type: str = "json", max_size_mb: int = 10, rotation_count: int = 5):
        self.log_file = Path(log_file)
        self.format_type = format_type.lower()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.rotation_count = rotation_count
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_packet(self, packet: 'Packet') -> None:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "src_ip": packet.src_ip,
            "dst_ip": packet.dst_ip,
            "src_port": packet.src_port,
            "dst_port": packet.dst_port,
            "protocol": packet.protocol,
            "length": packet.length,
            "payload_sample": (packet.payload[:64].hex() if packet.payload else ""),
            "is_multicast": packet.is_multicast,
            "metadata": {
                "capture_time": packet.timestamp,
                "interface": packet.interface,
                "packet_length": packet.length
            }
        }
        with open(self.log_file, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_data) + "\n")