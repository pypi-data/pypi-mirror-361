import logging
import sys
from pathlib import Path
from typing import Optional

class CliOpsLogger:
    """Centralized logging for CliOps with structured output"""
    
    _instance: Optional['CliOpsLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger = logging.getLogger('cliops')
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure logger with console and file handlers"""
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        
        # File handler
        log_dir = Path.home() / '.cliops' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_dir / 'cliops.log')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def set_verbose(self, verbose: bool = True):
        """Enable/disable verbose console logging"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                handler.setLevel(logging.DEBUG if verbose else logging.WARNING)
    
    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self.logger.info(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self.logger.error(msg, **kwargs)
    
    def critical(self, msg: str, **kwargs):
        self.logger.critical(msg, **kwargs)

# Global logger instance
logger = CliOpsLogger()