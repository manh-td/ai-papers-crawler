import requests
import xml.etree.ElementTree as ET
from .utils import logging, load_jsonl, write_jsonl
import time
import json
from tqdm import tqdm
from .config import (
    ALL_PAPERS_DIR,
)
import os

def search_paper_by_title(title, start=0, max_results=1) -> dict:
    """
    Search for papers on arXiv by title.

    Args:
        title (str): The title or keywords to search for.
        start (int): The starting index for the search results.
        max_results (int): The maximum number of results to fetch.

    Returns:
        list: A list of dictionaries containing paper details.
    """
    logging.debug(f"Searching for papers with title: {title}")
    base_url = "http://export.arxiv.org/api/query"
    query = f"search_query=all:{title}&start={start}&max_results={max_results}"
    url = f"{base_url}?{query}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from arXiv API. Status code: {response.status_code}")

    root = ET.fromstring(response.content)

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        authors = [
            author.find("{http://www.w3.org/2005/Atom}name").text.replace("\n", "").strip()
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
        ]
        if len(authors) > 3:
            authors = [authors[0], authors[1], authors[-1]]
        paper = {
            "link": entry.find("{http://www.w3.org/2005/Atom}id").text.replace("\n", "").strip(),
            "subject": entry.find("{http://arxiv.org/schemas/atom}primary_category").attrib.get("term", "").strip(),
            "authors": authors
        }
        return paper

    logging.warning(f"No results found for title: {title}")
    return None

def main():
    papers = load_jsonl(ALL_PAPERS_DIR)
    output_file = ALL_PAPERS_DIR.replace(".jsonl", "_arxiv.jsonl")
    checked_papers = load_jsonl(output_file) if os.path.exists(output_file) else []
    for paper in tqdm(papers, desc="Processing papers"):
        title = paper["title"]
        if any(paper["title"] == p["title"] for p in checked_papers):
            logging.info(f"Paper already checked: {paper['title']}")
            continue

        arxiv_paper = search_paper_by_title(title)
        time.sleep(3)
        if arxiv_paper:
            paper.update(arxiv_paper)
            logging.info(f"Updated paper: {json.dumps(paper, indent=4)}")
        write_jsonl(output_file, [paper], mode="a")

    logging.info(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()