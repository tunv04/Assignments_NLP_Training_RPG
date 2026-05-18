sentences = [
    "I love NLP",
    "NLP is fun"
]
# độ dài tối đa của câu
max_len = 5

# token dùng để padding và unknown
PAD = "<PAD>"
UNK = "<UNK>"
# Bước 1: tách từ
all_words = []
for sentence in sentences:
    words = sentence.lower().split()

    for word in words:
        if word not in all_words:
            all_words.append(word)
# thêm PAD và UNK vào đầu vocabulary
vocab = [PAD, UNK] + all_words
print("Vocabulary:")
print(vocab)
# Bước 2: tạo dictionary word -> index
word_to_index = {}
for i in range(len(vocab)):
    word_to_index[vocab[i]] = i
print("\nWord to index:")
print(word_to_index)
# Bước 3: hàm tạo one-hot vector
def one_hot(word):
    vector = [0] * len(vocab)
    if word in word_to_index:
        index = word_to_index[word]
    else:
        index = word_to_index[UNK]
    vector[index] = 1
    return vector
# Bước 4: hàm xử lý một câu
def encode_sentence(sentence):
    words = sentence.lower().split()
    # truncation: nếu câu dài hơn max_len thì cắt bớt
    if len(words) > max_len:
        words = words[:max_len]
    # padding: nếu câu ngắn hơn max_len thì thêm <PAD>
    while len(words) < max_len:
        words.append(PAD)
    result = []
    for word in words:
        vector = one_hot(word)
        result.append(vector)
    return result
# Bước 5: chạy thử
sentence = "I love NLP"
encoded = encode_sentence(sentence)
print("\nSentence:")
print(sentence)
print("\nEncoded sentence:")
print(encoded)
# Chạy thử câu có từ chưa xuất hiện trong vocabulary
sentence2 = "I love Python very much"
encoded2 = encode_sentence(sentence2)
print("\nSentence 2:")
print(sentence2)
print("\nEncoded sentence 2:")
print(encoded2)