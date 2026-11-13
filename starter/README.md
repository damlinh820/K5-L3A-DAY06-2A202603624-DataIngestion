# Starter · PostgreSQL + pgvector

> Đây là triển khai Đà Lạt trước khi đổi corpus, được giữ để tham khảo. Bài nộp Luật Đất đai hiện tại dùng `src/`, `data/` và `results/` ở thư mục gốc với OpenRouter + Chroma. Xem [README chính](../README.md) để kiểm tra kết quả bài nộp; các lệnh bên dưới thuộc pipeline cũ.

Starter tùy chọn cho lab cá nhân. Bộ khung `src/` đã được nối thành pipeline Python chạy local; cần đặt dữ liệu và benchmark của học viên vào đúng vị trí trước khi chạy. Có thể thay pgvector bằng vector store tương đương nếu ghi rõ cấu hình trong báo cáo.

## Cấu trúc chính

```text
starter/
├── docker-compose.yml
├── requirements.txt
├── requirements-embeddings.txt
├── .env.example
├── scripts/check_setup.py
├── src/                 # ingestion, chunking, embeddings, pgvector, evaluation, run
├── data/manifest.json   # manifest mẫu cho hai bài Wikipedia về Đà Lạt
├── data/*.pdf           # bạn tự đặt các PDF được phép xử lý
└── results/             # thống kê, trace và mẫu audit được tạo khi chạy
```

## 1. Cài và kiểm tra database

Cần Docker Desktop/Engine + Compose, Python **3.11–3.14**, và mạng để tải dependencies/model lần đầu. Chạy các lệnh từ thư mục `starter/`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-embeddings.txt
Copy-Item .env.example .env
docker compose -p day6_student_starter up -d --wait
python scripts/check_setup.py
```

Kỳ vọng setup báo PostgreSQL và pgvector, sau đó `Setup OK`; đây chỉ là kiểm tra hạ tầng. Docker chỉ mở cổng local `127.0.0.1:55433`; mật khẩu trong compose chỉ dùng cho lab local. Nếu cổng bận, đổi port trong compose và `DATABASE_URL` trong `.env`. Dừng database mà giữ volume bằng `docker compose -p day6_student_starter stop`.

## 2. Embedding local

Adapter dùng model multilingual Sentence Transformers mặc định `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; model báo 384 chiều. Tài liệu và query dùng cùng model. Lần đầu cần mạng để tải trọng số; mặc định chạy CPU. Có thể đổi `EMBEDDING_MODEL`, `EMBEDDING_DEVICE` và `EMBEDDING_BATCH_SIZE` trong `.env`. Các API key mẫu chưa được adapter này sử dụng; không cần API key cho cấu hình local. Ghi phiên bản package, model và thiết bị thực tế vào báo cáo.

## 3. Đặt corpus và benchmark

1. Đặt PDF theo `local_path` trong [`data/manifest.json`](data/manifest.json), hoặc sửa đường dẫn đó. Manifest dùng URL revision cố định, page range nội dung và metadata `article`. Không tính các trang chỉ có tham khảo. Kiểm tra quyền/giấy phép và ghi công; PDF trong `data/` bị Git ignore mặc định vì có thể chứa ảnh với giấy phép riêng. Nếu không được phép nộp PDF gốc, nộp manifest/hướng dẫn lấy dữ liệu theo yêu cầu môn học.
2. Trước khi full run, tạo `benchmark/questions.json` theo [BENCHMARK.md](../BENCHMARK.md): tối thiểu 20 câu, 15 dev / 5 test, ít nhất 3 câu có filter và 1 câu filter trong test. Gold source/page/evidence phải được kiểm tra thủ công trên bản nguồn. Câu có filter phải cung cấp phạm vi trước truy xuất và dùng giá trị metadata thật.

Mẫu một câu hỏi:

```json
{
  "id": "q01",
  "split": "dev",
  "question": "Câu hỏi được diễn đạt tự nhiên",
  "expected_answer": "Đáp án kiểm chứng từ nguồn",
  "gold_source_id": "dalat",
  "gold_page": 1,
  "evidence_quote": "Đoạn ngắn được kiểm tra trực tiếp",
  "filter": {}
}
```

Để filter chiến lược C theo tài liệu, ví dụ: `"filter": {"article": "Lịch sử Đà Lạt"}`. Không đưa đáp án hoặc gold source vào query/filter.

## 4. Chạy pipeline

Từ thư mục `starter/`:

```powershell
python -m src.run --ingest-only
python -m src.run
```

`--ingest-only` tạo index A (fixed 500/50), B (theo đoạn, tối đa 1000 ký tự), C (cùng chunk với B, filter chỉ lúc search) nhưng không chạy benchmark. Lệnh thứ hai cần benchmark hợp lệ; nó chạy top-3 cho mọi câu trên cả ba strategy và ghi:

- `results/ingest_summary.json`: số trang/chunk, kích thước và thời gian ingest.
- `results/traces.jsonl`: câu hỏi, kết quả top-3, metadata và nhãn evidence tự động.
- `results/retrieval_summary.json`: Hit@1 và Evidence Hit@3 theo split.
- `results/manual_audit_template.csv`: mẫu trống để học viên tự chấm coherence, metadata/filter và grounding.

Adapter đánh giá tự động chỉ đo khớp gold evidence; nó không suy ra nhãn coherence hoặc grounding. Người học phải kiểm tra nhãn thủ công và ghi hạn chế. Mỗi lần chạy sẽ thay index theo strategy trong một transaction để không giữ chunk cũ hoặc nhân đôi dữ liệu. Không có fallback vector giả khi model/database lỗi.

Lưu code, lệnh chạy, cấu hình và kết quả để tái lập. Không commit `.env`, API key, dữ liệu riêng tư hoặc nội dung không có quyền chia sẻ.
