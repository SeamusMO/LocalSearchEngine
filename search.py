import json
import sys
import re
import os
from utils import tokenize_text, STOPWORDS

INDEX_FILE = "inverted_index.json"
NOTES_DIR = "notes"

def load_index(index_file_path):
    """
    Loads the inverted index from a JSON file.
    """
    if not os.path.exists(index_file_path):
        print(f"Error: Index file '{index_file_path}' not found.")
        print("Please run 'python3 index.py' first to build the index.")
        sys.exit(1)
    try:
        with open(index_file_path, 'r', encoding='utf-8') as f:
            inverted_index = json.load(f)
            return inverted_index
    except Exception as e:
        print(f"Error loading index from '{index_file_path}': {e}")
        sys.exit(1)

def _parse_query(query_string):
    """
    Parses the query string into a structured format, handling phrases and OR operators.
    Returns a list of 'OR' groups, where each group is a list of 'AND' terms.
    Each term is a dictionary: {"type": "word"|"phrase", "value": tokenized_list_of_words}.
    """
    or_groups = []
    # Split by ' OR ' (case-insensitive)
    and_query_parts = re.split(r'\s+OR\s+', query_string, flags=re.IGNORECASE)

    for and_part in and_query_parts:
        current_and_group = []
        # Find all quoted phrases
        phrases = re.findall(r'"([^"]*)"', and_part)
        
        # Replace quoted phrases with a placeholder to process individual words
        temp_and_part = and_part
        for i, phrase in enumerate(phrases):
            temp_and_part = temp_and_part.replace(f'"{phrase}"', f"__PHRASE_{i}__")

        # Process individual words (not inside quotes and not 'OR')
        words = re.findall(r'\b\w+\b', temp_and_part)
        
        # Add individual words to the current AND group
        for word in words:
            # Ensure we don't re-add parts of phrases or the OR keyword itself
            if not re.match(r'__PHRASE_\d+__', word) and word.lower() != 'or':
                tokenized_word = tokenize_text(word, remove_stopwords=True)
                if tokenized_word:
                    current_and_group.append({"type": "word", "value": tokenized_word[0]})

        # Add phrases back to the current AND group
        for i, phrase in enumerate(phrases):
            tokenized_phrase = tokenize_text(phrase, remove_stopwords=True)
            if tokenized_phrase:
                current_and_group.append({"type": "phrase", "value": tokenized_phrase})
        
        if current_and_group:
            or_groups.append(current_and_group)
            
    return or_groups

def _check_phrase_in_file(filepath, phrase_tokens, inverted_index):
    """
    Checks if an exact phrase exists in a given file using the inverted index's position data.
    Returns True if the phrase is found, False otherwise.
    """
    if not phrase_tokens:
        return False
    
    first_word = phrase_tokens[0]
    if first_word not in inverted_index or filepath not in inverted_index[first_word]:
        return False

    # Get positions of the first word in the file
    first_word_positions = inverted_index[first_word][filepath]

    for start_pos in first_word_positions:
        match = True
        for i, word_token in enumerate(phrase_tokens):
            if i == 0: # Already checked the first word
                continue
            
            expected_pos = start_pos + i
            if word_token not in inverted_index or filepath not in inverted_index[word_token]:
                match = False
                break
            
            # Check if the next word is at the expected consecutive position
            if expected_pos not in inverted_index[word_token][filepath]:
                match = False
                break
        if match:
            return True
    return False

def search_index(query, inverted_index):
    """
    Searches the inverted index for the given query, supporting phrase search and OR queries.
    Returns a dictionary of matching file paths with their relevance score.
    """
    parsed_query_groups = _parse_query(query)
    if not parsed_query_groups:
        return {}

    overall_matching_files = {} # Stores {filepath: score}

    all_query_words_for_scoring = set() # Collect all unique query words (from phrases and single words) for scoring

    for and_group in parsed_query_groups:
        current_group_candidate_files = None # Set of filepaths for the current AND group

        # Collect all words from this AND group for scoring later
        for term in and_group:
            if term["type"] == "word":
                all_query_words_for_scoring.add(term["value"])
            elif term["type"] == "phrase":
                for word in term["value"]:
                    all_query_words_for_scoring.add(word)

        for term in and_group:
            term_matching_files = set()
            if term["type"] == "word":
                word = term["value"]
                if word in inverted_index:
                    term_matching_files.update(inverted_index[word].keys())
                else: # If a required word is not in the index, this AND group has no matches
                    current_group_candidate_files = set()
                    break
            elif term["type"] == "phrase":
                phrase_tokens = term["value"]
                # Find files that contain the first word of the phrase as candidates
                if phrase_tokens[0] in inverted_index:
                    candidate_files_for_phrase = inverted_index[phrase_tokens[0]].keys()
                    for filepath in candidate_files_for_phrase:
                        if _check_phrase_in_file(filepath, phrase_tokens, inverted_index):
                            term_matching_files.add(filepath)
                else: # If the first word of the phrase is not in the index, this AND group has no matches
                    current_group_candidate_files = set()
                    break
            
            if current_group_candidate_files is None:
                current_group_candidate_files = term_matching_files
            else:
                current_group_candidate_files.intersection_update(term_matching_files)
            
            if not current_group_candidate_files: # If intersection results in empty set, no need to check further terms in this AND group
                break
        
        # Add files from this AND group to the overall results (union for OR logic)
        if current_group_candidate_files:
            for filepath in current_group_candidate_files:
                overall_matching_files[filepath] = 0 # Initialize score, will be calculated later

    # Calculate relevance score for all overall matching files
    ranked_results = {}
    for filepath in overall_matching_files:
        score = 0
        for word in all_query_words_for_scoring:
            if word in inverted_index and filepath in inverted_index[word]:
                score += len(inverted_index[word][filepath]) # Term frequency
        if score > 0:
            ranked_results[filepath] = score

    # Sort results by score in descending order
    sorted_results = sorted(ranked_results.items(), key=lambda item: item[1], reverse=True)
    return sorted_results

def get_snippet(filepath, query_words, snippet_length=150, highlight_color='\033[1;33m', reset_color='\033[0m'):
    """
    Extracts a relevant snippet from the file content (reloaded from disk) and highlights query words.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        return "Error: File not found for snippet generation."
    except Exception as e:
        return f"Error reading file for snippet: {e}"

    if not text.strip():
        return "File content is empty."

    # Find the first occurrence of any query word to center the snippet
    first_match_index = -1
    # Use original query words (not tokenized) for snippet highlighting to match user input more closely
    # but ensure they are lowercased for consistent matching.
    query_terms_for_snippet = [q_word.lower() for q_word in re.findall(r'\b\w+\b', query_words)]
    
    for q_word in query_terms_for_snippet:
        match = re.search(r'\b' + re.escape(q_word) + r'\b', text, re.IGNORECASE)
        if match:
            first_match_index = match.start()
            break

    if first_match_index == -1:
        start_index = 0
    else:
        start_index = max(0, first_match_index - snippet_length // 2)

    end_index = min(len(text), start_index + snippet_length)
    snippet = text[start_index:end_index]

    # Highlight query words in the snippet
    for q_word in query_terms_for_snippet:
        snippet = re.sub(r'\b(' + re.escape(q_word) + r')\b', f"{highlight_color}\\1{reset_color}", snippet, flags=re.IGNORECASE)

    return snippet.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search.py <query>")
        sys.exit(1)

    raw_query = " ".join(sys.argv[1:])
    
    if len(raw_query.strip()) < 3:
        print("Query too short. Please provide a query with at least 3 characters.")
        sys.exit(1)

    print(f"Searching for: '{raw_query}'")

    inverted_index = load_index(INDEX_FILE)
    
    # Pass the raw query to get_snippet for better highlighting based on user input
    # but use tokenized words for the actual search logic.
    results = search_index(raw_query, inverted_index)

    if not results:
        print("No matching notes found.")
    else:
        print(f"\nFound {len(results)} matching notes:")
        for filepath, score in results:
            display_filepath = os.path.basename(filepath)
            print(f"\n--- {display_filepath} (Score: {score}) ---")
            
            # Pass the original raw query to get_snippet for highlighting
            snippet = get_snippet(filepath, raw_query)
            
            if not snippet.strip():
                print("No relevant snippet available.")
            else:
                print(snippet)
            print("------------------------------------")
