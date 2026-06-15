# logger.py — runtime/
# Configuración global del logging rotativo y consola para el agente

import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Definir directorios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "agent_runtime.log")

# Paleta HSL y códigos ANSI de color para consola premium
class PremiumFormatter(logging.Formatter):
    # ANSI escape codes para dar una UI premium en la consola
    GREY = "\033[90m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"
    RESET = "\033[0m"

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s -> %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: CYAN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_global_logging():
    """Configura logging para toda la app. 
    Envía Info+ a consola y Debug+ al archivo rotativo logs/agent_runtime.log."""
    root_logger = logging.getLogger()
    # Evitar handlers duplicados si se llama dos veces
    if root_logger.handlers:
        return root_logger

    root_logger.setLevel(logging.DEBUG)

    # 1. Handler para Consola (Con soporte ANSI si es posible)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(PremiumFormatter())
    root_logger.addHandler(console_handler)

    # 2. Handler para Archivo Rotativo (Detallado en logs/agent_runtime.log)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] (%(name)s:%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # 5MB de tamaño máximo, guarda hasta 5 respaldos históricos
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Capturar warnings del sistema
    logging.captureWarnings(True)
    
    return root_logger

# Ejecutar configuración global en la primera importación
logger = setup_global_logging()
