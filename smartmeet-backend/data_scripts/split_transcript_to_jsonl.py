import spacy
import json
from pathlib import Path

# Load spaCy's small English model for sentence splitting
nlp = spacy.load("en_core_web_sm")

# Input transcript file (change path if needed)
input_file = Path("meeting_ab1a5ff5_transcript.txt")
output_file = Path("sentences_for_labeling.jsonl")

# Read file content
text = input_file.read_text(encoding="utf-8").strip()

# Use spaCy to split into sentences
doc = nlp(text)
sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

# Write each sentence to JSONL
with open(output_file, "w", encoding="utf-8") as f:
    for sent in sentences:
        json_line = {"text": sent, "entities": []}
        f.write(json.dumps(json_line) + "\n")

print(f"✅ Saved {len(sentences)} sentences to {output_file}")
