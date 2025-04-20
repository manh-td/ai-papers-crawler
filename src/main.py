from .utils import logging, write_jsonl, load_jsonl
from .scholar import search_paper_by_title
import requests
import os
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm  # Import tqdm for progress bars
from .config import (
    CONFERENCE_LIST,
    YEARS,
    OUTPUT_DIR
)

def fetch_strategy_1(url:str) -> list:
    """
    Fetch papers from a given conference and year.
    """
    logging.debug(f"Fetching papers from {url}")
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from {url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    logging.debug(soup)
    dom = etree.HTML(str(soup))

    papers = []
    for paper in tqdm(dom.xpath("//li/a"), desc=f"Processing {url}"):  # Adjust XPath based on the actual structure
        title = paper.xpath("text()")[0]
        if "\n" in title:
            logging.warning(f"Title contains newline character: {title}")
            continue
        # logging.debug(f"Processing paper: {title}")
        # arxiv_paper = search_paper_by_title(title)
        # if not arxiv_paper:
        #     continue

        # if title.lower() != arxiv_paper['title'].lower():
        #     logging.warning(f"Title mismatch: {title} != {arxiv_paper['title']}")
        # papers.append(arxiv_paper)
        papers.append({
            "title": title,
        })

    return papers

def fetch_strategy_2(url:str) -> list:
    """
    Fetch papers from a given conference and year.
    """
    logging.debug(f"Fetching papers from {url}")
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch data from {url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    logging.debug(soup)
    dom = etree.HTML(str(soup))

    papers = []
    for paper in tqdm(dom.xpath("//p/strong"), desc=f"Processing {url}"):  # Adjust XPath based on the actual structure
        title = paper.xpath("text()")[0]
        # arxiv_paper = search_paper_by_title(title)
        # if not arxiv_paper:
        #     continue
        # if title.lower() != arxiv_paper['title'].lower():
        #     logging.warning(f"Title mismatch: {title} != {arxiv_paper['title']}")
        # papers.append(arxiv_paper)
        papers.append({
            "title": title,
        })

    return papers

def main():
    """
    Entry point for the application.
    """
    logging.info("Welcome to the AI Papers Crawler!")

    all_papers = []

    for conference, conf_url in CONFERENCE_LIST:
        fetch_func = fetch_strategy_2 if "emnlp" in conference else fetch_strategy_1
        for year in YEARS:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            output_dir = f"{OUTPUT_DIR}/{conference}{year}.jsonl"
            
            if os.path.exists(output_dir):
                logging.info(f"File {output_dir} already exists. Skipping...")
                papers = load_jsonl(output_dir)
            else:
                url = conf_url.format(year=year)
                papers = fetch_func(url)

                if papers:
                    logging.info(f"Fetched {len(papers)} papers from {url}")
                    write_jsonl(output_dir, papers)
                    logging.info(f"Saved papers to {output_dir}")
                else:
                    logging.warning(f"No papers found for {url}")
            
            for paper in papers:
                all_papers.append({
                    "conference": f"{conference}{year}",
                    "title": paper['title'],
                })

    write_jsonl(f"{OUTPUT_DIR}/all_papers.jsonl", all_papers)

if __name__ == "__main__":
    main()