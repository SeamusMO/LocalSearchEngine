import re

# Common English stopwords
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "for", "nor", "so", "yet",
    "at", "by", "in", "of", "on", "to", "up", "with", "from", "into",
    "about", "above", "after", "against", "among", "around", "as", "before",
    "behind", "below", "beneath", "beside", "between", "beyond", "during",
    "except", "for", "from", "inside", "into", "near", "off", "on", "onto",
    "out", "outside", "over", "past", "through", "under", "underneath",
    "until", "up", "upon", "with", "within", "without", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "can",
    "could", "will", "would", "shall", "should", "may", "might", "must",
    "i", "me", "my", "myself", "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", "he", "him", "his",
    "himself", "she", "her", "hers", "herself", "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves", "what", "which", "who",
    "whom", "whose", "where", "when", "why", "how", "all", "any", "both",
    "each", "every", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t",
    "can", "will", "just", "don", "should", "now"
}

def tokenize_text(text, remove_stopwords=True):
    """
    Cleans and tokenizes text into a list of words.
    Converts to lowercase, removes non-alphanumeric characters, and optionally removes stopwords.
    """
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    if remove_stopwords:
        words = [word for word in words if word not in STOPWORDS]
    return words
