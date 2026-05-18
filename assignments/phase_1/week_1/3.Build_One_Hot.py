# Input
sentences = [
    "I love NLP",
    "NLP is fun",
    "I enjoy learning machine learning",
    "Natural language processing is interesting",
    "Python is useful for NLP",
    "I love learning Python",
    "Machine learning is fun",
    "Deep learning is powerful",
    "Text data is important",
    "NLP helps computers understand language"
]
# Token đặc biệt
PAD_TOKEN = "<PAD>"   
UNK_TOKEN = "<UNK>"   
# Bước 1: Tiền xử lý dữ liệu

def tokenize(sentence):
    """
    Chuyển câu về chữ thường và tách thành các từ.
    """
    return sentence.lower().split()
tokenized_sentences = []
for sentence in sentences:
    tokens = tokenize(sentence)
    tokenized_sentences.append(tokens)
print("Tokenized sentences:")
print(tokenized_sentences)

# Bước 2: Xây dựng vocabulary

def build_vocabulary(tokenized_sentences):
    """
    Xây dựng vocabulary từ danh sách các câu đã tokenize.
    Có thêm <PAD> và <UNK>.
    """
    vocab = {
        PAD_TOKEN: 0,
        UNK_TOKEN: 1
    }
    for sentence in tokenized_sentences:
        for word in sentence:
            if word not in vocab:
                vocab[word] = len(vocab)
    return vocab
vocab = build_vocabulary(tokenized_sentences)
print("\nVocabulary:")
print(vocab)

# Bước 3: Tạo one-hot vector

def one_hot_encode(word, vocab):
    """
    Chuyển một từ thành one-hot vector.
    Nếu từ không có trong vocab, dùng <UNK>.
    """
    vector = [0] * len(vocab)
    if word in vocab:
        index = vocab[word]
    else:
        index = vocab[UNK_TOKEN]
    vector[index] = 1
    return vector

# Bước 4: Padding câu

def pad_sentence(tokens, max_length):
    """
    Padding câu để các câu có cùng độ dài.
    Nếu câu ngắn hơn max_length thì thêm <PAD>.
    """
    padded_tokens = tokens.copy()

    while len(padded_tokens) < max_length:
        padded_tokens.append(PAD_TOKEN)

    return padded_tokens
# Tìm độ dài câu dài nhất
max_length = max(len(sentence) for sentence in tokenized_sentences)
print("\nMax sentence length:")
print(max_length)
# Padding tất cả câu
padded_sentences = []

for sentence in tokenized_sentences:
    padded_sentence = pad_sentence(sentence, max_length)
    padded_sentences.append(padded_sentence)

print("\nPadded sentences:")
print(padded_sentences)

# Bước 5: Encode toàn bộ câu

def encode_sentence(tokens, vocab):
    """
    Chuyển một câu thành danh sách các one-hot vector.
    """
    encoded_sentence = []

    for word in tokens:
        vector = one_hot_encode(word, vocab)
        encoded_sentence.append(vector)

    return encoded_sentence


encoded_sentences = []

for sentence in padded_sentences:
    encoded_sentence = encode_sentence(sentence, vocab)
    encoded_sentences.append(encoded_sentence)
# Bước 6: In kết quả
print("\nOne-hot vectors for each sentence:")

for i, sentence in enumerate(padded_sentences):
    print(f"\nSentence {i + 1}: {sentence}")

    for word in sentence:
        vector = one_hot_encode(word, vocab)
        print(f"{word} -> {vector}")

# Bước 7: Kiểm tra từ không tồn tại
test_words = ["love", "nlp", "python", PAD_TOKEN]
print("\nTest unknown and padding tokens:")
for word in test_words:
    vector = one_hot_encode(word, vocab)
    print(f"{word} -> {vector}")