import math
# Hàm tách từ trong document
def tokenize(document):
    return document.lower().split()
# Tạo vocabulary mapping
def build_vocabulary(documents):
    vocabulary = {}
    for doc in documents:
        words = tokenize(doc)
        for word in words:
            if word not in vocabulary:
                vocabulary[word] = len(vocabulary)
    return vocabulary
# Tính TF cho một document
def compute_tf(document, vocabulary):
    words = tokenize(document)
    total_words = len(words)
    tf = [0] * len(vocabulary)
    for word in words:
        index = vocabulary[word]
        tf[index] += 1
    # Chia cho tổng số từ để ra TF
    for i in range(len(tf)):
        tf[i] = tf[i] / total_words
    return tf
# Tính IDF cho toàn bộ vocabulary
def compute_idf(documents, vocabulary):
    N = len(documents)
    idf = [0] * len(vocabulary)
    for word, index in vocabulary.items():
        df = 0
        # Đếm xem word xuất hiện trong bao nhiêu document
        for doc in documents:
            words = set(tokenize(doc))
            if word in words:
                df += 1
        # Smoothing:
        # IDF(t) = log((N + 1) / (df + 1)) + 1
        idf[index] = math.log((N + 1) / (df + 1)) + 1
    return idf
# Chuẩn hóa vector bằng L2 normalization
def normalize(vector):
    total = 0
    for value in vector:
        total += value ** 2
    length = math.sqrt(total)
    if length == 0:
        return vector
    for i in range(len(vector)):
        vector[i] = vector[i] / length
    return vector
# Tính ma trận TF-IDF
def compute_tfidf(documents):
    vocabulary = build_vocabulary(documents)
    idf = compute_idf(documents, vocabulary)
    tfidf_matrix = []
    for doc in documents:
        tf = compute_tf(doc, vocabulary)
        tfidf = [0] * len(vocabulary)
        for i in range(len(vocabulary)):
            tfidf[i] = tf[i] * idf[i]
        # Bonus: normalization
        tfidf = normalize(tfidf)
        tfidf_matrix.append(tfidf)
    return tfidf_matrix, vocabulary, idf
# Chương trình chính
documents = [
    "I love NLP",
    "NLP is fun",
    "I love machine learning"
]
tfidf_matrix, vocabulary, idf = compute_tfidf(documents)
print("Vocabulary mapping:")
print(vocabulary)
print("\nIDF:")
print([round(x, 4) for x in idf])
print("\nTF-IDF matrix:")
for i in range(len(tfidf_matrix)):
    row = [round(x, 4) for x in tfidf_matrix[i]]
    print("Document", i + 1, ":", row)