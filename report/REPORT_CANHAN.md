# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự cao nghĩa là hai vector có hướng gần nhau trong không gian vector, tức là chúng biểu diễn các ý nghĩa hoặc đặc trưng tương tự. 

**Ví dụ có độ tương tự CAO:**
- Câu A: Tôi muốn học Machine Learning.
- Câu B: Tôi muốn tìm hiểu về học máy.
- Tại sao tương đồng: Hai câu diễn đạt gần như cùng một ý nghĩa dù dùng từ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tôi muốn học Machine Learning.
- Câu B: Hôm nay trời mưa rất lớn.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau nên vector biểu diễn có hướng ít tương đồng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity tập trung vào hướng của vector, tức là mức độ giống nhau về ngữ nghĩa, và ít bị ảnh hưởng bởi độ lớn của vector. Vì vậy nó thường phù hợp hơn để so sánh text embeddings so với Euclidean distance.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
Bước nhảy giữa hai chunk = 500 - 50 = 450 ký tự.
Số chunk = ceil((10000 - 500) / 450) + 1 = 23.
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Khi overlap = 100, bước nhảy còn 400 ký tự nên số chunk tăng lên 33 chunks. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới giữa các chunk, giảm nguy cơ một ý hoặc câu quan trọng bị cắt tách.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* 
Tôi dùng regex để tách văn bản theo điểm kết thúc câu, ví dụ là các mẫu như . , ! , ?  và .\\n, rồi gom theo số câu tối đa trong mỗi chunk. Sau khi tách, tôi strip khoảng trắng thừa để tránh các chunk rỗng hoặc có khoảng trắng dư. Với trường hợp text rỗng, hàm trả về [] thay vì crash, và nếu văn bản quá dài thì chia thành nhiều nhóm câu liên tiếp.


**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
Tôi ưu tiên tách theo các separator có ý nghĩa hơn trước, theo thứ tự ["\\n\\n", "\\n", ". ", " ", ""], để giữ ngữ cảnh ở mức đoạn, đoạn văn, câu và từ. Nếu một đoạn vẫn dài hơn chunk_size, hàm sẽ gọi đệ quy với separator tiếp theo, và nếu cần thiết sẽ gom các mảnh nhỏ liền kề lại để không tạo ra các chunk quá ngắn, vụn. Base case là khi text rỗng, đã nhỏ hơn hoặc bằng chunk_size, hoặc không còn separator nào để chia thì trả về chunk cuối cùng hoặc fallback theo kích thước cố định.


### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
Tôi lưu mỗi tài liệu dưới dạng Document với id, content và metadata, sau đó chuyển nội dung thành embedding bằng hàm embedding đã cho. Khi tìm kiếm, hệ thống chuyển query thành vector tương tự và tính cosine similarity với tất cả embedding trong kho, rồi sắp xếp giảm dần theo điểm số để lấy top-k kết quả phù hợp.


**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
Tôi áp dụng lọc metadata trước khi tính khoảng cách hoặc sau khi có kết quả để giảm không gian tìm kiếm và giữ các tài liệu đúng điều kiện. Với xóa tài liệu, tôi dùng id hoặc khóa xác định để loại bỏ bản ghi khỏi bộ nhớ và cập nhật lại số lượng tài liệu trong collection.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
Tôi xây dựng prompt theo kiểu: “Dựa trên ngữ cảnh dưới đây, trả lời câu hỏi...”, rồi chèn các đoạn dữ liệu có độ tương tự cao nhất từ EmbeddingStore vào phần context. Cách làm này giúp agent trả lời theo ngữ cảnh thực tế hơn, giảm nguy cơ hallucination và tập trung vào thông tin liên quan trực tiếp tới câu hỏi.
---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
(.venv) PS C:\Users\thaih\Projects\Vin\K4-DAY07-HoThaiHoa-2A202602915> pytest tests/ -v
============================================== test session starts ==============================================
platform win32 -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\thaih\Projects\Vin\K4-DAY07-HoThaiHoa-2A202602915\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\thaih\Projects\Vin\K4-DAY07-HoThaiHoa-2A202602915
collected 42 items                                                                                               

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                      [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                               [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                        [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                         [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                              [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED              [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                    [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                     [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                   [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                     [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                     [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                            [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                      [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED             [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                 [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED           [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                 [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                     [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                       [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                         [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                               [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                    [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                      [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED          [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                       [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                               [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                          [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                      [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                 [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                     [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                           [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                     [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED  [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED               [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED   [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED              [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED       [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================================== 42 passed in 0.34s ===============================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Code: part-4.py
```
python part-4.py
1: 0.818989
2: 0.577284
3: 0.814756
4: 0.644129
5: 0.79961
```

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Shopee cho phép người mua gửi yêu cầu trả hàng/hoàn tiền trong các trường hợp đủ điều kiện. | Chính sách trả hàng và hoàn tiền quy định các trường hợp người mua có thể yêu cầu hoàn trả sản phẩm. | cao | 0.818989 | Đúng |
| 2 | Sản phẩm hạn chế trả hàng chỉ được hoàn trả trong một số trường hợp nhất định. | Shopee hướng dẫn cách đóng gói đơn hàng trước khi giao cho đơn vị vận chuyển. | thấp | 0.577284 | Sai |
| 3 | Người mua có thể trả hàng vì đổi ý hoặc không còn nhu cầu nếu đáp ứng điều kiện của Shopee. | Một số sản phẩm được phép hoàn trả khi người mua thay đổi nhu cầu mua hàng. | cao | 0.814756 | Đúng |
| 4 | Chính sách bảo hành quy định việc hỗ trợ sản phẩm mua tại Shopee. | Người mua có thể theo dõi tình trạng vận chuyển của đơn hàng hoàn trả. | thấp | 0.644129 | Sai |
| 5 | Shopee có các phương thức gửi hàng hoàn trả và quy định về phí hoàn trả. | Khi trả hàng, người mua cần chọn phương thức vận chuyển và kiểm tra chi phí gửi hàng hoàn. | cao | 0.799610 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 2 và cặp 4 có điểm tương đồng cao hơn dự đoán ban đầu mặc dù nội dung không hoàn toàn cùng chủ đề. Điều này cho thấy embeddings vẫn nắm bắt được mối liên hệ ngữ nghĩa chung giữa các câu thuộc cùng lĩnh vực như trả hàng, vận chuyển và bảo hành, chứ không chỉ phụ thuộc vào sự trùng nhau của từ khóa.

---
## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Code: bench.py
```
python src/bench.py
bench.py
Indexing 369 chunks...
  indexed 10/369 chunks
  indexed 20/369 chunks
  indexed 30/369 chunks
  indexed 40/369 chunks
  indexed 50/369 chunks
  indexed 60/369 chunks
  indexed 70/369 chunks
  indexed 80/369 chunks
  indexed 90/369 chunks
  indexed 100/369 chunks
  indexed 110/369 chunks
  indexed 120/369 chunks
  indexed 130/369 chunks
  indexed 140/369 chunks
  indexed 150/369 chunks
  indexed 160/369 chunks
  indexed 170/369 chunks
  indexed 180/369 chunks
  indexed 190/369 chunks
  indexed 200/369 chunks
  indexed 210/369 chunks
  indexed 220/369 chunks
  indexed 230/369 chunks
  indexed 240/369 chunks
  indexed 250/369 chunks
  indexed 260/369 chunks
  indexed 270/369 chunks
  indexed 280/369 chunks
  indexed 290/369 chunks
  indexed 300/369 chunks
  indexed 310/369 chunks
  indexed 320/369 chunks
  indexed 330/369 chunks
  indexed 340/369 chunks
  indexed 350/369 chunks
  indexed 360/369 chunks
  indexed 369/369 chunks
Using embedding backend: gemini-embedding-001
Loaded 369 chunks from /mnt/c/Users/thaih/Projects/Vin/K4-DAY07-HoThaiHoa-2A202602915/data/doi-tra-bao-hanh
Agent backend: gemini_llm

Top-3 retrieval results (metadata filter: audience=buyer)


1. Query: Khi chọn đơn vị vận chuyển đến lấy hàng hoàn trả, đơn vị vận chuyển hỗ trợ tối đa bao nhiêu lần và trong khoảng thời gian nào?
   Gold: Tối đa 3 lần lấy hàng, trong vòng 1–3 ngày kể từ ngày lấy hàng đã chọn.
Direct use of automatic function calling (AFC) in Models.generate_content is not recommended. Instead, we recommend to use AFC in Chat.send_message. Similarly, direct use of AFC in Models.generate_content_stream is not recommended. Instead, we recommend to use AFC in Chat.send_message_stream.
   Agent answer: Dựa vào nội dung trong bài, khi bạn chọn hình thức đơn vị vận chuyển đến lấy hàng hoàn trả:

* **Số lần hỗ trợ tối đa:** Tối đa 3 lần lấy hàng khác nhau.
* **Khoảng thời gian:** Trong vòng 1-3 ngày kể từ ngày lấy hàng bạn đã chọn.
   Top-1: score=0.774572 doc_id=shopee-189477 chunk_id=shopee-189477#3
           Bước 34: Đăng tải bằng chứng trả hàng tại Chi tiết Trả hàng/hoàn tiền của đơn hàng đang hoàn trả Xem chi tiết Cách đóng gói đơn hàng hoàn trả và cách Tra cứu mã vận đơn trả hàng tại đây. 1.2. Lưu ý khi chọn Hình thức Đơn vị vận chuyển đến l...
   Top-2: score=0.760597 doc_id=shopee-79508 chunk_id=shopee-79508#6
           4. Giao hàng cho nhân viên nhận hàng hoàn trả: Thời gian chọn hình thức trả hàng: kiểm tra tại trang Chi tiết Trả hàng/Hoàn tiền Qúa hạn trả hàng mà đơn hàng chưa được giao cho nhân viên vận chuyển, đơn hàng sẽ bị hủy tự độn...
   Top-3: score=0.757682 doc_id=shopee-189477 chunk_id=shopee-189477#4
           Nếu đơn vị vận chuyển không đến lấy hàng đúng thời gian dự kiến hoặc cập nhật sai trạng thái hoàn hàng, bạn có thể: Liên hệ đơn vị vận chuyển hỗ trợ nhận đơn hàng hoàn trả của bạn để được hỗ trợ. Hoặc bạn cũng có thể chủ động mang hàng ra b...

2. Query: Khi nào người mua được hoàn lại phí vận chuyển ban đầu của đơn hàng?
   Gold: Khi yêu cầu Trả hàng/Hoàn tiền cho tất cả sản phẩm trong đơn và được Shopee/Người bán đồng ý hoàn đầy đủ giá trị đã thanh toán. Nếu chỉ yêu cầu cho một số sản phẩm thì không được hoàn phí vận chuyển ban đầu.
   Agent answer: Dựa vào đoạn văn bản trên, người mua sẽ được hoàn lại phí vận chuyển ban đầu khi:

* Người mua yêu cầu Trả hàng/Hoàn tiền cho **tất cả sản phẩm** trong đơn hàng đã đặt; **và**
* Được Shopee hoặc Người bán **đồng ý hoàn đầy đủ giá trị** mà người mua đã thanh toán. 

*(Lưu ý: Nếu chỉ yêu cầu Trả hàng/Hoàn tiền cho một số sản phẩm nhất định trong đơn hàng thì phí vận chuyển sẽ không được hoàn lại).*
   Top-1: score=0.800686 doc_id=shopee-189477 chunk_id=shopee-189477#8
           Nếu bạn yêu cầu Trả hàng/Hoàn tiền cho một số sản phẩm nhất định trong đơn hàng đã đặt (VD: yêu cầu Trả hàng/Hoàn tiền cho 1 trong 2 sản phẩm đã mua), phí vận chuyển sẽ không được hoàn lại cho bạn. 2.2. Phí vận chuyển trả hàng: Nếu bạn trả ...
   Top-2: score=0.761789 doc_id=shopee-189477 chunk_id=shopee-189477#7
           1.4. Lưu ý khi chọn hình thức Tự sắp xếp: Bạn phải lưu lại hóa đơn trả hàng với đầy đủ thông tin: Mã vận đơn, số điện thoại và đúng địa chỉ người nhận, không thu hộ (COD) 2. Chính sách hỗ trợ phí trả hàng: 2.1. Phí vận chuyển ban đầu khi yê...
   Top-3: score=0.748286 doc_id=shopee-189477 chunk_id=shopee-189477#10
           Đối với đơn hàng không thuộc Shopee Mall, Shopee sẽ hoàn lại khoản phí này dưới hình thức hoàn Shopee Xu sau khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận hoàn tiền và đáp ứng đầy đủ các điều kiện hỗ trợ phí trả hàng, số xu hoàn trả cố định...

3. Query: Sau khi yêu cầu trả hàng được chấp nhận, người mua chọn đơn vị vận chuyển đến lấy hàng thì cần thực hiện những bước nào?
   Gold: Chọn thời gian và địa chỉ lấy hàng → đóng gói hàng → dán phiếu gửi hàng hoặc viết mã vận đơn Shopee cung cấp lên hộp → bàn giao cho đơn vị vận chuyển tại địa chỉ và thời gian đã chọn.
   Agent answer: Sau khi chọn hình thức đơn vị vận chuyển đến lấy hàng, người mua cần thực hiện 4 bước sau:

* **Bước 1:** Chọn thời gian và địa chỉ lấy hàng
* **Bước 2:** Đóng gói hàng trong hộp vận chuyển
* **Bước 3:** Dán phiếu gửi hàng hoặc viết tay trực tiếp mã vận đơn được Shopee cung cấp lên hộp vận chuyển
* **Bước 4:** Đơn vị vận chuyển sẽ đến lấy hàng theo địa chỉ và thời gian đã chọn
   Top-1: score=0.809154 doc_id=shopee-189477 chunk_id=shopee-189477#1
           (Miễn phí trả hàng) Bước 1: Chọn thời gian và địa chỉ lấy hàng Bước 2: Đóng gói hàng trong hộp vận chuyển Bước 3: Dán phiếu gửi hàng hoặc viết tay trực tiếp mã vận đơn được Shopee cung cấp lên hộp vận chuyển Bước 4: Đơn v...
   Top-2: score=0.803451 doc_id=shopee-189477 chunk_id=shopee-189477#3
           Bước 34: Đăng tải bằng chứng trả hàng tại Chi tiết Trả hàng/hoàn tiền của đơn hàng đang hoàn trả Xem chi tiết Cách đóng gói đơn hàng hoàn trả và cách Tra cứu mã vận đơn trả hàng tại đây. 1.2. Lưu ý khi chọn Hình thức Đơn vị vận chuyển đến l...
   Top-3: score=0.803094 doc_id=shopee-189477 chunk_id=shopee-189477#4
           Nếu đơn vị vận chuyển không đến lấy hàng đúng thời gian dự kiến hoặc cập nhật sai trạng thái hoàn hàng, bạn có thể: Liên hệ đơn vị vận chuyển hỗ trợ nhận đơn hàng hoàn trả của bạn để được hỗ trợ. Hoặc bạn cũng có thể chủ động mang hàng ra b...

4. Query: Có những hình thức gửi hàng hoàn trả nào?
   Gold: Đơn vị vận chuyển đến lấy hàng; trả hàng tại bưu cục; tự sắp xếp.
   Agent answer: Dựa vào thông tin trong bài viết, có **2 hình thức** gửi hàng hoàn trả:

1. **Đơn vị vận chuyển đến lấy hàng** (Miễn phí trả hàng)
2. **Trả hàng tại bưu cục** (Miễn phí trả hàng)
   Top-1: score=0.804968 doc_id=shopee-189477 chunk_id=shopee-189477#0
           # [Trả hàng/ Hoàn tiền] Các phương thức gửi hàng hoàn trả và phí hoàn trả [Trả hàng/ Hoàn tiền] Các phương thức gửi hàng hoàn trả và phí hoàn trả | Shopee Trung tâm trợ giúp Xin chào, Shopee có thể giúp gì cho bạn? [Trả hàng/ Hoàn tiền] Các...
   Top-2: score=0.783820 doc_id=shopee-189477 chunk_id=shopee-189477#1
           (Miễn phí trả hàng) Bước 1: Chọn thời gian và địa chỉ lấy hàng Bước 2: Đóng gói hàng trong hộp vận chuyển Bước 3: Dán phiếu gửi hàng hoặc viết tay trực tiếp mã vận đơn được Shopee cung cấp lên hộp vận chuyển Bước 4: Đơn v...
   Top-3: score=0.779582 doc_id=shopee-79508 chunk_id=shopee-79508#6
           4. Giao hàng cho nhân viên nhận hàng hoàn trả: Thời gian chọn hình thức trả hàng: kiểm tra tại trang Chi tiết Trả hàng/Hoàn tiền Qúa hạn trả hàng mà đơn hàng chưa được giao cho nhân viên vận chuyển, đơn hàng sẽ bị hủy tự độn...

5. Query: Với hình thức ‘Tự sắp xếp’ để trả hàng, tôi có phải thanh toán trước phí vận chuyển không?
   Gold: Với đối tượng người mua: Có, người mua cần thanh toán trước phí vận chuyển trả hàng.
   Agent answer: Dựa trên thông tin được cung cấp trong đoạn văn:

**Có**, bạn cần phải thanh toán trước phí trả hàng (phí vận chuyển) nếu chọn hình thức **Tự sắp xếp**. 

Sau đó, Shopee sẽ hỗ trợ lại phí trả hàng cho bạn trong vòng 3 - 5 ngày làm việc (không tính Thứ 7, Chủ nhật, Ngày lễ & Tết) sau khi yêu cầu trả hàng/hoàn tiền của bạn được chấp nhận.
   Top-1: score=0.799102 doc_id=shopee-189477 chunk_id=shopee-189477#7
           1.4. Lưu ý khi chọn hình thức Tự sắp xếp: Bạn phải lưu lại hóa đơn trả hàng với đầy đủ thông tin: Mã vận đơn, số điện thoại và đúng địa chỉ người nhận, không thu hộ (COD) 2. Chính sách hỗ trợ phí trả hàng: 2.1. Phí vận chuyển ban đầu khi yê...
   Top-2: score=0.772454 doc_id=shopee-189477 chunk_id=shopee-189477#9
           Nếu bạn trả hàng qua hình thức Tự sắp xếp, bạn cần thanh toán trước phí trả hàng. Shopee sẽ hỗ trợ bạn phí trả hàng trong vòng 3 - 5 ngày làm việc (không kể Thứ 7, Chủ nhật, Ngày lễ & Tết) cụ thể như sau: Đối với đơn hàng thuộc Shopee Mall:...
   Top-3: score=0.744913 doc_id=shopee-189477 chunk_id=shopee-189477#8
           Nếu bạn yêu cầu Trả hàng/Hoàn tiền cho một số sản phẩm nhất định trong đơn hàng đã đặt (VD: yêu cầu Trả hàng/Hoàn tiền cho 1 trong 2 sản phẩm đã mua), phí vận chuyển sẽ không được hoàn lại cho bạn. 2.2. Phí vận chuyển trả hàng: Nếu bạn trả ...
```

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Khi chọn đơn vị vận chuyển đến lấy hàng hoàn trả, đơn vị vận chuyển hỗ trợ tối đa bao nhiêu lần và trong khoảng thời gian nào? | `shopee-189477#3`: Tối đa 3 lần lấy hàng trong vòng 1–3 ngày kể từ ngày lấy hàng đã chọn. | 0.774572 | Có | Tối đa 3 lần lấy hàng khác nhau trong vòng 1–3 ngày kể từ ngày đã chọn. |
| 2 | Khi nào người mua được hoàn lại phí vận chuyển ban đầu của đơn hàng? | `shopee-189477#8`: Nếu chỉ trả một số sản phẩm thì phí vận chuyển ban đầu không được hoàn lại. | 0.800686 | Có | Được hoàn khi trả hàng/hoàn tiền cho toàn bộ sản phẩm và được Shopee hoặc Người bán đồng ý hoàn đủ giá trị đã thanh toán. |
| 3 | Sau khi yêu cầu trả hàng được chấp nhận, người mua chọn đơn vị vận chuyển đến lấy hàng thì cần thực hiện những bước nào? | `shopee-189477#1`: Chọn thời gian/địa chỉ, đóng gói, dán phiếu hoặc mã vận đơn, rồi bàn giao cho đơn vị vận chuyển. | 0.809154 | Có | Thực hiện 4 bước: chọn thời gian và địa chỉ, đóng gói, dán phiếu hoặc mã vận đơn, bàn giao cho đơn vị vận chuyển. |
| 4 | Có những hình thức gửi hàng hoàn trả nào? | `shopee-189477#0`: Phần hướng dẫn liệt kê các hình thức gửi hàng hoàn trả và quy định phí trả hàng. | 0.804968 | Có, nhưng Agent thiếu 1 hình thức | Agent nêu đơn vị vận chuyển đến lấy hàng và trả tại bưu cục; chưa nêu hình thức tự sắp xếp. |
| 5 | Với hình thức ‘Tự sắp xếp’ để trả hàng, tôi có phải thanh toán trước phí vận chuyển không? | `shopee-189477#7`: Hình thức tự sắp xếp yêu cầu người mua lưu hóa đơn và liên quan đến chính sách hỗ trợ phí trả hàng. | 0.799102 | Có | Có. Người mua thanh toán trước phí trả hàng; Shopee hỗ trợ hoàn lại trong 3–5 ngày làm việc nếu đủ điều kiện. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Nhận xét:** Retrieval có chunk liên quan trong top-3 cho cả 5 câu hỏi. Ở câu 4, Agent chỉ nêu 2/3 hình thức dù kết quả retrieval có liên quan, cho thấy còn thiếu sót trong việc bao quát context khi sinh câu trả lời.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua demo của các thành viên khác, tôi học được rằng chất lượng retrieval không chỉ phụ thuộc vào model embedding mà còn phụ thuộc nhiều vào cách chunking và thiết kế metadata. Việc lọc đúng đối tượng bằng metadata như `audience=buyer` giúp giảm các kết quả không liên quan, còn việc kiểm tra cả câu trả lời của Agent giúp phát hiện trường hợp top-3 có vẻ phù hợp nhưng Agent vẫn bỏ sót một ý quan trọng.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |

