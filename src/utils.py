import logging
import os
import json
from .config import (
    LOGS_DIR,
    PRODUCT,
)

os.makedirs(LOGS_DIR, exist_ok=True)
log_file_path = os.path.join(LOGS_DIR, 'logs.log')
logging.basicConfig(
    force=True,
    level=logging.INFO if PRODUCT else logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
    ] if PRODUCT else [
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

def write_jsonl(file_path, data):
    """
    Write a list of dictionaries to a JSONL file.

    :param file_path: Path to the JSONL file.
    :param data: List of dictionaries to write.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')