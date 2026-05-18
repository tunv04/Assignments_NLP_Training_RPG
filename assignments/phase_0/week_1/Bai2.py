def chunk_tokens(tokens, chunk_size, overlap=0):
    """   
    Em dùng thuật toán Sliding Window. 
    Mỗi chunk được lấy bằng cách cắt danh sách tokens từ vị trí start đến start + chunk_size. 
    Sau mỗi lần tạo chunk, vị trí bắt đầu được dịch đi chunk_size - overlap, nhờ đó có thể tạo overlap giữa các chunk liên tiếp. 
    Hàm cũng kiểm tra input để tránh các trường hợp lỗi như chunk_size <= 0 hoặc overlap >= chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks = []
    step = chunk_size - overlap
    start = 0
    while start + chunk_size <= len(tokens):
        chunk = tokens[start:start + chunk_size]
        chunks.append(chunk)
        start += step
    return chunks
def main():
    # Example 1
    tokens_1 = ["a", "b", "c", "d", "e", "f"]
    chunk_size_1 = 3
    overlap_1 = 0
    result_1 = chunk_tokens(tokens_1, chunk_size_1, overlap_1)
    print("Example 1:")
    print(result_1)
    # Example 2
    tokens_2 = ["a", "b", "c", "d", "e", "f", "g"]
    chunk_size_2 = 3
    overlap_2 = 1
    result_2 = chunk_tokens(tokens_2, chunk_size_2, overlap_2)
    print("\nExample 2:")
    print(result_2)
if __name__ == "__main__":
    main()