import re
from collections import Counter
class WhitespaceTokenizer:
    """
    Bộ tokenizer đơn giản:
    - Chuyển text thành chữ thường
    - Chuẩn hóa khoảng trắng, tab, xuống dòng
    - Tách token bằng whitespace
    """
    def lowercase(self, text):
        if not isinstance(text, str):
            raise TypeError("Input phải là chuỗi.")
        return text.lower()

    def normalize_whitespace(self, text):
        if not isinstance(text, str):
            raise TypeError("Input phải là chuỗi.")
        # \s+ xử lý nhiều khoảng trắng, tab, newline thành 1 khoảng trắng
        return re.sub(r"\s+", " ", text).strip()

    def remove_punctuation(self, text):
        if not isinstance(text, str):
            raise TypeError("Input phải là chuỗi.")
        # Chỉ giữ lại chữ, số và khoảng trắng
        return re.sub(r"[^\w\s]", "", text)
    def tokenize(self, text, remove_punctuation=False):
        """
        Tokenize một đoạn văn bản.
        Parameters:
            text: chuỗi đầu vào
            remove_punctuation: True nếu muốn bỏ dấu câu
        Returns:
            Danh sách token
        """
        text = self.lowercase(text)
        text = self.normalize_whitespace(text)
        if remove_punctuation:
            text = self.remove_punctuation(text)
        return text.split()
    def count_frequency(self, text, remove_punctuation=False):
        """
        Đếm số lần xuất hiện của từng token.
        """
        tokens = self.tokenize(text, remove_punctuation)
        return dict(Counter(tokens))
    def batch_tokenize(self, texts, remove_punctuation=False):
        """
        Tokenize nhiều câu cùng lúc.
        """
        if not isinstance(texts, list):
            raise TypeError("Input phải là danh sách các chuỗi.")
        return [
            self.tokenize(text, remove_punctuation)
            for text in texts
        ]
if __name__ == "__main__":
    tokenizer = WhitespaceTokenizer()
    text = """Hello world!   
NLP is fun."""

    print("Input:")
    print(text)
    print("\n1. Tokenize cơ bản:")
    print(tokenizer.tokenize(text))
    print("\n2. Tokenize và bỏ dấu câu:")
    print(tokenizer.tokenize(text, remove_punctuation=True))
    print("\n3. Đếm tần suất token:")
    sentence = "NLP is fun. NLP is useful."
    print(tokenizer.count_frequency(sentence, remove_punctuation=True))
    print("\n4. Batch tokenization:")
    texts = [
        "I love NLP",
        "Tokenization is easy",
        "Python   is\nvery useful"
    ]
    print(tokenizer.batch_tokenize(texts))