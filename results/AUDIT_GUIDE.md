# Gate 4 — đọc và xem xét ba bảng audit

Retrieval đã chạy trên bộ câu hỏi đã khóa. C được chọn trên dev trước test. Sau đó học viên yêu cầu “vậy bạn chấm giúp mình”: Codex đã đọc và chấm đủ ba bảng, ghi rõ `label_origin=ai_assisted`, `reviewer=Codex`, `human_verified=false`. Đây không phải nhãn thủ công độc lập và chưa được học viên xác minh. Đọc bản dễ xem tại [AUDIT_REVIEW.md](AUDIT_REVIEW.md); phương pháp và hạn chế ở [audit_method.json](audit_method.json). Bảng trống ban đầu được giữ trong `audit_before_ai/`.

Rubric bên dưới dùng cho điểm AI hiện tại và để học viên xem xét lại. AI chấm sau khi biết điểm retrieval, cùng assistant đã viết pipeline; vì vậy có nguy cơ thiên lệch. Metadata có hỗ trợ kiểm tra lại text layer 22 trang nguồn, không phải kiểm tra bố cục PDF bằng mắt.

## 1. Coherence — audit_coherence.csv (30 dòng)

Mỗi cấu hình A/B/C có cùng 10 vị trí nguồn được chọn trước retrieval. Đọc `text`, đối chiếu vị trí nguồn rồi điền:

- `score_0_1_2`: 0 = cắt giữa ý/thiếu chủ thể làm không hiểu; 1 = hiểu một phần nhưng thiếu ngữ cảnh; 2 = tự hiểu được và giữ trọn ý.
- `reason`: lý do ngắn của người chấm cho từng dòng.

## 2. Metadata — audit_metadata.csv (45 dòng)

5 câu test × top-3 × 3 cấu hình. Đối chiếu `source_url`, trang PDF, `provenance_json`, `metadata_json` với tài liệu gốc. Trang chính là trang bắt đầu thân chunk; tiêu đề lặp ở C có provenance riêng. Một chunk có thể đi qua nhiều trang; đừng coi mọi trang trong khoảng số đều thuộc cùng một file nếu provenance có nhiều source.

- `metadata_complete_correct_0_1`: 1 nếu metadata bắt buộc đúng và đủ để truy vết/lọc, 0 nếu thiếu/sai. Các trường bắt buộc là source/document ID, trang hoặc provenance tương đương và trường cần cho filter (`part`). Không tự động đánh trượt A vì không có nhãn Điều/Khoản tùy chọn.
- `filter_compliant_0_1_or_NA`: nếu `requested_filter` là `{}` thì điền `N/A`. Nếu câu hỏi yêu cầu `part`, điền 1/0 theo chunk có nằm đúng phần đó hay không. A/B/C chính chạy không filter; cột `applied_filter` để người chấm phân biệt với yêu cầu đầu vào. Thí nghiệm B+filter được báo riêng trong filter_comparison.json.
- `reason`: nêu lỗi khi chấm metadata 0; có thể ghi ngắn khi chấm 1.

Tỷ lệ query tuân thủ filter sẽ chỉ tính một câu đạt nếu cả ba hit của câu đó đều tuân thủ; không coi tập không có filter là 100%.

## 3. Grounding — audit_grounding.csv (15 dòng)

5 câu test × 3 cấu hình. Đọc câu hỏi và toàn bộ `top3_json`, dùng `expected_answer`/`gold_evidence_json` để kiểm tra điều kiện và nguồn. Điền:

- `score_0_1_2`: 0 = không có bằng chứng; 1 = có nhưng thiếu điều kiện/ngữ cảnh; 2 = đủ bằng chứng để trả lời và truy nguồn.
- `reason`: lý do ngắn cho từng dòng.

Đây là độ đủ bằng chứng truy xuất, không phải độ chính xác câu trả lời do LLM sinh. Không suy điểm grounding trực tiếp từ Hit@3. Đáp án và gold là tham chiếu; người chấm vẫn phải kiểm tra nguồn.

## Kiểm tra sau khi điền

Giữ các cột source/text/ID, chỉ sửa các ô nhãn và reason. Lưu CSV phân tách bằng dấu phẩy, UTF-8. Không dùng Excel để đổi kiểu các cột JSON/ID.

Chạy từ thư mục gốc:

```powershell
.\.venv-legal\Scripts\python.exe scripts/summarize_manual_audits.py --check-only
.\.venv-legal\Scripts\python.exe scripts/summarize_manual_audits.py
```

Lệnh thứ hai tạo `audit_summary.json` và bản đọc `AUDIT_REVIEW.md` khi đủ nhãn hợp lệ; luôn giữ nguồn gốc người/AI trong kết quả. Các bảng hiện là nhãn AI, không phải kết quả chấm tay của học viên. Nếu muốn sửa/xác minh nhãn, lưu riêng phiên bản do người kiểm tra và ghi rõ người sửa, ngày, lý do và các dòng đã xem; không chỉ đổi cờ thành nhãn người cho cả bảng. Cần ghi hạn chế mẫu 5 câu test.
