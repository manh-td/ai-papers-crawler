import os
import requests
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
from timeout_decorator import timeout, TimeoutError

from .utils import logging, write_jsonl, load_jsonl
from .config import CONFERENCE_LIST, YEARS, OUTPUT_DIR


def fetch_strategy_1(url: str) -> list:
    """
    Fetch papers from a webpage using <li><a> elements as titles.
    """
    logging.debug(f"Fetching data from {url}")
    papers = []

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return papers

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))

        for paper in tqdm(dom.xpath("//li/a"), desc=f"Processing {url}"):
            titles = paper.xpath("text()")
            if not titles:
                continue

            title = titles[0].strip()
            if not title or "\n" in title:
                logging.warning(f"Invalid title skipped: {title}")
                continue

            papers.append({"title": title})
    except Exception as e:
        logging.error(f"Error parsing HTML for {url}: {e}")

    return papers


def fetch_strategy_2(url: str) -> list:
    """
    Fetch papers from a webpage using <p><strong> elements as titles.
    """
    logging.debug(f"Fetching data from {url}")
    papers = []

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from {url}: {e}")
        return papers

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        dom = etree.HTML(str(soup))

        for paper in tqdm(dom.xpath("//p/strong"), desc=f"Processing {url}"):
            titles = paper.xpath("text()")
            if not titles:
                continue

            title = titles[0].strip()
            if not title:
                continue

            papers.append({"title": title})
    except Exception as e:
        logging.error(f"Error parsing HTML for {url}: {e}")

    return papers


@timeout(seconds=18000)
def main():
    """
    Entry point for the AI Papers Crawler.
    Iterates over configured conferences and years, fetching paper titles.
    """
    logging.info("Welcome to the AI Papers Crawler!")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_papers = []

    for conference, conf_url in CONFERENCE_LIST:
        fetch_func = fetch_strategy_2 if "emnlp" in conference.lower() else fetch_strategy_1

        for year in YEARS:
            output_path = os.path.join(OUTPUT_DIR, f"{conference}{year}.jsonl")

            try:
                if os.path.exists(output_path):
                    logging.info(f"File {output_path} already exists. Skipping...")
                    papers = load_jsonl(output_path)
                else:
                    url = conf_url.format(year=year)
                    papers = fetch_func(url)

                    if papers:
                        logging.info(f"Fetched {len(papers)} papers from {url}")
                        write_jsonl(output_path, papers)
                        logging.info(f"Saved papers to {output_path}")
                    else:
                        logging.warning(f"No papers found for {url}")

                for paper in papers:
                    if paper.get("title") in ["Browse ", "Visualization"]:
                        continue

                    all_papers.append({
                        "conference": f"{conference}{year}",
                        "title": paper["title"]
                    })

            except Exception as e:
                logging.error(f"Error processing {conference} {year}: {e}")

    try:
        all_papers_path = os.path.join(OUTPUT_DIR, "all_papers.jsonl")
        write_jsonl(all_papers_path, all_papers)
        logging.info(f"Saved all papers to {all_papers_path}")
    except Exception as e:
        logging.error(f"Error writing all_papers.jsonl: {e}")


if __name__ == "__main__":
    try:
        main()
    except TimeoutError:
        logging.error("⏰ The crawling process timed out after 5 hours (18000 seconds). Exiting gracefully.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
