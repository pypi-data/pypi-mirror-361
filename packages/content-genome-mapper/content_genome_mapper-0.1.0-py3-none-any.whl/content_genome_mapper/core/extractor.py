import os
import json
import spacy
from urllib.parse import urlparse
from typing import Tuple, List

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def extract(url: str, save_dir: str = "data") -> Tuple[str, dict]:
    """
    Load the crawled JSON content for a URL and return the text + metadata.
    """
    parsed = urlparse(url)
    filename = parsed.netloc.replace(".", "_") + ".json"
    filepath = os.path.join(save_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Crawled data not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("text", ""), data  # (text, full_metadata)

def get_entities(text: str) -> List[Tuple[str, str]]:
    """
    Extract named entities from text using spaCy.
    Returns list of (entity_text, entity_label) tuples.
    """
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]
