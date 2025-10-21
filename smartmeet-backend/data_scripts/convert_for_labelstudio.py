import json
from pathlib import Path

input_path = Path("sentences_for_labeling.jsonl")
output_path = Path("sentences_for_labelstudio.jsonl")

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        obj = json.loads(line)
        sentence = obj.get("text")
        new_obj = {"data": {"text": sentence}}
        outfile.write(json.dumps(new_obj) + "\n")

print(f"✅ Saved {output_path}")
