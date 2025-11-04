from pathlib import Path
import subprocess
import json
from tqdm import tqdm
from .utils import load_jsonl, write_json, logging
from .config import ALL_PAPERS_DIR, OUTPUT_DIR, LLM_MODEL, LLM_TIMEOUT, PROMPT, HUMAN_KEYWORDS

def extract_keywords_with_ollama(title: str, model: str = LLM_MODEL) -> list:
    """
    Use Ollama via subprocess to extract a list of keywords from a paper title.
    Returns a list of keywords, or ['Error'] on failure.
    """
    prompt = PROMPT.format(
        human_keywords=", ".join(HUMAN_KEYWORDS),
        title=title
    )

    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=LLM_TIMEOUT
        )

        if result.returncode != 0:
            logging.error(f"Ollama error for title: {title}\n{result.stderr.strip()}")
            return ["Error"]

        output = result.stdout.strip()
        # Try to extract JSON safely
        try:
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
        except Exception:
            return None

        # Try to parse JSON output
        try:
            data = json.loads(output[json_start:json_end])
            keywords = data.get("keywords", [])
            if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
                return [k.strip() for k in keywords if k.strip()]
            else:
                logging.warning(f"Unexpected format for title '{title}': {output}")
                return []
        except json.JSONDecodeError:
            logging.warning(f"Failed to parse JSON for title '{title}': {output}")
            return []

    except subprocess.TimeoutExpired:
        logging.error(f"Ollama request timed out for title: {title}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error while extracting keywords for '{title}': {e}")
        return []


def main():
    """
    Loads all paper titles and uses Ollama to extract keywords for each.
    Caches results per paper to avoid redundant calls.
    """
    logging.info("Starting keyword extraction using Ollama (subprocess mode)...")

    papers = load_jsonl(ALL_PAPERS_DIR)[:2]  # limit for testing
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    CACHE_DIR = Path(OUTPUT_DIR) / "cache"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for paper in tqdm(papers, desc="Extracting keywords"):
        title = paper.get("title", "").strip()
        if not title:
            continue

        # Create a safe filename for caching
        cache_file = CACHE_DIR / f"{title.replace('/', '_').replace(' ', '_')}.json"

        if cache_file.exists():
            # Load keywords from cache
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                keywords = cached_data.get("keywords", [])
            except Exception as e:
                logging.warning(f"Failed to read cache for '{title}': {e}")
                keywords = extract_keywords_with_ollama(title)
                cache_file.write_text(json.dumps({"keywords": keywords}), encoding="utf-8")
        else:
            # Extract keywords and cache them
            keywords = extract_keywords_with_ollama(title)
            cache_file.write_text(json.dumps({"keywords": keywords}), encoding="utf-8")

        if not keywords:
            continue

        results.append({
            "conference": paper.get("conference", ""),
            "title": title,
            "keywords": keywords,
        })

    output_path = Path(OUTPUT_DIR) / "ollama_keywords.json"
    write_json(output_path, results)
    logging.info(f"Saved extracted keywords to {output_path}")


if __name__ == "__main__":
    main()
