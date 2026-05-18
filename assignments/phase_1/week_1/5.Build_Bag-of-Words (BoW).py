documents = [
    "NLP is fun",
    "I love NLP",
    "NLP NLP NLP",
    "I love learning NLP",
    "Python is fun",
    "I love Python",
    "NLP is useful",
    "Python and NLP are important"
]
# Bước 1: Tách từ
tokenized_docs = []
for doc in documents:
    words = doc.lower().split()
    tokenized_docs.append(words)
print("Tokenized documents:")
print(tokenized_docs)
# Bước 2: Xây dựng vocabulary
vocab = []
for doc in tokenized_docs:
    for word in doc:
        if word not in vocab:
            vocab.append(word)
print("\nVocabulary:")
print(vocab)
# Bước 3: Tạo Count BoW
count_bow = []
for doc in tokenized_docs:
    vector = []
    for word in vocab:
        count = doc.count(word)
        vector.append(count)
    count_bow.append(vector)
print("\nCount BoW:")
print(count_bow)
# Bước 4: Tạo Binary BoW
binary_bow = []
for doc in tokenized_docs:
    vector = []
    for word in vocab:
        if word in doc:
            vector.append(1)
        else:
            vector.append(0)
    binary_bow.append(vector)
print("\nBinary BoW:")
print(binary_bow)
# Bước 5: In kết quả dễ nhìn hơn
print("\nDocument-Term Matrix Count BoW:")
for i in range(len(documents)):
    print("Document", i + 1, ":", documents[i])
    print(count_bow[i])
print("\nDocument-Term Matrix Binary BoW:")
for i in range(len(documents)):
    print("Document", i + 1, ":", documents[i])
    print(binary_bow[i])