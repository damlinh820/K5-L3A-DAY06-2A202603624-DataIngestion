# Rà soát bài nộp — 2A202603624

Đối chiếu README, GUIDE, BENCHMARK, RULES, RUBRIC và SUBMISSION ngày 13/11/2026. Đây là kiểm tra minh chứng, không phải điểm do giảng viên chấm.

Trạng thái tick từng Phase/Gate ở [CHECKPOINTS.md](../CHECKPOINTS.md). Các mục cần học viên xác minh đã được đặt ngay đầu [báo cáo](../report/individual/2A202603624_DamTuanLinh.md), trong phần “Ghi chú cho học viên trước khi đưa lên Git”. Gate 1–3 đã xác nhận; Gate 4 còn xem xét nhãn AI; commit cuối, push và nộp link chưa hoàn thành.

| Yêu cầu | Minh chứng và trạng thái |
|---|---|
| Corpus ≥30 trang, nguồn/quyền và truy vết | Manifest: 253 trang có text, ba phần tiếp nối cùng một luật; nguồn Chính phủ, hash PDF, quy tắc loại hai trang rỗng và ghi công. Chưa rà thủ công mọi trang. |
| Đọc/chuẩn hóa/ghi lỗi | pages.jsonl có raw text và normalized text; extraction_log.jsonl ghi từng trang; offset/provenance bảo toàn. |
| Ba chiến lược và so sánh có kiểm soát | A 512/64; B nguyên Điều; C tách Điều dài theo Khoản; cùng corpus/model/metric. B với B+filter đo riêng trên cùng ba câu có yêu cầu phạm vi. |
| Model thật, store bền vững, nạp không trùng | OpenRouter text-embedding-3-small, 1536 chiều; Chroma cosine; ingest/probe/index checks thật, số bản ghi lần hai không đổi. |
| ≥20 câu, gold/split trước retrieval | 15 dev/5 test, ba câu có filter (một test), benchmark commit 65922c5 trước retrieval, kiểm tra evidence 20/20. |
| Trace/Hit@1/Hit@3, chọn dev trước test | metrics.csv và trace; dev_selection.json khóa C trước test_run.json; integrity check đạt, không tune theo test. |
| Coherence/metadata/grounding | Có 30/45/15 nhãn và lý do do Codex chấm theo yêu cầu học viên. **AI-assisted, chưa được học viên xác minh; không đánh dấu đã hoàn thành chấm thủ công độc lập.** |
| Phân tích đủ năm khía cạnh | Báo cáo cá nhân có retrieval, coherence, metadata, grounding, data strategy impact; nêu ít nhất bốn lỗi có ID/nguồn, trade-off và mẫu test nhỏ. |
| Lệnh, phiên bản, thời gian/chi phí | README, requirements.lock.txt, environment.json, usage/ingest/retrieval logs; cache dùng chung và giới hạn so sánh thời gian được nêu rõ. |
| Kiểm tra mã và secret | 13 tests đạt; scripts/check_submission.py kiểm tra syntax Python, liên kết, hash hồ sơ và dấu hiệu credential mà không in secret. Không có .env/PDF/venv/cache/Chroma trong file chuẩn bị đưa lên Git. |
| Nộp link cho giảng viên | Học viên tự nộp theo kênh lớp; agent không gửi tin cho giảng viên và không tự xác định thời hạn. |

## Kiểm tra từ bản clone mới

Theo README: tạo venv Python 3.12, cài requirements.lock.txt, chạy verify_evidence.py, unittest, check_phase4_integrity.py, summarize_manual_audits.py --check-only và check_submission.py. Các lệnh kiểm tra kết quả đã lưu không gọi embedding/retrieval; tokenizer có thể cần mạng ở lần tải đầu.

PDF/cache/index chỉ tồn tại tại máy thực nghiệm, được ignore. Bản clone có manifest/nguồn tải, pages/chunks/trace và kết quả để kiểm tra; không chạy check_phase3_results.py nếu chưa có Chroma gốc. .gitattributes cố định EOL cho mã và trace có hash, giữ nguyên byte của PDF extraction/audit CSV để Git trên Windows không làm sai hồ sơ khóa.

## Phần cần học viên xem xét

- Xem lại nhãn AI, nhất là grounding một phần B/q17, A/q18, B/q19 và lỗi phạm vi q19. GUIDE yêu cầu xem xét nhãn khi dùng LLM judge; chưa có bằng chứng học viên xác minh.
- Kiểm tra quyền truy cập repo của người chấm và nộp link theo hướng dẫn lớp. Không coi việc push GitHub là đã gửi bài qua kênh giảng viên.
