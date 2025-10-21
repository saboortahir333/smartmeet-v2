import json

input_file = "sentences_for_labelstudio.jsonl"
output_file = "sentences_for_labelstudio.txt"

with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
    for line in f:
        obj = json.loads(line)
        text = obj["data"]["text"]
        out.write(text + "\n")

print(f"✅ Saved plain text version: {output_file}")
