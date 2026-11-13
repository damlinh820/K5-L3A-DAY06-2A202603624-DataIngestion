# Báo cáo cá nhân — Day 06: Data Ingestion Engineering

## Thông tin học viên

- Họ và tên: Đàm Tuấn Linh
- MSSV: 2A202603624 · Lớp: L3A
- Chủ đề: Truy xuất bằng chứng từ Luật Đất đai số 31/2024/QH15.
- Repo: [K5-L3A-DAY06-2A202603624-DataIngestion](https://github.com/damlinh820/K5-L3A-DAY06-2A202603624-DataIngestion).
- Mốc chốt mã/kết quả thực nghiệm: [f3a1470](https://github.com/damlinh820/K5-L3A-DAY06-2A202603624-DataIngestion/commit/f3a1470c357e144a97248ae7a9023a3113562faf). Các commit sau cập nhật hồ sơ hoặc tinh gọn repo; không thay gold, chunk hay kết quả gốc.

## Dữ liệu và pipeline

Nguồn do học viên cung cấp: [Luật Đất đai 31/2024/QH15 — Cổng Thông tin điện tử Chính phủ](https://chinhphu.vn/?pageid=27160&docid=211189&classid=1&typegroupid=3), ngày ban hành 18/01/2024; kiểm tra nguồn ngày 13/11/2026. Ba PDF là **ba phần tiếp nối cùng một luật**, không phải ba luật khác nhau.

| File | PDF nguồn | Trang vật lý | Trang tính | Ký tự chuẩn hóa |
|---|---|---:|---|---:|
| luatdat1.pdf | [Phần 1](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_1.pdf) | 94 | 1–93 | 179.152 |
| luatdat2.pdf | [Phần 2](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_2.pdf) | 95 | 1–94 | 185.015 |
| luatdat3.pdf | [Phần 3](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_3.pdf) | 66 | 1–66 | 158.424 |
| **Tổng** | | **255** | **253 trang có text** | **522.591** |

Loại hai trang cuối rỗng của phần 1–2; không OCR vì PDF có text layer. Số trang là trang vật lý, bắt đầu từ 1 cho từng file, không phải số trang Công báo in trên header. 253 là số trang trích xuất được text, chưa phải kết quả rà thủ công chất lượng toàn bộ trang. Học viên đã xác nhận corpus và cách tính ở Gate 1.

[Manifest](../../data/manifest.json) lưu hash bản cục bộ, nguồn, quyền/ghi công, trang được tính và quy tắc chuẩn hóa. Chưa so hash bản tải mới từ cổng với bản cục bộ. Ghi nguồn “www.chinhphu.vn” theo yêu cầu của cổng; không tự gán giấy phép Creative Commons. Đây là bản công bố được cung cấp cho lab, chưa được hợp nhất sửa đổi để khẳng định pháp luật hiện hành. PDF gốc không đưa lên Git; có URL và snapshot để đối chiếu.

Pipeline: PDF → text từng trang → chuẩn hóa → A/B/C → embedding → Chroma → top-3 → đánh giá. `pdfplumber` trích xuất và lưu cả raw text, normalized text, source/page/error trong [pages.jsonl](../../results/pages.jsonl); [extraction_log.jsonl](../../results/extraction_log.jsonl) ghi trạng thái từng trang. Chuẩn hóa Unicode NFC, khoảng trắng, bỏ header Công báo và dòng chỉ có số; nối dòng gãy nhưng giữ marker Chương/Điều/Khoản/Điểm. Không đoán sửa từ tiếng Việt bị tách. Parser nhận đủ **260 Điều**, giữ phần mở đầu/Chương/Mục và phân biệt Khoản gốc với số Khoản trong trích dẫn sửa đổi.

Chunk giữ `document_id`, `source`, `part`, `page`, `page_end`, `n_tokens` và offset/provenance từng trang; B/C thêm Chương/Mục/Điều, C có Khoản. Tiêu đề lặp của C có context provenance riêng; trang chính là trang bắt đầu thân chunk. `part` từ file nguồn, là filter có thật do câu hỏi cung cấp trước truy xuất. A không có nhãn Điều tùy chọn nhưng vẫn truy nguồn được.

| Thành phần | Cấu hình thực tế |
|---|---|
| Môi trường | Python 3.12.14; pdfplumber 0.11.9; tiktoken 0.14.0; httpx 0.28.1; python-dotenv 1.2.4 |
| Embedding | OpenRouter API, request `openai/text-embedding-3-small`; response `text-embedding-3-small`, 1536 chiều, giới hạn input 8192 token |
| Lưu trữ | Chroma 1.5.9 PersistentClient, cosine HNSW approximate; chưa tuning index theo benchmark |
| Tokenizer | `cl100k_base`, dùng chung A/B/C và thống kê |
| Gọi API | Batch tối đa 32 input/20.000 token, retry giới hạn; lỗi dừng, không fallback vector giả |
| Nạp dữ liệu | IDs ổn định, upsert; lần nạp thứ hai vẫn 586/307/1.137 bản ghi |

Không có Docker nên dùng Chroma theo phương án cho phép. Probe thật kiểm tra lưu bền vững bằng process khác và filter; [embedding_probe.json](../../results/embedding_probe.json), [store_probe.json](../../results/store_probe.json). Phiên bản đầy đủ: [requirements.lock.txt](../../requirements.lock.txt), [environment.json](../../results/environment.json). Lệnh setup/kiểm tra/chạy lại ở [README](../../README.md); lần chạy lại lưu riêng dưới `runs/`, không đổi lần thực nghiệm gốc.

## Cấu hình và benchmark

| Cấu hình | Cách chia | Tham số |
|---|---|---|
| A — Fixed-size | Cửa sổ token, có thể cắt qua Điều | 512 token, overlap danh nghĩa 64 |
| B — Heading | Giữ trọn mỗi Điều, kể cả qua trang; context thành đơn vị riêng | 260 Điều + 47 đơn vị context |
| C — Hybrid | Điều dài hơn 512 token tách theo Khoản, lặp tiêu đề Điều | Giữ trọn Khoản; 512 là ngưỡng tách, không phải trần cứng |

A có 582 cặp overlap 64 token và ba cặp 65 token để không cắt ký tự UTF-8; mọi chunk A ≤512 token. C có 119 chunk >512 token do giữ đơn vị pháp lý dài. B lớn nhất 5.331 token, C lớn nhất 2.107; không vượt 8.192, không truncation/pooling.

A–B đổi cách chia theo cấu trúc; B–C chỉ đổi việc tách Khoản khi Điều dài. Giữ cùng corpus, model, store, metric, câu hỏi. Metadata filter đo **riêng B với B+filter trên cùng câu**, không quy chênh lệch B–C cho filter.

[questions.jsonl](../../benchmark/questions.jsonl) có **20 câu: 15 dev từ phần 1–2, 5 test từ phần 3**, câu trực tiếp, diễn đạt lại, điều kiện/ngoại lệ; ba câu filter q05/q12/q19, trong đó q19 là test. Mỗi câu có đáp án, nguồn/trang/quote và filter; chấp nhận gold thay thế đã liệt kê. Chia theo phần vẫn có nguy cơ rò rỉ thuật ngữ/dẫn chiếu trong cùng luật.

Học viên xác nhận Gate 2; evidence kiểm tra **20/20** theo nguồn/trang sau chuẩn hóa. Benchmark khóa và commit **65922c51745807d5b44e2b9d72845130769737e0 trước retrieval**; [LOCK.json](../../benchmark/LOCK.json) và [protocol.json](../../benchmark/protocol.json). So khớp quote không tự chứng minh đáp án đủ mọi điều kiện pháp lý. Không đưa gold answer/source vào query/filter.

Tiêu chí chọn trước test: **Hit@3 dev → Hit@1 dev → ít token tài liệu hơn → tên cấu hình theo thứ tự từ điển**. [dev_selection.json](../../results/dev_selection.json) lưu C và hash mã/chunk/trace trước [test_run.json](../../results/test_run.json). Không tune sau khi xem test. Hit yêu cầu một chunk chứa đủ evidence, đúng nguồn/trang/provenance; hợp nhiều chunk chỉ là chỉ số bổ sung, không thay Hit@3 chính.

## Kết quả

Nguồn: [metrics.csv](../../results/metrics.csv), [chunk_stats.csv](../../results/chunk_stats.csv), `ingest_A/B/C.json`, [embedding_usage.jsonl](../../results/embedding_usage.jsonl).

| Cấu hình | Split | Hit@1 | Evidence Hit@3 |
|---|---|---|---|
| A | Dev | 7/15 (46,67%) | 8/15 (53,33%) |
| B | Dev | 6/15 (40%) | 10/15 (66,67%) |
| C | Dev | 11/15 (73,33%) | 13/15 (86,67%) |
| A | Test | 1/5 (20%) | 3/5 (60%) |
| B | Test | 3/5 (60%) | 3/5 (60%) |
| C | Test | 1/5 (20%) | 4/5 (80%) |

| Cấu hình | Chunk | Token min/median/max | Tổng token chunk | Token API thực tế | Input mới embed | Wall ingest (giây) | Chi phí USD |
|---|---:|---|---:|---:|---:|---:|---:|
| A | 586 | 416/512/512 | 299.933 | 299.933 | 586 | 49,66 | 0,00599866 |
| B | 307 | 12/604/5.331 | 262.491 | 262.477 | 306 | 34,48 | 0,00524954 |
| C | 1.137 | 12/210/2.107 | 306.697 | 273.781 | 1.002 | 77,15 | 0,00547562 |

Wall time gồm lần upsert kiểm tra thứ hai; không gồm setup, trích xuất và chia chunk. Tổng 161,28 giây. A/B/C dùng chung cache từ response API thật, nên đây **không phải so sánh cold-cache độc lập**. Lần upsert thứ hai không gọi embedding lại.

Ingest: **836.191 token / 0,01672382 USD**. Query được embed một lần dùng chung: dev 792 token/0,00001584 USD, test 318/0,00000636 USD. Ingest+query: **837.301 token/0,01674602 USD**. Hai probe riêng: 58 token/0,00000116 USD. Tổng biết được **837.359 token/0,01674718 USD**. Không có bước LLM sinh câu trả lời.

| Filter đo riêng trên B | Hit@1 / Hit@3 trước | Hit@1 / Hit@3 sau | Câu có cả top-3 đúng phạm vi: trước → sau |
|---|---|---|---|
| Dev q05, q12 | 1/2 / 2/2 | 1/2 / 2/2 | 1/2 → 2/2 |
| Test q19 | 0/1 / 0/1 | 0/1 / 0/1 | 0/1 → 1/1 |

Filter làm phạm vi đúng trên 3/3 câu, không tăng số hit evidence trong mẫu này. Cùng query vector/index B, chỉ thêm `part` được câu hỏi cung cấp. Chi tiết [filter_comparison.json](../../results/filter_comparison.json), [trace_B_filter.jsonl](../../results/trace_B_filter.jsonl); baseline là đúng ba câu tương ứng trong trace B, không so với toàn bộ 20 câu.

### Coherence, metadata và grounding 

| Cấu hình | Coherence trung bình /2 (n) | Metadata đúng–đủ | Filter: câu có cả top-3 đúng phạm vi | Grounding 0/1/2 (số câu) | Grounding trung bình /2 |
|---|---|---|---|---|---|
| A | 1,00 (10) | 15/15 | 0/1 | 1/1/3 | 1,40 |
| B | 2,00 (10) | 15/15 | 0/1 | 0/2/3 | 1,60 |
| C | 2,00 (10) | 15/15 | 0/1 | 1/0/4 | 1,60 |

Nguồn: [audit_summary.json](../../results/audit_summary.json), [audit_coherence.csv](../../results/audit_coherence.csv) (30 dòng), [audit_metadata.csv](../../results/audit_metadata.csv) (45), [audit_grounding.csv](../../results/audit_grounding.csv) (15). Coherence dùng cùng [10 vị trí nguồn đã định trước](../../results/audit_positions.json); metadata dùng 5 test × top-3 × 3 cấu hình; grounding dùng 5 test × 3 cấu hình. Câu không yêu cầu filter là N/A; chỉ q19 vào mẫu số filter. A/B/C chính không áp dụng filter, cả ba đều có hit ngoài phần 3 nên đều 0/1.

Metadata được đối chiếu text layer 22 trang PDF liên quan, hash PDF, offset body/prefix, nguồn/trang/part và tiêu đề pháp lý; không phải rà bố cục bằng mắt hay kiểm tra cả 253 trang. Chi tiết kiểm tra nguồn: [ai_audit_source_checks.json](../../results/ai_audit_source_checks.json). A không bị trừ vì thiếu nhãn Điều tùy chọn. Mỗi dòng có `label_origin=ai_assisted`, `reviewer=Codex`, `human_verified=false`; phương pháp/hash tại [audit_method.json](../../results/audit_method.json). Giữ lại [audit_before_ai/](../../results/audit_before_ai/) gồm ba bảng trống trước khi chấm; hash khớp `original_sheet_sha256` trong hồ sơ phương pháp. Bảng trống và nhãn sau chấm là hai giai đoạn của quy trình, không phải các bản kết quả thay thế nhau.

## Phân tích và kết luận

- **Retrieval accuracy:** C có dev Hit@3 cao nhất, được chọn trước test. Test C đạt 4/5 so với A/B 3/5, nhưng B có Hit@1 3/5, cao hơn C 1/5. Chọn C cho mục tiêu đủ evidence trong top-3, không kết luận tốt nhất mọi tiêu chí.
- **Chunk coherence:** mẫu A đều giữ một số ý nhưng cắt đầu/cuối; B/C giữ Điều/Khoản trọn ý. Điểm 2/2 của B/C chỉ áp dụng 10 mẫu, không chứng minh mọi khoản đều tự đủ ngữ cảnh khi có dẫn chiếu.
- **Metadata usefulness:** 15/15 bản ghi mỗi cấu hình truy nguồn đúng, nhưng q19 vẫn có kết quả sai phạm vi. B+filter sửa phạm vi mà không tăng evidence; metadata đúng và đủ không đồng nghĩa truy xuất đúng nội dung.
- **Grounding quality:** B/C cùng 1,60 nhưng khác phân bố. B có hai câu đủ một phần, C bốn câu đủ và một câu không có bằng chứng. B/q19 có danh sách giấy ở phần 2 nhưng thiếu điều kiện đúng Điều 220/phần 3; C/q19 có evidence ở rank 3 dù hai hit đầu sai phạm vi.
- **Data strategy impact:** A→B tăng dev Hit@3 từ 8/15 lên 10/15 nhưng giảm Hit@1 một câu; B→C tăng lên 13/15 và 11/15. C có median nhỏ hơn nhưng lặp tiêu đề/tăng token và thời gian. Trên test C hơn B một câu Hit@3, kém hai câu Hit@1; không tune theo kết quả này.

### Ví dụ lỗi có trace

1. **C/dev/q03:** cần định nghĩa chiếm đất ở Điều 3 khoản 9, `luatdat1.pdf:2`; top-3 là Điều 178 khoản 1 (`luatdat3:6`), Điều 26 (`luatdat1:21`), Điều 207 khoản 1 (`luatdat3:25`). Có từ liên quan đất đai nhưng không có định nghĩa.
2. **C/dev/q08:** cần ngoại lệ giấy chứng nhận cho thừa kế tại Điều 45 khoản 1 điểm a, `luatdat1.pdf:40`; rank 1 là khoản 4 Điều 45, rank 2–3 là Điều 135 khoản 7 và Điều 138 khoản 9. Đúng số Điều chưa đủ khi sai Khoản.
3. **C/test/q17:** cần 50 năm/không làm thủ tục gia hạn ở Điều 172 khoản 1 điểm a, `luatdat3.pdf:2`; top-3 đều Điều 176 khoản 2/4/1 về hạn mức diện tích, không có thời hạn.
4. **A/test/q18:** rank 1 `luatdat3.pdf:3` bắt đầu bằng đuôi từ “ụng, đất rừng phòng hộ...” và kết luận ổn định lâu dài; mất tiền đề chuyển từ đất trồng cây hằng năm sang rừng đặc dụng. Hai hit còn lại nói hạn mức. Hit@3 không đạt, grounding AI 1/2.

Trace đầy đủ: [A](../../results/trace_A.jsonl), [B](../../results/trace_B.jsonl), [C](../../results/trace_C.jsonl); có question/gold, IDs/text, cosine distance, metadata/provenance và cờ evidence. Nếu mở rộng, thử kết hợp từ khóa/nhận diện Điều–Khoản trong một vòng thí nghiệm mới, chọn bằng dev và có test mới; chưa đưa cải tiến đó vào kết quả hiện tại.

### Giới hạn, checkpoint và AI

Corpus chỉ một luật, có thể lỗi khoảng trắng hoặc ranh giới qua trang/file; không xác minh pháp luật hợp nhất hiện hành. Chỉ năm câu test, không đại diện mọi corpus. Thời gian chịu ảnh hưởng cache dùng chung; audit AI chưa độc lập/chưa được học viên xác minh.

CLI chạy lại đã được kiểm tra bằng cache embedding thật, không thêm API trả phí, giữ nguyên 37 file kết quả gốc. Lần xây index mới vẫn chọn C nhưng B/test Hit@3 là 4/5 thay vì 3/5 do truy xuất HNSW approximate có thể thay thứ tự top-3. Không dùng lần tái lập để sửa các bảng gốc hoặc chọn lại cấu hình. Script kiểm tra trace tái tính chính xác các số liệu gốc mà không xây lại index.

| Checkpoint | Trạng thái |
|---|---|
| Dữ liệu/setup và benchmark | Gate 1–2 đã xác nhận; 20 câu khóa/commit trước retrieval |
| Chuẩn hóa/chunk/vector | Gate 3 đã xác nhận; đủ ba index, nạp lại không trùng |
| Retrieval và audit | Dev/test đã chạy; nhãn AI hoàn thành, chưa ghi nhận học viên xác minh |
| Báo cáo/nộp | Có báo cáo và repo; việc nộp link qua kênh lớp do học viên tự xác nhận |

Codex hỗ trợ code, kiểm tra nguồn, trích xuất, gọi embedding, chạy retrieval, chấm audit và viết báo cáo. Kiểm chứng bằng **13 tests**, gold 20/20, hash snapshot, so index/text/metadata, trace/usage thật và nhãn có lý do. Không dùng mock vector hay gọi điểm AI là chấm tay độc lập. Các file review và bản trùng đã được gỡ khỏi bản nộp hiện tại để dễ đọc; lịch sử commit giữ hồ sơ ban đầu. Không thay benchmark, gold, cấu hình được chọn hoặc số liệu để tăng điểm.
