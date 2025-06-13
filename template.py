import os
from pathlib import Path
from logger_config import logger



list_of_files = [
    "src/__init__.py",
    "src/run_local.py",
    "src/helper.py",
    "model/instruction.txt",
    "requirements.txt",
    "setup.py",
    "main.py",
    ".env",
    "logger_config.py",
    "research/trials.ipynb",
    "Dockerfile",
    ".dockerignore",

]



for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)


    if filedir !="":
        os.makedirs(filedir, exist_ok=True)
        logger.info(f"Creating directory; {filedir} for the file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logger.info(f"Creating empty file: {filepath}")


    else:
        logger.info(f"{filename} is already exists")