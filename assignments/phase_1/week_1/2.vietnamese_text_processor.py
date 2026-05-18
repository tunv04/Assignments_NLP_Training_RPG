import re
import string
from underthesea import sent_tokenize, word_tokenize
class VietnameseTextProcessor:
    def __init__(self, stopword_file=None, remove_stopwords_option=True):
        """
        Khởi tạo bộ xử lý văn bản tiếng Việt.

        Parameters:
            stopword_file: đường dẫn tới file stopwords .txt
            remove_stopwords_option: True nếu muốn xóa stopwords
        """
        self.remove_stopwords_option = remove_stopwords_option
        self.stopwords = set()

        if stopword_file is not None:
            self.load_stopwords(stopword_file)
    def load_stopwords(self, file_path):
        """
        Load stopwords từ file .txt.
        Mỗi dòng trong file là một stopword.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    word = line.strip().lower()
                    if word:
                        self.stopwords.add(word)
        except FileNotFoundError:
            print(f"Không tìm thấy file stopwords: {file_path}")

    def sentence_tokenize(self, text):
        """
        Tách văn bản thành các câu.
        """
        text = self.remove_html(text)
        text = self.normalize_whitespace(text)
        return sent_tokenize(text)

    def word_tokenize(self, text):
        """
        Tách từ tiếng Việt bằng underthesea.

        Ví dụ:
            "xử lý ngôn ngữ tự nhiên"
        Có thể thành:
            ["xử_lý", "ngôn_ngữ", "tự_nhiên"]
        """
        return word_tokenize(text, format="text").split()

    def lowercase(self, text):
        """
        Chuyển văn bản thành chữ thường.
        """
        return text.lower()

    def remove_urls(self, text):
        """
        Xóa URL khỏi văn bản.
        """
        url_pattern = r"http\S+|https\S+|www\S+"
        return re.sub(url_pattern, " ", text)

    def remove_html(self, text):
        """
        Xóa thẻ HTML khỏi văn bản.
        """
        html_pattern = r"<.*?>"
        return re.sub(html_pattern, " ", text)

    def remove_emojis(self, text):
        """
        Xóa emoji khỏi văn bản.
        """
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  
            "\U0001F300-\U0001F5FF"  
            "\U0001F680-\U0001F6FF"  
            "\U0001F1E0-\U0001F1FF"  
            "\U00002700-\U000027BF"  
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(" ", text)

    def remove_punctuation(self, text):
        """
        Xóa dấu câu.
        """
        vietnamese_punctuation = "“”‘’…–—«»"
        punctuation = string.punctuation + vietnamese_punctuation
        return text.translate(str.maketrans("", "", punctuation))

    def normalize_whitespace(self, text):
        """
        Chuẩn hóa khoảng trắng, tab và ký tự xuống dòng.
        """
        return re.sub(r"\s+", " ", text).strip()

    def remove_stopwords(self, tokens):
        """
        Xóa stopwords khỏi danh sách token.
        """
        if not self.remove_stopwords_option:
            return tokens

        return [
            token for token in tokens
            if token.lower() not in self.stopwords
        ]

    def preprocess(self, text):
        """
        Pipeline tiền xử lý hoàn chỉnh.

        Các bước:
        1. Xóa HTML
        2. Xóa URL
        3. Xóa emoji
        4. Chuyển thành chữ thường
        5. Xóa dấu câu
        6. Chuẩn hóa khoảng trắng
        7. Tách từ
        8. Xóa stopwords nếu được bật
        9. Trả về tokens và văn bản cuối cùng
        """
        text = self.remove_html(text)
        text = self.remove_urls(text)
        text = self.remove_emojis(text)
        text = self.lowercase(text)
        text = self.remove_punctuation(text)
        text = self.normalize_whitespace(text)
        tokens = self.word_tokenize(text)
        tokens = self.remove_stopwords(tokens)
        final_text = " ".join(tokens)
        return {
            "tokens": tokens,
            "processed_text": final_text
        }
if __name__ == "__main__":
    text = """<p>Hello!!!</p>
I am learning NLP 😄
Visit https://abc.com now!!!

Tôi đang học xử lý ngôn ngữ tự nhiên.
Việt Nam là một đất nước rất đẹp."""
    processor = VietnameseTextProcessor(
        stopword_file="D:\\TRAINING_NLP_RPG\\Phase1\\vietnamese_stopwords.txt",
        remove_stopwords_option=True
    )
    sentences = processor.sentence_tokenize(text)
    result = processor.preprocess(text)

    print("Sentences:")
    print(sentences)

    print("\nTokens:")
    print(result["tokens"])

    print("\nFinal Processed Text:")
    print(result["processed_text"])
