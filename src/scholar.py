import requests
import xml.etree.ElementTree as ET
from .utils import logging

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
        paper = {
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
            "summary": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
            "authors": [author.find("{http://www.w3.org/2005/Atom}name").text.strip() for author in entry.findall("{http://www.w3.org/2005/Atom}author")],
            "published": entry.find("{http://www.w3.org/2005/Atom}published").text.strip(),
            "link": entry.find("{http://www.w3.org/2005/Atom}id").text.strip()
        }
        return paper

    logging.warning(f"No results found for title: {title}")
    return {}

if __name__ == "__main__":
    title = "Graph Neural Networks"
    paper = search_paper_by_title(title)
    print(f"Title: {paper['title']}")
    print(f"Summary: {paper['summary']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"Published: {paper['published']}")
    print(f"Link: {paper['link']}")
    print()