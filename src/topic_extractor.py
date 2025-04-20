from transformers import (
    Text2TextGenerationPipeline,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    set_seed,
)
from .utils import load_jsonl, write_json
from .config import (
    ALL_PAPERS_DIR,
    OUTPUT_DIR
)
from tqdm import tqdm  # Import tqdm for progress tracking

class KeyphraseGenerationPipeline(Text2TextGenerationPipeline):
    def __init__(self, model, keyphrase_sep_token=";", *args, **kwargs):
        super().__init__(
            model=AutoModelForSeq2SeqLM.from_pretrained(model, device_map="cuda:1"),
            tokenizer=AutoTokenizer.from_pretrained(model, device_map="cuda:1"),
            *args,
            **kwargs
        )
        self.keyphrase_sep_token = keyphrase_sep_token

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs
        )
        return [[keyphrase.strip() for keyphrase in result.get("generated_text").split(self.keyphrase_sep_token) if keyphrase != ""] for result in results]

# Set seed for reproducibility
set_seed(42)

# Load pipeline
model_name = "ml6team/keyphrase-generation-keybart-inspec"
generator = KeyphraseGenerationPipeline(model=model_name)

if __name__ == "__main__":
    papers = load_jsonl(ALL_PAPERS_DIR)

    titles = []
    for paper in tqdm(papers, desc="Loading paper titles"):  # Add tqdm here
        title = paper["title"]
        titles.append(title)

    keyphrases = generator(titles)  # Add tqdm here

    # Create a dictionary to count the appearance of each topic
    topic_appearance = {}
    for keyphrase_list in tqdm(keyphrases, desc="Counting topic appearances"):  # Add tqdm here
        for topic in keyphrase_list:
            topic_appearance[topic] = topic_appearance.get(topic, 0) + 1

    topic_appearance = dict(sorted(topic_appearance.items(), key=lambda item: item[1], reverse=True))
    write_json(f"{OUTPUT_DIR}/topics.jsonl", topic_appearance)
