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

LLM_MODEL = "phi3:mini"
LLM_TIMEOUT = 5 * 60
HUMAN_KEYWORDS = [
    "Reinforcement Learning",
    "Text-to-SQL"
]
HUMAN_KEYWORDS = [
    "Reinforcement Learning",
    "Text-to-SQL",
    "Fine-tuning"
]

PROMPT = """
You are an academic keyword extraction assistant.

You are provided with a set of **human-labeled keywords** as examples for this paper: {human_keywords}.

Given the research paper title below, your task is to:
1. Determine which of the human-labeled keywords are relevant to this paper.
2. Suggest 1–3 additional relevant keywords that are not in the human-labeled list.

Requirements:
- Each keyword should be short (1–3 words).
- Return **only valid JSON**, no explanations or markdown.
- The JSON must have exactly this format:

{{
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Title: "{title}"

Return ONLY the JSON object above. Include both relevant human keywords and new suggested keywords.
"""