import os
import re
import json
import shutil

STATES_FILE = "gamefiles/states/00_states.txt"
INDEX_FILE = "data/state_index.json"
POPS_DIR = "gamefiles/pops"
BUILDINGS_DIR = "gamefiles/buildings"
OUTPUT_DIR = "output"

def parse_state_owners(states_file):
    with open(states_file, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r's:(STATE_[A-Z0-9_]+)\s*=\s*{[^}]*?country\s*=\s*c:([A-Z]{3})'
    matches = re.findall(pattern, content, re.DOTALL)
    state_owners = {state: owner for state, owner in matches}
    print(f"Found {len(state_owners)} state ownership entries.")
    return state_owners

def build_state_index():
    print("Building state index from pops and buildings files...")
    index = {}

    # Scan pops folder files
    for fname in os.listdir(POPS_DIR):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(POPS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        states_found = re.findall(r's:(STATE_[A-Z0-9_]+)\s*=', content)
        for st in states_found:
            index.setdefault(st, {})["pops"] = fname

    # Scan buildings folder files
    for fname in os.listdir(BUILDINGS_DIR):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(BUILDINGS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        states_found = re.findall(r's:(STATE_[A-Z0-9_]+)\s*=', content)
        for st in states_found:
            index.setdefault(st, {})["buildings"] = fname

    os.makedirs("data", exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    print(f"Indexed {len(index)} states.")
    return index

def swap_ownership_in_file(input_path, output_path, state_name, new_owner):
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf'(s:{re.escape(state_name)}\s*=\s*{{\s*?)region_state:([A-Z]+)(\s*=)'

    updated, count = re.subn(
        pattern,
        lambda m: f"{m.group(1)}region_state:{new_owner}{m.group(3)}",
        content,
        flags=re.DOTALL,
    )

    if count > 0:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"{state_name}: changed region_state to {new_owner} in {os.path.basename(output_path)}")

def run_ownership_swap():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load state owners from states file
    state_owners = parse_state_owners(STATES_FILE)

    # Load state index (or build it if missing)
    if not os.path.exists(INDEX_FILE):
        print("Index file missing, rebuilding...")
        state_index = build_state_index()
    else:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            state_index = json.load(f)

    modified_files = {}

    for state, owner in state_owners.items():
        index_entry = state_index.get(state)
        if not index_entry:
            print(f"{state} not found in state_index.json — skipping.")
            continue

        for category, folder in [("pops", POPS_DIR), ("buildings", BUILDINGS_DIR)]:
            if category in index_entry:
                filename = index_entry[category]
                source_path = os.path.join(folder, filename)
                output_folder = os.path.join(OUTPUT_DIR, category)
                os.makedirs(output_folder, exist_ok=True)
                output_path = os.path.join(output_folder, filename)

                # Copy original to output only once
                if filename not in modified_files:
                    shutil.copy2(source_path, output_path)
                    modified_files[filename] = True

                # Now modify the output file
                swap_ownership_in_file(output_path, output_path, state, owner)

    print("Ownership swap completed.")

if __name__ == "__main__":
    print("Step 1: Parsing states and building index...")
    build_state_index()
    print("Step 2: Running ownership swap...")
    run_ownership_swap()
