# Trạng thái checkpoint trước khi đưa bài lên Git

Cập nhật 13/11/2026 theo kết quả và xác nhận đã có. `[x]` chỉ có nghĩa dòng đó đã có minh chứng, không đồng nghĩa được giảng viên duyệt. Đây là bản theo dõi trong repo; không sửa AGENT_PLAN.md gốc ở Downloads. Mốc thời gian là checkpoint của đề, không phải thời lượng thực tế đã làm.

## Phase 1 — Dữ liệu và môi trường

- [x] Tạo venv, pin phiên bản, lưu environment.json.
- [x] Gọi embedding thật, xác nhận model/số chiều/usage; không dùng mock.
- [x] Chroma persistent: ghi/đọc/filter và nạp không trùng đạt.
- [x] Trích xuất PDF theo trang, raw/normalized text, log lỗi/trang rỗng.
- [x] Chuẩn hóa giữ cấu trúc pháp lý, offset và provenance.
- [x] Manifest ba phần PDF, 253 trang có text, nguồn/ghi công/hash/quy tắc tính.
- [x] HUMAN GATE 1 — học viên đã xác nhận corpus/cách tính trang; không khẳng định rà từng trang thủ công.

## Phase 2 — Benchmark trước retrieval

- [x] 20 câu, đáp án, nguồn/trang/evidence, gold thay thế và filter tường minh.
- [x] 15 dev/5 test; ba câu filter, trong đó một test; ghi nguy cơ trùng chủ đề trong cùng luật.
- [x] Kiểm tra evidence 20/20, không đưa gold vào query/filter.
- [x] HUMAN GATE 2 — đã xác nhận và khóa câu hỏi/gold/protocol/corpus.
- [x] Commit benchmark `65922c51745807d5b44e2b9d72845130769737e0` trước retrieval.

## Phase 3 — Chunking và ingest

- [x] A 512/64; B nguyên Điều; C tách Khoản khi Điều dài; ghi ngoại lệ kích thước/UTF-8.
- [x] Kiểm thử bảo toàn text, đủ 260 Điều, context/provenance và Khoản gốc so với trích dẫn.
- [x] Batch embedding thật, retry giới hạn; lỗi dừng, không fallback vector giả.
- [x] Ba collection, IDs ổn định, upsert lần hai không nhân đôi; mở DB bằng process riêng kiểm tra.
- [x] Có chunk_stats, ingest logs, usage/chi phí và experiment_log.
- [x] HUMAN GATE 3 — đã xác nhận mẫu chunk và khóa snapshot trước retrieval.

## Phase 4 — Retrieval và audit

- [x] Top-3 cosine, filter metadata, trace A/B/C đầy đủ.
- [x] Hit@1/Hit@3 có tử/mẫu, tách dev/test; B với B+filter đo trên cùng câu.
- [x] Chọn C bằng dev trước test, giữ hash mã/index/gold; không tune theo test.
- [x] Tạo audit trống đúng mẫu trước khi chấm, giữ bản gốc ở results/audit_before_ai/.
- [x] Codex chấm theo yêu cầu bổ sung: 30 coherence/45 metadata/15 grounding, có lý do và nhãn nguồn AI.
- [x] Công khai phương pháp/thiên lệch/chưa xác minh; kiểm tra text layer 22 trang nguồn.
- [x] Gate 4 — hoàn thành bảng chấm bằng AI theo yêu cầu bổ sung của học viên. Nguồn nhãn vẫn là AI; chưa ghi nhận cụ thể các dòng đã được học viên xác minh, không coi là chấm thủ công độc lập.

Đọc results/AUDIT_REVIEW.md và mục “Ghi chú cho học viên trước khi đưa lên Git” trong báo cáo. Chú ý B/q17, A/q18, B/q19 và lỗi phạm vi q19; không nhầm metadata đúng nguồn với bằng chứng đủ hoặc đúng phạm vi.

## Phase 5 — Báo cáo và nộp

- [x] Báo cáo: cấu hình, dev/test, audit AI công khai, tài nguyên, ≥2 ví dụ lỗi và phân tích năm khía cạnh.
- [x] Thông tin học viên/repo đã điền; khai báo AI và cách kiểm tra.
- [x] README có setup/kiểm tra/nguồn PDF; phân biệt pipeline luật với starter Đà Lạt cũ.
- [x] 13 tests đạt; kiểm tra gold/index/trace và audit hợp lệ.
- [x] Rà file chuẩn bị đưa lên Git, không có .env/key/PDF/venv/cache/index; có submission_check.json.
- [ ] Chốt commit mã/kết quả cuối; điền mã vào STUDENT.md và báo cáo. Đang thực hiện theo yêu cầu chốt repo của học viên.
- [ ] Push GitHub và kiểm tra commit/file từ xa; chỉ đánh dấu sau khi lệnh thành công.
- [x] Học viên đã tự đánh dấu mục kiểm tra quyền truy cập/nộp link trong checklist. Agent không trực tiếp xác minh kênh nộp lớp; push không đồng nghĩa đã nộp bài.

## Những giới hạn không tự coi là việc kỹ thuật còn thiếu

Không cần chạy lại benchmark để tăng điểm, sửa test sau khi xem kết quả, xây chatbot hoặc OCR corpus đã có text. Chưa rà thủ công cả 253 trang, chưa đối chiếu hash bản tải mới từ cổng, test chỉ năm câu và chưa xác minh pháp luật hợp nhất hiện hành là các giới hạn đã khai báo; không tự biến chúng thành yêu cầu bắt buộc bổ sung của bài.
