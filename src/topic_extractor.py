from transformers import (
    Text2TextGenerationPipeline,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    set_seed,
)
from .utils import load_jsonl, write_jsonl
from .config import (
    ALL_PAPERS_DIR,
    OUTPUT_DIR
)

class KeyphraseGenerationPipeline(Text2TextGenerationPipeline):
    def __init__(self, model, keyphrase_sep_token=";", *args, **kwargs):
        super().__init__(
            model=AutoModelForSeq2SeqLM.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
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

def extract_topics(texts):
    """
    Extract topics from a set of input strings using the KeyBART model.

    Args:
        texts (set): A set of strings to extract topics from.

    Returns:
        list: A list of extracted topics.
    """
    topics = []
    for text in texts:
        # Generate keyphrases using the pipeline
        outputs = generator(text)
        topics.extend(outputs[0])  # Flatten the list of keyphrases
    
    return topics

if __name__ == "__main__":
    papers = load_jsonl(ALL_PAPERS_DIR)

    titles = []
    for paper in papers:
        title = paper["title"]
        titles.append(title)

    keyphrases = generator(titles)

    # Create a dictionary to count the appearance of each topic
    topic_appearance = {}
    for keyphrase_list in keyphrases:
        for topic in keyphrase_list:
            topic_appearance[topic] = topic_appearance.get(topic, 0) + 1

    topic_appearance = dict(sorted(topic_appearance.items(), key=lambda item: item[1], reverse=True))
    write_jsonl(f"{OUTPUT_DIR}/topics.jsonl", topic_appearance)
