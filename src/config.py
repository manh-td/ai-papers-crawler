from datetime import datetime

LOGS_DIR = "./logs"
OUTPUT_DIR = "./outputs"
PRODUCT = True

current_year = datetime.now().year
YEARS = list(range(current_year, 2017, -1))

CONFERENCE_LIST = [
    ("iclr", "https://iclr.cc/virtual/{year}/papers.html?layout=detail"),
    ("neurips", "https://neurips.cc/virtual/{year}/papers.html?layout=detail"),
    ("icml", "https://icml.cc/virtual/{year}/papers.html?layout=detail"),
    ("emnlp", "https://{year}.emnlp.org/program/accepted_main_conference/")
]

ALL_PAPERS_DIR = "outputs/all_papers.jsonl"