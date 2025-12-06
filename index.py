import os
import json
from utils import tokenize_text

INDEX_FILE = "inverted_index.json"
NOTES_DIR = "notes"

def build_inverted_index(notes_directory):
    """
    Recursively scans the notes directory, tokenizes text, and builds an inverted index.
    The index maps each word to a dictionary of file paths, where each file path
    points to a list of positions where the word appears in that file.
    """
    inverted_index = {}
    processed_files_count = 0

    for root, _, files in os.walk(notes_directory):
        for filename in files:
            if filename.endswith((".txt", ".md")):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                        # Tokenize text, removing stopwords for indexing
                        words = tokenize_text(text, remove_stopwords=True)

                        for i, word in enumerate(words):
                            if word not in inverted_index:
                                inverted_index[word] = {}
                            if filepath not in inverted_index[word]:
                                inverted_index[word][filepath] = []
                            inverted_index[word][filepath].append(i)
                        processed_files_count += 1
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
    
    if processed_files_count == 0:
        print(f"Your notes folder '{notes_directory}' is empty or contains no readable .txt/.md files.")
        return {}, None # Return empty index and no file_contents

    return inverted_index, None # No longer returning file_contents

def save_index(inverted_index, index_file_path):
    """
    Saves the inverted index to a JSON file.
    File contents are no longer saved to the index.
    """
    try:
        with open(index_file_path, 'w', encoding='utf-8') as f:
            json.dump(inverted_index, f, indent=2)
        print(f"Index successfully saved to {index_file_path}")
    except Exception as e:
        print(f"Error saving index to {index_file_path}: {e}")

if __name__ == "__main__":
    print(f"Scanning notes in '{NOTES_DIR}' and building index...")
    inverted_index, _ = build_inverted_index(NOTES_DIR) # _ to ignore file_contents
    if inverted_index: # Only save if index is not empty
        save_index(inverted_index, INDEX_FILE)
