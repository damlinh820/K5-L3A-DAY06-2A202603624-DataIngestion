# Báo cáo cá nhân — Day 06: Data Ingestion Engineering

> Báo cáo ngày 13/11/2026. Gate 1–3 đã được xác nhận; benchmark được khóa/commit trước retrieval. A/B/C đã ingest thật; dev chọn C trước test, đạt Evidence Hit@3 13/15 dev và 4/5 test. Theo yêu cầu bổ sung “vậy bạn chấm giúp mình”, Codex đã chấm đủ 30/45/15 dòng audit. Đây là **nhãn do AI hỗ trợ, chưa được học viên xác minh**, không phải nhãn thủ công độc lập.

## Thông tin học viên

- Họ và tên: Đàm Tuấn Linh
- MSSV: 2A202603624
- Lớp: L3A
- Chủ đề và corpus: Truy xuất bằng chứng từ Luật Đất đai số 31/2024/QH15, gồm ba PDF tiếp nối của cùng một văn bản.
- Repo bài nộp: https://github.com/damlinh820/K5-L3A-DAY06-2A202603624-DataIngestion
- Commit chốt bài (snapshot mã và kết quả): [f3a1470c357e144a97248ae7a9023a3113562faf](https://github.com/damlinh820/K5-L3A-DAY06-2A202603624-DataIngestion/commit/f3a1470c357e144a97248ae7a9023a3113562faf). Phần cập nhật mã commit/trạng thái trong hồ sơ được commit sau snapshot, không đổi mã hoặc kết quả thực nghiệm.

## Ghi chú xác nhận và trạng thái nộp bài

Phần kỹ thuật, báo cáo và snapshot kết quả đã được commit/push lên `origin/main` tại commit nêu trên. **Nhãn audit vẫn được công khai là AI hỗ trợ, chưa có ghi nhận cụ thể các dòng học viên xác minh.** Yêu cầu AI chấm hộ không tự đổi nhãn thành nhãn thủ công độc lập.

| Trạng thái | Nội dung | Đọc/kiểm tra ở đâu |
|---|---|---|
| Đã xác nhận — Gate 1 | Nguồn corpus, ba PDF tiếp nối và cách tính 253 trang có text | Mục “Nguồn và phạm vi dữ liệu”, “Số trang và quy tắc tính”; `data/approvals.json` |
| Đã xác nhận — Gate 2 | Bộ 20 câu/gold và split 15 dev/5 test trước retrieval | Mục “Bộ câu hỏi và gold”; `benchmark/REVIEW.md`, commit `65922c5` |
| Đã xác nhận — Gate 3 | Mẫu chunk A/B/C trước retrieval | Mục “Thiết kế theo AGENT_PLAN”; `results/CHUNK_REVIEW.md` và hồ sơ duyệt |
| Cần học viên xem xét — Gate 4 | Đọc điểm/lý do audit AI, đối chiếu mẫu và nguồn; báo các dòng đồng ý hoặc cần sửa | Mục “Kết quả” và “Phân tích và kết luận”; [AUDIT_REVIEW.md](../../results/AUDIT_REVIEW.md), ba CSV audit và [AUDIT_GUIDE.md](../../results/AUDIT_GUIDE.md) |
| Đã thực hiện — chốt Git | Snapshot mã/kết quả đã commit và push lên `origin/main`; ghi mã vào báo cáo/STUDENT.md trong commit cập nhật hồ sơ | Trường “Commit chốt bài” phía trên; [STUDENT.md](../../STUDENT.md) |
| Học viên tự xác nhận — nộp bài | Học viên đã đánh dấu mục quyền truy cập/nộp link trong checklist; agent không trực tiếp xác minh kênh nộp | Hướng dẫn [SUBMISSION.md](../../SUBMISSION.md); push Git không đồng nghĩa xác nhận nộp qua kênh lớp |

**Phần cần xem kỹ ở Gate 4:** coherence 30 dòng, metadata 45 dòng và grounding 15 dòng. Ví dụ dễ nhầm: B/q17 (nhận chuyển quyền khác giao/công nhận đất), A/q18 (mất tiền đề do cắt chunk), B/q19 (danh sách giấy ở phần 2 nhưng yêu cầu phần 3). C/q19 đủ bằng chứng ở rank 3 nhưng không đạt yêu cầu cả top-3 nằm trong phần 3. Metadata đúng nguồn/trang không đồng nghĩa retrieval đúng phạm vi.

Khi xem lại, ghi rõ các dòng đã kiểm tra và sửa nếu cần; chỉ xác nhận phần đã thực sự đọc. Một lời đồng ý chung không tự đổi toàn bộ nhãn `ai_assisted` thành nhãn thủ công độc lập. AI vẫn là nguồn tạo nhãn ban đầu; hồ sơ phải giữ dấu vết này.

**Các lựa chọn/giới hạn cần hiểu để giải thích bài:** C được chọn theo Hit@3 dev; B có Hit@1 test cao hơn C. Ngưỡng 512 của C không phải trần cứng cho Khoản; A có ba overlap 65 token để giữ ký tự UTF-8. Ba PDF là một luật, test chỉ năm câu, thời gian ingest có cache dùng chung. Đây là giải thích đã ghi trong báo cáo, không phải thí nghiệm còn thiếu hoặc gate xác nhận mới. Không bắt buộc rà thủ công lại cả 253 trang để hoàn thành các mẫu audit của bài.

Các ô đã/chưa hoàn thành được ghi ở [CHECKPOINTS.md](../../CHECKPOINTS.md). Plan gốc ở Downloads chưa được cập nhật dấu tick; không suy từ các ô trống đó rằng toàn bộ công việc còn chưa làm.

## Dữ liệu và pipeline

### Nguồn và phạm vi dữ liệu

Nguồn do học viên cung cấp: [Luật số 31/2024/QH15 của Quốc hội — Luật Đất đai, Cổng Thông tin điện tử Chính phủ](https://chinhphu.vn/?pageid=27160&docid=211189&classid=1&typegroupid=3). Trang nguồn ghi ngày ban hành 18/01/2024 và đính kèm ba PDF. Đã truy cập kiểm tra nguồn ngày 13/11/2026.

| Source ID | File cục bộ | PDF chính thức |
|---|---|---|
| `luatdat1` | `data/luatdat1.pdf` | [31-2024-qh15_1.pdf](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_1.pdf) |
| `luatdat2` | `data/luatdat2.pdf` | [31-2024-qh15_2.pdf](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_2.pdf) |
| `luatdat3` | `data/luatdat3.pdf` | [31-2024-qh15_3.pdf](https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/31-2024-qh15_3.pdf) |

Ba file có tên văn bản và số trang phù hợp với ba tệp đính kèm trên trang nguồn; chưa đối chiếu hash của bản tải từ mạng với bản học viên cung cấp. SHA-256 của các file cục bộ được lưu trong [manifest](../../data/manifest.json). Corpus này là bản công bố được cung cấp để làm lab; chưa được kiểm tra, hợp nhất các văn bản sửa đổi để khẳng định nội dung pháp luật đang có hiệu lực tại thời điểm sử dụng.

**Nguồn/quyền và ghi công:** Cổng Chính phủ yêu cầu ghi rõ nguồn “Cục Thông tin và Truyền thông Chính phủ” hoặc “www.chinhphu.vn” khi phát hành lại thông tin từ cổng. Báo cáo ghi nguồn theo yêu cầu này; không gán giấy phép Creative Commons cho tài liệu. Học viên đã xác nhận corpus và cách tính trang tại HUMAN GATE 1 ngày 13/11/2026; xác nhận được ghi trong [data/approvals.json](../../data/approvals.json). Điều này không có nghĩa học viên đã kiểm tra thủ công mọi trang.

### Số trang và quy tắc tính

| Source ID | Trang vật lý PDF | Trang có văn bản sau chuẩn hóa | Trang được tính | Trang loại | Ký tự sau chuẩn hóa |
|---|---:|---:|---|---|---:|
| `luatdat1` | 94 | 93 | 1–93 | 94: rỗng | 179.152 |
| `luatdat2` | 95 | 94 | 1–94 | 95: rỗng | 185.015 |
| `luatdat3` | 66 | 66 | 1–66 | Không | 158.424 |
| **Tổng** | **255** | **253** | | **2 trang rỗng** | **522.591** |

Các số liệu trên được sinh bằng `scripts/prepare_legal_corpus.py`, dùng **pdfplumber 0.11.9**, không OCR. Quy tắc hiện tại: tính trang có văn bản thân bài sau chuẩn hóa; loại trang rỗng hoặc lỗi trích xuất. **253 là số trang trích xuất được văn bản, chưa phải kết quả kiểm tra thủ công toàn bộ trang hoặc chất lượng nội dung.** Học viên đã xác nhận corpus ở Gate 1 và bộ câu hỏi/gold ở Gate 2.

Số trang trong manifest/gold là số trang vật lý PDF, bắt đầu từ 1 cho từng file; không dùng số trang Công báo in trên header làm `gold_page`.

Minh chứng đã tạo:

- [data/manifest.json](../../data/manifest.json): nguồn, hash, trang được tính và số ký tự.
- [results/pages.jsonl](../../results/pages.jsonl): `raw_text`, `text`, source ID, part, số trang và lỗi nếu có.
- [results/extraction_log.jsonl](../../results/extraction_log.jsonl): trạng thái từng trang vật lý.
- [results/PHASE1_REVIEW.md](../../results/PHASE1_REVIEW.md): hồ sơ kiểm tra Phase 1.

### Chuẩn hóa, lỗi và giới hạn

Đã chuẩn hóa Unicode NFC, thay khoảng trắng không ngắt dòng, thu gọn khoảng trắng ngang, bỏ dòng chứa header Công báo và dòng chỉ có số. Giữ ranh giới dòng để còn nhận diện Chương/Điều/Khoản/Điểm. Không đoán rồi tự sửa các từ tiếng Việt bị tách khoảng trắng. Lưu đồng thời text gốc và text chuẩn hóa để đối chiếu.

Đã thêm `src/normalize.py` để nối các dòng in bị ngắt trong cùng nội dung, đồng thời giữ marker Chương/Điều/Khoản/Điểm. Parser dùng offset toàn corpus và provenance theo trang, nhận diện đủ **260 Điều**; phần mở đầu/Chương/Mục được giữ thành đơn vị riêng. B giữ nguyên nội dung các Điều qua trang, C phân biệt Khoản gốc với số Khoản nằm trong trích dẫn sửa đổi. Bộ **13 kiểm tra tự động đã đạt**, gồm 8 kiểm tra chunk/provenance và 5 kiểm tra logic đánh giá/tiêu chí chọn dev. Có kiểm tra nguồn/trang phải chứa đúng quote, nhiều gold hợp lệ được chấp nhận và evidence bị tách qua nhiều hit không được tự tính thành một hit đơn. Các kiểm tra này không thay thế nhãn audit của học viên.

### Embedding, vector store và tài nguyên

Đã lấy danh sách embedding model trực tiếp từ OpenRouter và gọi thử một câu tiếng Việt qua `/api/v1/embeddings`. Kết quả thật được lưu trong [results/embedding_probe.json](../../results/embedding_probe.json):

| Thuộc tính | Giá trị đã xác nhận |
|---|---|
| Provider | OpenRouter API |
| Model gửi trong request | `openai/text-embedding-3-small` |
| Tên model trong response | `text-embedding-3-small` |
| Số chiều | 1536 |
| Usage của một câu thử | 21 prompt token / 21 total token |
| Giá input trong danh sách model tại lúc kiểm tra | 0,00000002 USD/token, tương đương 0,02 USD/triệu token |
| Chi phí API báo cho câu thử | 0,00000042 USD |

Đây chỉ là kết quả **một lần thử embedding**, không phải chi phí ingest toàn corpus hoặc kết quả benchmark. Không lưu API key trong artifact. Một lần gọi ban đầu bị sandbox chặn socket; lần gọi được cấp quyền mạng đã thành công, không dùng vector giả.

Chưa tìm thấy Docker trong PATH hoặc vị trí cài chuẩn, nên đã dùng **Chroma 1.5.9 local persistent, metric cosine** theo phương án trong plan. [results/store_probe.json](../../results/store_probe.json) ghi kiểm tra thật: ghi 2 bản ghi, upsert lại vẫn 2 bản ghi, mở lại bằng process khác vẫn đọc đủ 2 bản ghi; truy xuất đúng top-1 với vector của chính bản ghi và filter chỉ trả bản ghi thuộc nhóm được chỉ định. Kiểm tra này dùng embedding thật của hai câu hạ tầng riêng, không phải corpus hay câu benchmark. API báo 37 token, chi phí 0,00000074 USD cho lần kiểm tra này. Tổng hai lần probe API là 58 token, 0,00000116 USD, tách riêng khỏi chi phí ingest bên dưới.

Môi trường `starter/.venv` cũ không khởi động được do Python gốc không còn; đã tạo `.venv-legal` chạy Python 3.12.14 và cài dependencies. Phiên bản trực tiếp: pdfplumber 0.11.9, Chroma 1.5.9, tiktoken 0.14.0, httpx 0.28.1, python-dotenv 1.2.4. Xem [environment.json](../../results/environment.json), [requirements.txt](../../requirements.txt) và bản khóa toàn bộ [requirements.lock.txt](../../requirements.lock.txt).

Đã chạy `python -m src.ingest --config all --verify-reingest` bằng model đã khóa. Index ở `results/chroma/`, collections `land_law_a`, `land_law_b`, `land_law_c`, dùng cosine HNSW (approximate search, chưa tùy chỉnh index theo benchmark). Mỗi cấu hình upsert hai lần; số bản ghi lần hai lần lượt vẫn là **586 / 307 / 1.137**. Process kiểm tra riêng đã mở lại DB, so toàn bộ ID/text/metadata với artifact và xác nhận vector mẫu 1536 chiều. Đây là kiểm tra tính nhất quán lưu trữ, chưa phải nhãn audit metadata độc lập từ PDF.

### Metadata đã cài

Chunk giữ `document_id`, `source`, `part`, `page`, `page_end`, `n_tokens` và provenance chi tiết theo trang. B/C thêm `chapter`, `article`, `section`; chunk C tách theo Khoản có `clause`. A không gắn nhãn Chương/Điều bằng parser. `law_number` ghi ở manifest. `part` lấy từ file; Chương/Điều/Khoản lấy từ văn bản. Provenance của tiêu đề lặp lại ở C được giữ riêng với provenance thân chunk, tránh nhầm trang chứa evidence khi Điều đi qua nhiều trang. Filter chỉ dùng giá trị có thật được câu hỏi/ngữ cảnh cung cấp trước truy xuất. Đã có audit AI theo yêu cầu học viên, chưa có xác minh nhãn của học viên.

## Tiến độ theo checkpoint

| Mốc | Trạng thái | Minh chứng hiện có / phần còn lại |
|---|---|---|
| 0:25 — dữ liệu và setup | Đã hoàn thành, Gate 1 đã xác nhận | Manifest 253 trang, môi trường pin, embedding/store probe đạt; không tuyên bố rà thủ công mọi trang |
| 1:00 — benchmark | Đã hoàn thành, Gate 2 đã xác nhận | 20 câu/gold khóa và commit `65922c5` trước retrieval; kiểm tra evidence đạt |
| 1:50 — chuẩn hóa và chunk | Đã hoàn thành, Gate 3 đã xác nhận | Đủ 260 Điều; A/B/C: 586/307/1.137 chunk; kiểm tra chunk/provenance đạt |
| 2:40 — vector và ba chiến lược | Đã hoàn thành | Embed thật, lưu đủ ba index; nạp không nhân đôi, process riêng đọc lại đạt |
| 3:30 — benchmark và audit | Retrieval/audit AI đã xong; xác minh của học viên còn mở | Có trace dev/test và 30/45/15 nhãn AI; chưa đánh dấu học viên đã xem xét nhãn |
| 4:00 — báo cáo và nộp | Báo cáo/rà kỹ thuật và chốt Git đã xong; nộp link do học viên tự xác nhận | 13 tests, kiểm tra gold/index/trace/file đạt; snapshot đã push; agent không trực tiếp xác minh kênh nộp lớp |

Các mốc là checkpoint của bài, không phải ghi nhận thời gian thực tế đã hoàn thành. Thời gian ingest đo được nằm trong bảng kết quả; không bao gồm thời gian cài đặt/trích xuất/chia chunk ban đầu.

## Cấu hình và benchmark

### Thiết kế theo AGENT_PLAN — đã chạy trên dev và test

| Cấu hình | Cách chia | Tham số đã dùng |
|---|---|---|
| A — Fixed-size | Cửa sổ token, cho phép cắt qua Điều | 512 token, overlap 64; tokenizer cố định `cl100k_base` |
| B — Heading | Mỗi Điều là một chunk, kể cả Điều trải nhiều trang | Giữ số và tiêu đề Điều; không tách Khoản chỉ vì dài |
| C — Hybrid | Theo Điều; Điều vượt ngưỡng được tách tiếp theo Khoản | Ngưỡng 512 token; giữ tiêu đề Điều trong chunk con |

Implementation corpus mới ở `src/`, thay thế thiết kế Đà Lạt trong `starter/src` trước đó. Cả A/B/C đã ingest bằng cùng model OpenRouter và cùng Chroma; không dùng cấu hình local cũ cho corpus luật.

A–B đo thay đổi chiến lược chia theo cấu trúc; B–C đo ảnh hưởng của việc tách Khoản khi Điều dài. B có 260 chunk Điều và 47 chunk ngữ cảnh. Chunk B dài nhất 5.331 token, C dài nhất 2.107 token, đều dưới giới hạn 8.192 token của model; không cần cắt cụt hoặc pooling. C có 119 chunk vượt 512 token do giữ nguyên Khoản/đơn vị dài: 512 là ngưỡng quyết định tách Điều, không phải trần cứng của mỗi Khoản. A có 582 cặp chunk overlap đúng 64 token và 3 cặp overlap 65 token vì tránh cắt giữa ký tự UTF-8 tiếng Việt; mọi chunk A vẫn không vượt 512 token.

Đo **metadata filter riêng** bằng một biến thể cùng chunk và cùng model, ví dụ B với filter so với B không filter trên các câu có filter. Không quy kết chênh lệch B–C cho filter. Giữ nguyên corpus, model, store, cosine và bộ câu hỏi giữa các thí nghiệm.

### Bộ câu hỏi và gold

Đã duyệt và khóa [benchmark/questions.jsonl](../../benchmark/questions.jsonl) gồm 20 câu: **15 dev / 5 test**, **3 câu filter**, trong đó **1 câu test**. Có câu trực tiếp, diễn đạt lại, điều kiện/ngoại lệ và phạm vi phần văn bản được nêu rõ. Mỗi câu có `id`, `split`, `question`, `expected_answer`, `gold_source_id`, `gold_page`, `evidence_quote`, `filter`; các vị trí chứa cùng đoạn evidence được liệt kê trong `gold_evidence` để chấp nhận nhiều nguồn/trang hợp lệ.

Đã chạy `scripts/verify_evidence.py`: **20 câu đạt kiểm tra cấu trúc/provenance và evidence, không có lỗi**. [Kết quả kiểm tra](../../results/evidence_verification.json) ghi hash file và trạng thái từng quote. Script chỉ so khớp Unicode/whitespace và nguồn/trang; không chứng minh độc lập rằng đáp án đã đủ mọi điều kiện pháp lý. Học viên đã xác nhận Gate 2; [LOCK.json](../../benchmark/LOCK.json) ghi hash corpus/protocol/câu hỏi trước retrieval, commit **`65922c51745807d5b44e2b9d72845130769737e0`**. Sau Gate 3, đã chạy dev trước; [dev_selection.json](../../results/dev_selection.json) lưu lựa chọn C cùng hash mã/index trước [test_run.json](../../results/test_run.json). Không đổi cấu hình sau khi xem điểm test.

Không đưa gold answer/source vào query/filter. Vì ba PDF là một luật tiếp nối, chia theo file chưa bảo đảm độc lập theo nội dung; cần chọn chủ đề/Điều cho dev và test để hạn chế trùng, ghi nguy cơ rò rỉ. Chỉ dùng bản corpus đã chốt để xác minh evidence.

**Tiêu chí chọn cấu hình trước test:** ưu tiên Evidence Hit@3 trên dev, tiếp theo Hit@1 dev, sau đó ít token embedding tài liệu hơn khi đồng điểm; dùng tên cấu hình theo thứ tự từ điển làm quy tắc cuối để lựa chọn tái lập được. Tiêu chí được ghi trước retrieval trong [benchmark/protocol.json](../../benchmark/protocol.json). Coherence/grounding AI được báo riêng để phân tích sau thí nghiệm, không tham gia chọn lại cấu hình. Chốt cấu hình và tham số sau dev, rồi mới chạy test; không điều chỉnh theo test. Không đặt mục tiêu “tốt nhất tổng quát”.

## Kết quả

Đã có số liệu trích xuất, chunking, ingest, retrieval thật và audit AI được công khai phương pháp. **C được chọn theo retrieval trên dev trước khi chấm audit; không chọn lại theo điểm test/audit.** Số liệu tài nguyên từ [chunk_stats.csv](../../results/chunk_stats.csv), `ingest_A/B/C.json`, [embedding_usage.jsonl](../../results/embedding_usage.jsonl) và [phase3_summary.json](../../results/phase3_summary.json). Chỉ số retrieval lấy từ [metrics.csv](../../results/metrics.csv).

| Cấu hình | Số chunk | Token min / median / max | Tổng token trong các chunk | Token API thực tế | Input mới được embed | Chi phí API thực tế (USD) |
|---|---:|---|---:|---:|---:|---:|
| A | 586 | 416 / 512 / 512 | 299.933 | 299.933 | 586 | 0,00599866 |
| B | 307 | 12 / 604 / 5.331 | 262.491 | 262.477 | 306 | 0,00524954 |
| C | 1.137 | 12 / 210 / 2.107 | 306.697 | 273.781 | 1.002 | 0,00547562 |

Tổng ingest: **836.191 token API, 0,01672382 USD**; tách riêng 58 token/0,00000116 USD cho hai probe setup. A/B/C chia sẻ cache chỉ từ response API thật, nên số token gọi API của B/C ít hơn tổng token trong artifact. Cache và việc tái sử dụng text trùng cũng ảnh hưởng thời gian; bảng thời gian không phải so sánh cold-cache độc lập. Lần upsert thứ hai tái sử dụng vector đã tạo, không gọi API lại.

| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) |
|---|---|---|---|
| A | Dev | 7/15 (46,67%) | 8/15 (53,33%) |
| B | Dev | 6/15 (40%) | 10/15 (66,67%) |
| C | Dev | 11/15 (73,33%) | 13/15 (86,67%) |
| A | Test | 1/5 (20%) | 3/5 (60%) |
| B | Test | 3/5 (60%) | 3/5 (60%) |
| C | Test | 1/5 (20%) | 4/5 (80%) |

| Cấu hình | Wall time ingest có lần upsert kiểm tra thứ hai | Chi phí ingest thực tế |
|---|---:|---:|
| A | 49,66 giây | 0,00599866 USD |
| B | 34,48 giây | 0,00524954 USD |
| C | 77,15 giây | 0,00547562 USD |

Thời gian trên là wall time ingest từng cấu hình **bao gồm lần kiểm tra upsert thứ hai**, không bao gồm setup, trích xuất, chia chunk và toàn bộ thời gian chuẩn bị corpus. Tổng đo được của ba cấu hình là 161,28 giây.

Embedding câu hỏi được tạo một lần rồi dùng chung cho cả A/B/C và biến thể filter: dev 792 token/0,00001584 USD, test 318 token/0,00000636 USD. Tổng query là **1.110 token, 0,00002220 USD**. Ingest + query: 837.301 token/0,01674602 USD; cộng hai probe setup: **837.359 token/0,01674718 USD**. Không có chi phí sinh câu trả lời LLM vì thí nghiệm này chỉ truy xuất evidence.

### Metadata filter đo riêng trên B

| Split và mẫu | B không filter: Hit@1 / Hit@3 | B+filter: Hit@1 / Hit@3 | Top-3 tuân thủ phạm vi: trước → sau |
|---|---|---|---|
| Dev: q05, q12 (2 câu) | 1/2 / 2/2 | 1/2 / 2/2 | 1/2 → 2/2 |
| Test: q19 (1 câu) | 0/1 / 0/1 | 0/1 / 0/1 | 0/1 → 1/1 |

Theo [filter_comparison.json](../../results/filter_comparison.json), cùng query vector, model và index B, chỉ thêm `part` do câu hỏi cung cấp. Filter giúp phạm vi top-3 khớp metadata trên 3/3 câu, nhưng không cải thiện số hit evidence trong mẫu này. Đây là kiểm tra tự động giá trị metadata, chưa phải tỷ lệ metadata đúng-đủ được người học đối chiếu với PDF. Không so 2 câu B+filter dev trực tiếp với toàn bộ 15 câu B dev như hai mẫu có cùng mẫu số.

| Strategy | Coherence trung bình /2 (n) | Metadata đúng-đủ (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 và trung bình /2 |
|---|---|---|---|---|
| A | 1,00 (10) | 15/15 | 0/1 | 0: 1; 1: 1; 2: 3 — trung bình 1,40 |
| B | 2,00 (10) | 15/15 | 0/1 | 0: 0; 1: 2; 2: 3 — trung bình 1,60 |
| C | 2,00 (10) | 15/15 | 0/1 | 0: 1; 1: 0; 2: 4 — trung bình 1,60 |

**Bảng trên là AI-assisted audit, không phải nhãn thủ công độc lập.** Nguồn: [audit_summary.json](../../results/audit_summary.json), [AUDIT_REVIEW.md](../../results/AUDIT_REVIEW.md). Filter của A/B/C chính được chấm theo phạm vi câu hỏi q19: cả ba cấu hình có ít nhất một hit ngoài phần 3 nên 0/1 câu đạt điều kiện cả top-3. Các câu không yêu cầu filter là N/A, không tính vào mẫu số.

Trace đã lưu đầy đủ câu hỏi, gold, chunk IDs/text, khoảng cách cosine, metadata/provenance và kiểm tra evidence: [trace_A.jsonl](../../results/trace_A.jsonl), [trace_B.jsonl](../../results/trace_B.jsonl), [trace_C.jsonl](../../results/trace_C.jsonl). Có các file tách dev/test và biến thể B+filter. [phase4_integrity.json](../../results/phase4_integrity.json) xác nhận chỉ số khớp trace, lựa chọn dev được lưu trước test và hash mã đánh giá không đổi; việc kiểm tra lại không gọi retrieval lần nữa.

Gate 3 đã được xác nhận. Ở Gate 4, học viên yêu cầu Codex chấm hộ thay quy định người dùng tự chấm trong plan. Đã ghi đầy đủ điểm và lý do ở:

- [audit_coherence.csv](../../results/audit_coherence.csv): 30 dòng, cùng 10 vị trí đã chọn trước retrieval trong [audit_positions.json](../../results/audit_positions.json), điểm 0–2 và lý do.
- [audit_metadata.csv](../../results/audit_metadata.csv): 45 dòng = 5 test × top-3 × 3 cấu hình; ghi đúng-đủ và tuân thủ filter nếu có.
- [audit_grounding.csv](../../results/audit_grounding.csv): 15 dòng = 5 test × 3 cấu hình; đọc đủ top-3, điểm 0–2 và lý do.

Phương pháp: Codex đọc toàn bộ 30 chunk coherence và 15 bộ câu hỏi/top-3 grounding; giữ cùng rubric 0–2 cho A/B/C. Chunk có một số ý hoàn chỉnh nhưng bị cắt ở đầu/cuối được 1, đơn vị pháp lý trọn ý được 2; không tự trừ điểm chỉ vì Điều có dẫn chiếu. Grounding 1 dành cho mảnh bằng chứng/quy tắc liên quan nhưng thiếu tiền đề hoặc đúng phạm vi; 0 khi không có bằng chứng cho điều được hỏi. Ví dụ B/q17 có quy tắc miễn thủ tục của trường hợp nhận chuyển quyền nhưng thiếu thời hạn và sai trường hợp giao/công nhận nên 1; A/q19 chỉ có giấy tờ ở các thủ tục khác, sai phạm vi nên 0. Không suy nhãn trực tiếp từ Hit@3.

Metadata được AI xem xét với kiểm tra nguồn bằng script: kiểm tra hash ba PDF, trích xuất lại text layer ở **22 trang liên quan** (gồm các trang gold test), đối chiếu văn bản với snapshot đã khóa; so khớp offset body/prefix, nguồn/trang/part và các tiêu đề Chương/Mục/Điều/Khoản. Cả 45 bản ghi đạt đúng-đủ nguồn/trang; đây không phải kiểm tra bố cục bằng mắt hoặc rà toàn bộ 253 trang. Source check chi tiết: [ai_audit_source_checks.json](../../results/ai_audit_source_checks.json).

Mỗi dòng có `label_origin=ai_assisted`, `reviewer=Codex`, `human_verified=false`. [audit_method.json](../../results/audit_method.json) ghi yêu cầu học viên, quy trình, hash bảng trước/sau và hạn chế; bản bảng trống được giữ trong `results/audit_before_ai/`. Cùng assistant đã viết pipeline và nhìn thấy điểm retrieval rồi mới chấm, nên **không độc lập, không làm mù, có nguy cơ thiên lệch**. Chưa ghi nhận học viên xem xét/xác minh nhãn; cần phân biệt với yêu cầu chấm thủ công của GUIDE. Không biết chính xác phiên bản model trong phiên nên không tự gán tên model. Không gọi thêm API embedding/sinh câu trả lời trong bước ghi audit này. Script tổng hợp chỉ đọc điểm đã ghi, kiểm tra nhãn hợp lệ và công khai nguồn AI.

## Phân tích và kết luận

- **Retrieval accuracy:** C đạt dev Hit@3 cao nhất (13/15), được chọn trước test theo protocol. Trên test, C có Hit@3 4/5 so với A/B 3/5, nhưng Hit@1 của B là 3/5, cao hơn C 1/5. C phù hợp hơn với mục tiêu ưu tiên lấy đủ evidence trong top-3 của thí nghiệm này; chưa thể kết luận tốt nhất ở mọi tiêu chí. Hit tự động yêu cầu quote nằm trong text và đúng vùng provenance của nguồn/trang gold, chấp nhận các gold thay thế đã ghi. Không tính hợp nhiều chunk thành một hit đơn.
- **Chunk coherence:** AI chấm A trung bình 1,00/2, B/C 2,00/2 trên cùng 10 vị trí đã chọn trước retrieval. Cả 10 chunk A còn ý đọc được nhưng có phần bị cắt, ví dụ Điều 260 mất dẫn chiếu ở cuối khoản 1; B giữ đủ Điều, C giữ tiêu đề và Khoản. Không suy rộng điểm tối đa của mẫu B/C cho tất cả chunk, nhất là các khoản dẫn chiếu hoặc phụ thuộc nhau.
- **Metadata usefulness:** cả A/B/C đạt 15/15 đúng-đủ theo kiểm tra text/provenance của mẫu; A không có nhãn Điều nhưng vẫn truy nguồn được. Metadata đúng không có nghĩa retrieval đúng phạm vi: A/B/C chính đều 0/1 câu test tuân thủ toàn bộ top-3. B+filter làm phạm vi top-3 đúng `part` trên 3/3 câu so với 1/3 khi không filter; số hit evidence không tăng. Tiêu đề lặp của C có nguồn/trang riêng, phải đọc cả context provenance để truy vết.
- **Grounding quality:** AI chấm A 1,40/2; B/C cùng 1,60/2 nhưng phân bố khác nhau: B có hai câu chỉ đủ một phần, C có bốn câu đủ và một câu không có bằng chứng. B/q19 có danh sách giấy trong quy định liên quan ở phần 2 nhưng chưa đủ chứng minh điều kiện Điều 220 ở phần 3; C/q19 có đúng bằng chứng ở rank 3, dù hai hit đầu vi phạm phạm vi. Chỉ đánh giá độ đủ của bằng chứng top-3, không phải độ chính xác câu trả lời do LLM sinh; không thay kết quả Hit@3 tự động bằng nhãn này.
- **Data strategy impact:** A–B tăng dev Hit@3 từ 8/15 lên 10/15 nhưng giảm dev Hit@1 từ 7/15 xuống 6/15. B–C tăng dev Hit@3 lên 13/15 và Hit@1 lên 11/15. C có median nhỏ hơn B nhưng thêm token do lặp tiêu đề. Trên test, C hơn B một câu ở Hit@3 nhưng thấp hơn hai câu ở Hit@1; cần ghi rõ đánh đổi theo mục tiêu và hạn chế mẫu nhỏ. Không điều chỉnh cấu hình theo các điểm test này.

### Ví dụ lỗi có trace thực tế

1. **C/dev/q03 — nhầm nội dung định nghĩa:** gold là khoản 9 Điều 3, `luatdat1.pdf`, trang 2, định nghĩa chiếm đất. Top-3 lại là Điều 178 Khoản 1 (`luatdat3.pdf:6`), Điều 26 (`luatdat1.pdf:21`) và Điều 207 Khoản 1 (`luatdat3.pdf:25`); không chứa đủ evidence gold. Các kết quả có nhiều từ liên quan quyền sử dụng đất nhưng không trả được định nghĩa cần hỏi.
2. **C/dev/q08 — đúng Điều nhưng sai Khoản:** câu hỏi về ngoại lệ Giấy chứng nhận cho thừa kế ở điểm a khoản 1 Điều 45, gold `luatdat1.pdf:40`. Top-1 là Khoản 4 Điều 45 ở trang 41; top-2/3 là Điều 135 Khoản 7 và Điều 138 Khoản 9. Trả về cùng số Điều ở top-1 chưa đủ để tính hit khi thiếu điều kiện/ngoại lệ được hỏi.
3. **C/test/q17 — truy xuất quy định được dẫn chiếu thay vì thời hạn:** gold điểm a khoản 1 Điều 172 ở `luatdat3.pdf:2` nói 50 năm và không phải làm thủ tục gia hạn trong trường hợp được nêu. Top-3 là Điều 176 Khoản 2, 4, 1, ở trang 4–5, liên quan hạn mức đất; không chứa quy định thời hạn cần hỏi. Đây là quan sát sau test để phân tích lỗi, không được dùng để sửa tham số của lần đánh giá hiện tại.
4. **A/test/q18 — mất tiền đề do cắt giữa ý:** rank 1 tại `luatdat3.pdf:3` bắt đầu bằng đuôi từ “ụng, đất rừng phòng hộ...” rồi kết luận ổn định lâu dài. Mất phần xác định chuyển từ đất trồng cây hằng năm sang đất rừng đặc dụng; hai hit còn lại nói hạn mức Điều 176. Vì vậy không đạt Evidence Hit@3 và AI chỉ chấm grounding 1/2: có mảnh kết luận nhưng không đủ tiền đề để trả lời chắc chắn.

Các trường hợp khác nằm trong [failure_cases.md](../../results/failure_cases.md). Nếu mở rộng sau bài này, có thể thử kết hợp từ khóa hoặc nhận diện Điều/Khoản do người dùng nêu trên một vòng thí nghiệm mới, chọn tham số bằng dev và dành một tập test mới; chưa thực hiện các cải tiến đó trong kết quả hiện tại.
- **Giới hạn:** corpus chỉ gồm một luật trong ba file tiếp nối, chưa kiểm tra chất lượng toàn bộ 253 trang thủ công; có thể có lỗi khoảng trắng và ranh giới qua trang/file. Benchmark 5 câu test có độ đại diện hạn chế. Nhãn audit do cùng AI viết pipeline chấm sau khi biết điểm, chưa được học viên xác minh; không xem là bằng chứng đánh giá độc lập. Không suy rộng thành phương pháp tốt nhất cho mọi corpus hoặc tư vấn pháp lý hiện hành.
- **AI và cách kiểm tra:** dùng Codex để đọc hướng dẫn, viết script, trích xuất PDF, kiểm tra nguồn, gọi embedding, chạy retrieval, chấm audit theo yêu cầu mới và soạn báo cáo. Số liệu lấy từ manifest/log/response API/trace; không dùng mock vector. Gold và chunk được học viên xác nhận ở Gate 2–3; audit ghi rõ nhãn AI và lý do từng dòng, kiểm tra lại text layer 22 trang nguồn và bảo toàn hash benchmark/index. Chưa tuyên bố học viên xác minh nhãn AI.
- **Việc học viên cần lưu ý:** snapshot mã/kết quả đã commit và push. Xem lại nhãn AI, nhất là grounding một phần và filter; xác nhận nộp link theo kênh lớp. Nếu sửa nhãn, ghi rõ người sửa và phương pháp thay vì ngầm đổi nhãn AI thành nhãn người.

### Kiểm tra trước khi đưa lên repo

Đã chạy lại 13 kiểm thử tự động, xác minh 20 gold evidence và kiểm tra toàn bộ index A/B/C; đều đạt. Kiểm tra trace lưu sẵn khớp chỉ số, thứ tự dev trước test và hash mã đánh giá không đổi; không gọi retrieval lại. Các bảng audit đủ 30/45/15 dòng, không thiếu điểm/lý do; nguồn gốc AI được giữ rõ. [submission_check.json](../../results/submission_check.json) ghi rà file chuẩn bị đưa lên Git, syntax Python, liên kết báo cáo, hash nhãn và dấu hiệu credential; không in giá trị secret. PDF gốc, `.env`, venv, cache và Chroma không đưa vào Git; có nguồn và snapshot/trace để kiểm tra. Xem [SUBMISSION_REVIEW.md](../../results/SUBMISSION_REVIEW.md) để phân biệt phần đã có minh chứng với phần học viên cần xử lý.
