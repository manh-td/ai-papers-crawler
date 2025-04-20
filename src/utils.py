# import logging
# import os
import json
# from .config import (
#     LOGS_DIR,
#     PRODUCT,
# )

# os.makedirs(LOGS_DIR, exist_ok=True)
# log_file_path = os.path.join(LOGS_DIR, 'logs.log')
# logging.basicConfig(
#     force=True,
#     level=logging.INFO if PRODUCT else logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
#     handlers=[
#         logging.FileHandler(log_file_path),
#     ] if PRODUCT else [
#         logging.FileHandler(log_file_path),
#         logging.StreamHandler()
#     ]
# )

def write_jsonl(file_path, data):
    """
    Write a list of dictionaries to a JSONL file.

    :param file_path: Path to the JSONL file.
    :param data: List of dictionaries to write.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')

def write_json(file_path, data):
    """
    Write a dictionary or list to a JSON file.

    :param file_path: Path to the JSON file.
    :param data: Dictionary or list to write.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_jsonl(file_path):
    """
    Load a JSONL file and return a list of dictionaries.

    :param file_path: Path to the JSONL file.
    :return: List of dictionaries.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data