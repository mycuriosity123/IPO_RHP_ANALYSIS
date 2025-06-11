# logger_config.py
import logging
import os

LOGGER_NAME = "my_project_logger"


logger = logging.getLogger(LOGGER_NAME)

if not logger.handlers:
    
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, "project.log"))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    
    logger.propagate = False
