import math
def compute_document_frequency(documents):
    """
    Tính document frequency df(t):
    df(t) = số lượng tài liệu có chứa từ t
    """
    df = {}
    for document in documents:
        # Chuyển về chữ thường và tách từ
        words = document.lower().split()

        # Dùng set để mỗi từ chỉ được tính 1 lần trong 1 document
        unique_words = set(words)

        for word in unique_words:
            df[word] = df.get(word, 0) + 1
    return df
def compute_idf(documents):
    """
    Tính IDF cho từng từ:
    IDF(t) = log(N / df(t))
    """
    N = len(documents)
    df = compute_document_frequency(documents)
    idf_scores = {}
    for word, freq in df.items():
        idf_scores[word] = math.log(N / freq)
    return idf_scores, df
def explain_idf(word, df_value, total_documents, idf_value):
    """
    Phần nâng cao:
    Giải thích ý nghĩa IDF của từng từ
    """
    print(f"\nTừ: '{word}'")
    print(f"Xuất hiện trong {df_value}/{total_documents} tài liệu")
    print(f"IDF = log({total_documents} / {df_value}) = {idf_value:.4f}")
    if df_value == total_documents:
        print("Giải thích: Đây là từ rất phổ biến, xuất hiện trong mọi tài liệu nên IDF thấp.")
    elif df_value == 1:
        print("Giải thích: Đây là từ hiếm, chỉ xuất hiện trong một tài liệu nên IDF cao.")
    else:
        print("Giải thích: Từ này xuất hiện ở một số tài liệu, nên IDF ở mức trung bình.")
def main():
    documents = [
        "python is easy",
        "python is powerful",
        "java is powerful",
        "python and java are programming languages"
    ]
    total_documents = len(documents)
    idf_scores, df_scores = compute_idf(documents)
    print("===== DOCUMENT FREQUENCY =====")
    for word, freq in df_scores.items():
        print(f"{word}: {freq}")
    print("\n===== IDF SCORES =====")
    for word, score in idf_scores.items():
        print(f"{word}: {score:.4f}")
    print("\n===== GIẢI THÍCH NÂNG CAO =====")
    print("""
IDF dùng để đo mức độ quan trọng của một từ trong tập tài liệu.

- Từ phổ biến xuất hiện trong nhiều tài liệu.
  Khi df(t) lớn, N / df(t) nhỏ, nên log(N / df(t)) nhỏ.
  Vì vậy từ phổ biến có IDF thấp.

- Từ hiếm xuất hiện trong ít tài liệu.
  Khi df(t) nhỏ, N / df(t) lớn, nên log(N / df(t)) lớn.
  Vì vậy từ hiếm có IDF cao.
""")
    for word in idf_scores:
        explain_idf(
            word,
            df_scores[word],
            total_documents,
            idf_scores[word]
        )
if __name__ == "__main__":
    main()