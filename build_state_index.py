import os
import re
import json

DATA_DIR = "data"
OUTPUT_INDEX = os.path.join(DATA_DIR, "state_index.json")

def extract_state_keys_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    states = set()
    for line in lines:
        match = re.search(r's:(STATE_[A-Z0-9_]+)\s*=', line)
        if match:
            states.add(match.group(1))
    return list(states)

def build_state_index():
    index = {}

    for category in ["pops", "buildings"]:
        folder = os.path.join(DATA_DIR, category)
        for filename in os.listdir(folder):
            if not filename.endswith(".txt"):
                continue
            path = os.path.join(folder, filename)
            state_names = extract_state_keys_from_file(path)
            for state in state_names:
                if state not in index:
                    index[state] = {}
                index[state][category] = filename

    with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"Indexed {len(index)} states and saved to {OUTPUT_INDEX}")

if __name__ == "__main__":
    build_state_index()
