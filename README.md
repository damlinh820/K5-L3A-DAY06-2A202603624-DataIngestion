# Data Ingestion — Luật Đất đai 31/2024/QH15

Bài cá nhân của **Đàm Tuấn Linh · 2A202603624 · L3A**. So sánh A fixed-size, B theo Điều và C theo Điều/Khoản trên ba PDF tiếp nối của cùng một luật, tổng 253 trang có text.

**Đọc kết quả:** [Báo cáo](report/individual/2A202603624_DamTuanLinh.md) · [Chỉ số dev/test](results/metrics.csv) · [Corpus và nguồn PDF](data/manifest.json).

## Cài đặt

Python 3.12; chạy PowerShell tại thư mục gốc, không cần kích hoạt venv:

```powershell
python -m venv .venv-legal
.\.venv-legal\Scripts\python.exe -m pip install -r requirements.lock.txt
```

Nếu đã có venv thì bỏ lệnh tạo lại. Có thể dùng `py -3.12` thay `python`. Tokenizer `cl100k_base` có thể cần mạng tải dữ liệu lần đầu.

## Kiểm tra kết quả đã nộp

Không cần API key hoặc Chroma gốc:

```powershell
.\.venv-legal\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-legal\Scripts\python.exe scripts/verify_evidence.py
.\.venv-legal\Scripts\python.exe scripts/check_phase4_integrity.py
.\.venv-legal\Scripts\python.exe scripts/summarize_manual_audits.py --check-only
```

Các lệnh kiểm tra 13 tests, gold của 20 câu, chỉ số so với trace và nhãn audit. Chúng không gọi embedding hay chạy lại retrieval. Bỏ `--check-only` để tổng hợp lại `results/audit_summary.json` từ nhãn đã ghi.

## Chạy lại pipeline

Chỉ chuẩn hóa/chia chunk, không gọi API:

```powershell
.\.venv-legal\Scripts\python.exe -m src.run --output runs/prepare01 --prepare-only
```

Để chạy đủ embedding, ingest và retrieval, sao chép `.env.example` thành `.env`, điền `OPENROUTER_API_KEY`, rồi chạy:

```powershell
Copy-Item .env.example .env
# Điền key vào .env; không ghi key trong lệnh hoặc commit lên Git.
.\.venv-legal\Scripts\python.exe -m src.run --output runs/run01
```

Nếu đã có `.env`, giữ file đó. Model: OpenRouter `openai/text-embedding-3-small`, 1536 chiều; Chroma persistent cosine. Lệnh chạy tạo A/B/C, batch embed thật, upsert hai lần để kiểm tra không trùng, chạy dev → lưu lựa chọn → chạy test; đo B/B+filter riêng trên cùng câu có yêu cầu phạm vi. Không tự sinh nhãn audit mới.

Mỗi lần chạy phải dùng **thư mục mới dưới `runs/`**. Index, cache, usage, log, trace và metrics mới nằm ở đó; không ghi đè `results/` đã nộp. Kết quả chạy lại là tái lập trên benchmark đã biết, không phải holdout mới; thời gian/chi phí có thể khác. Có thể thêm `--reuse-cache results/embedding_cache.jsonl` nếu máy đã có cache từ API thật; cache được sao chép sang lần chạy mới. Không dùng vector giả khi lỗi API.

Chroma dùng HNSW approximate: xây lại index có thể thay top-3 và chỉ số dù dùng cùng vector. Lần kiểm tra CLI bằng cache thật vẫn chọn C; B/test Hit@3 thành 4/5 thay vì 3/5 ở lần gốc. Các bảng trong báo cáo giữ kết quả gốc; dùng kiểm tra trace ở trên để tái tính chính xác số liệu đã nộp, không thay bằng lần chạy thuận lợi hơn.

Pipeline chạy lại từ snapshot văn bản theo trang `results/pages.jsonl`. PDF gốc không cần cho bước này. Muốn đối chiếu PDF, tải ba tệp qua URL trong manifest, đặt tại `data/luatdat1.pdf` đến `luatdat3.pdf`, kiểm tra hash. `scripts/prepare_legal_corpus.py` là mã trích xuất PDF đã dùng; nó bảo vệ snapshot đã khóa nên không ghi đè corpus hiện tại. Bản tải mới từ cổng chưa được xác minh có hash giống hệt bản học viên cung cấp.

## File chính

| Đường dẫn | Nội dung |
|---|---|
| `src/` | Chuẩn hóa, chunking, embedding, lưu trữ, retrieval, đánh giá và CLI chạy lại |
| `scripts/` | Bốn tiện ích: trích xuất PDF, kiểm chứng gold, kiểm tra trace, tổng hợp audit |
| `benchmark/` | 20 câu/gold, split 15 dev/5 test, protocol và khóa trước retrieval |
| `data/` | Manifest nguồn và xác nhận corpus/benchmark/chunk |
| `results/` | Snapshot trang/chunk, trace, số liệu, usage/log và ba bảng audit có lý do |
| `artifacts/experiment_log.csv` | Cấu hình, giả thuyết và kết quả A/B/C |
| `report/individual/` | Báo cáo duy nhất của học viên |

C được chọn trước test: Hit@3 **13/15 dev, 4/5 test**. Audit coherence/metadata/grounding được Codex chấm theo yêu cầu học viên, có `label_origin=ai_assisted`; **chưa có xác minh độc lập của học viên**. Phương pháp và giới hạn nằm trong báo cáo và `results/audit_method.json`.

PDF, `.env`, venv, cache, Chroma và `runs/` bị Git ignore. Các tài liệu GUIDE/RULES/BENCHMARK/RUBRIC/SUBMISSION giữ yêu cầu gốc của bài; người chấm có thể bắt đầu từ README này và báo cáo.
