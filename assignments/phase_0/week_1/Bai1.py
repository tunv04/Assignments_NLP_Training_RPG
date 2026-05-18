import re
def count_word_frequency(documents):
    """    Count the frequency of each word in a list of documents.
    Args:
        documents (list[str]): List of text documents.
    Returns:
        dict[str, int]: Word frequency dictionary.
    """
    word_frequency = {}
    for document in documents:
        words = re.findall(r"\b\w+\b", document.lower())
        for word in words:
            if word not in word_frequency:
                word_frequency[word] = 0
            word_frequency[word] += 1
    return word_frequency
documents = [
    "the quick brown fox",
    "the lazy dog sleeps",
    "the fox jumps over the dog"
]

print(count_word_frequency(documents))