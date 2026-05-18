from collections import Counter
import re


class TermFrequencyAnalyzer:
    """
    Class dùng để phân tích Term Frequency (TF) trong một document.
    Term Frequency là tần suất xuất hiện của một từ trong một văn bản.
    Có 2 dạng chính:
    1. Raw Count:
       - Đếm số lần xuất hiện thật sự của từng từ.
       - Ví dụ: "NLP NLP is fun"
       - Raw count của "nlp" là 2.
    2. Normalized Term Frequency:
       - Lấy số lần xuất hiện của từ chia cho tổng số từ trong document.
       - Công thức:
            TF(t, d) = count(t, d) / total_terms(d)
       Trong đó:
       - t là term, tức là từ cần tính.
       - d là document, tức là văn bản đầu vào.
       - count(t, d) là số lần từ t xuất hiện trong document d.
       - total_terms(d) là tổng số từ trong document d.
    """
    def __init__(self, document):
        """
        Hàm khởi tạo đối tượng phân tích TF.

        Tham số:
        - document: văn bản đầu vào, kiểu string.
        """
        self.original_document = document
        self.cleaned_document = ""
        self.tokens = []
        self.raw_counts = {}
        self.normalized_tf = {}
    def validate_document(self):
        """
        Kiểm tra document đầu vào có hợp lệ không.

        Điều kiện hợp lệ:
        - Document phải là kiểu string.
        - Document không được rỗng sau khi loại bỏ khoảng trắng.
        """
        if not isinstance(self.original_document, str):
            raise TypeError("Document phải là kiểu dữ liệu string.")
        if self.original_document.strip() == "":
            raise ValueError("Document không được để trống.")
    def clean_text(self):
        """
        Làm sạch văn bản đầu vào.
        Các bước xử lý:
        1. Chuyển toàn bộ văn bản về chữ thường.
        2. Loại bỏ dấu câu không cần thiết.
        3. Giữ lại chữ cái, chữ số và khoảng trắng.
        Ví dụ:
        Input:
            "NLP, NLP is fun!"
        Output:
            "nlp nlp is fun"
        """
        text = self.original_document.lower()
        # Thay thế các ký tự không phải chữ, số hoặc khoảng trắng bằng khoảng trắng
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r"\s+", " ", text).strip()
        self.cleaned_document = text
    def tokenize(self):
        """
        Tách văn bản đã làm sạch thành danh sách các từ.

        Ví dụ:
        Input:
            "nlp nlp is fun"

        Output:
            ["nlp", "nlp", "is", "fun"]
        """
        if self.cleaned_document == "":
            self.tokens = []
        else:
            self.tokens = self.cleaned_document.split()
    def calculate_raw_count(self):
        """
        Tính raw count cho từng từ.
        Raw count là số lần xuất hiện thô của mỗi từ trong document.
        Ví dụ:
        tokens = ["nlp", "nlp", "is", "fun"]
        Kết quả:
        {
            "nlp": 2,
            "is": 1,
            "fun": 1
        }
        """
        self.raw_counts = dict(Counter(self.tokens))

    def calculate_normalized_tf(self):
        """
        Tính normalized Term Frequency cho từng từ.
        Công thức:
            TF(t, d) = count(t, d) / total_terms(d)
        Ví dụ:
        Document: "NLP NLP is fun"
        Tổng số từ = 4
        "nlp" xuất hiện 2 lần:
            TF("nlp") = 2 / 4 = 0.5
        "is" xuất hiện 1 lần:
            TF("is") = 1 / 4 = 0.25
        "fun" xuất hiện 1 lần:
            TF("fun") = 1 / 4 = 0.25
        """
        total_terms = len(self.tokens)
        if total_terms == 0:
            self.normalized_tf = {}
            return
        tf_result = {}
        for term, count in self.raw_counts.items():
            tf_result[term] = count / total_terms
        self.normalized_tf = tf_result
    def analyze(self):
        """
        Hàm chính để chạy toàn bộ quá trình phân tích.

        Các bước:
        1. Kiểm tra input.
        2. Làm sạch văn bản.
        3. Tách từ.
        4. Tính raw count.
        5. Tính normalized TF.
        """
        self.validate_document()
        self.clean_text()
        self.tokenize()
        self.calculate_raw_count()
        self.calculate_normalized_tf()
    def get_total_terms(self):
        """
        Trả về tổng số từ trong document.
        """
        return len(self.tokens)
    def display_input_information(self):
        """
        In thông tin cơ bản của document đầu vào.
        """
        print("=" * 60)
        print("INPUT INFORMATION")
        print("=" * 60)
        print("Original document:")
        print(self.original_document)
        print("\nCleaned document:")
        print(self.cleaned_document)
        print("\nTokens:")
        print(self.tokens)
        print("\nTotal terms:")
        print(self.get_total_terms())
    def display_raw_count(self):
        """
        In kết quả raw count.
        """
        print("\n" + "=" * 60)
        print("RAW COUNT")
        print("=" * 60)

        for term, count in self.raw_counts.items():
            print(f"{term}: {count}")

    def display_normalized_tf(self):
        """
        In kết quả normalized TF.
        """
        print("\n" + "=" * 60)
        print("NORMALIZED TERM FREQUENCY")
        print("=" * 60)

        for term, tf_score in self.normalized_tf.items():
            print(f"{term}: {tf_score}")

    def display_comparison_table(self):
        """
        In bảng so sánh giữa raw count và normalized TF.

        Bảng này giúp mentor dễ thấy sự khác nhau giữa:
        - Số lần xuất hiện thô
        - Tần suất đã chuẩn hóa
        """
        print("\n" + "=" * 60)
        print("COMPARISON: RAW COUNT VS NORMALIZED TF")
        print("=" * 60)

        print(f"{'Term':<15}{'Raw Count':<15}{'Normalized TF':<15}")
        print("-" * 45)

        for term in self.raw_counts:
            raw_count = self.raw_counts[term]
            tf_score = self.normalized_tf[term]

            print(f"{term:<15}{raw_count:<15}{tf_score:<15.4f}")

    def display_explanation(self):
        """
        In phần giải thích chi tiết về kết quả.
        """
        print("\n" + "=" * 60)
        print("EXPLANATION")
        print("=" * 60)

        total_terms = self.get_total_terms()

        print(f"Document sau khi xử lý có tổng cộng {total_terms} từ.")
        print("Normalized TF được tính bằng công thức:")
        print("TF(term, document) = số lần xuất hiện của term / tổng số từ")

        for term, count in self.raw_counts.items():
            tf_score = self.normalized_tf[term]
            print(
                f"\nTừ '{term}' xuất hiện {count} lần, "
                f"nên TF = {count} / {total_terms} = {tf_score}"
            )

    def display_all_results(self):
        """
        In toàn bộ kết quả phân tích.
        """
        self.display_input_information()
        self.display_raw_count()
        self.display_normalized_tf()
        self.display_comparison_table()
        self.display_explanation()


def compare_two_documents(document_1, document_2):
    """
    Hàm mở rộng dùng để so sánh TF giữa hai document khác nhau.
    Ý nghĩa:
    Normalized TF hữu ích hơn raw count khi so sánh các document
    có độ dài khác nhau.
    Ví dụ:
    Document 1: "NLP NLP is fun"
    Document 2: "NLP is fun and NLP is powerful"
    Raw count có thể cho biết số lần xuất hiện,
    nhưng normalized TF cho biết tỉ lệ xuất hiện của từ trong từng document.
    """
    analyzer_1 = TermFrequencyAnalyzer(document_1)
    analyzer_2 = TermFrequencyAnalyzer(document_2)
    analyzer_1.analyze()
    analyzer_2.analyze()
    print("\n" + "=" * 60)
    print("DOCUMENT COMPARISON")
    print("=" * 60)
    print("\nDocument 1:")
    print(document_1)
    print("TF result:")
    print(analyzer_1.normalized_tf)
    print("\nDocument 2:")
    print(document_2)
    print("TF result:")
    print(analyzer_2.normalized_tf)
def main():
    """
    Hàm main dùng để chạy chương trình.
    """

    document = "NLP NLP is fun"
    analyzer = TermFrequencyAnalyzer(document)
    analyzer.analyze()
    analyzer.display_all_results()
    second_document = "NLP is fun and NLP is powerful"
    compare_two_documents(document, second_document)
if __name__ == "__main__":
    main()