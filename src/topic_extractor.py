from transformers import (
    Text2TextGenerationPipeline,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    set_seed,
)
from .utils import load_jsonl, write_json, logging
from .config import (
    ALL_PAPERS_DIR,
    OUTPUT_DIR
)
from tqdm import tqdm  # Import tqdm for progress tracking
from bertopic import BERTopic

# Set seed for reproducibility
set_seed(42)

if __name__ == "__main__":
    papers = load_jsonl(ALL_PAPERS_DIR)

    titles = []
    for paper in tqdm(papers, desc="Loading paper titles"):  # Add tqdm here
        title = paper["title"]
        titles.append(title)

    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(titles)

    logging.info(topic_model.get_topic_info())

    # Create a dictionary to count the appearance of each topic
    # topic_appearance = {}
    # for keyphrase_list in tqdm(keyphrases, desc="Counting topic appearances"):  # Add tqdm here
    #     for topic in keyphrase_list:
    #         topic_appearance[topic] = topic_appearance.get(topic, 0) + 1

    # topic_appearance = dict(sorted(topic_appearance.items(), key=lambda item: item[1], reverse=True))
    # write_json(f"{OUTPUT_DIR}/topics.jsonl", topic_appearance)
