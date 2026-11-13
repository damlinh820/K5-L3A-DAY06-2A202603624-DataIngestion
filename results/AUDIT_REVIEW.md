# Kết quả audit

Phương pháp và hạn chế: [audit_method.json](audit_method.json).

| Cấu hình | Coherence /2 (10 mẫu) | Metadata đúng-đủ | Filter: câu có đủ 3 hit đúng phạm vi | Grounding /2 (5 câu) | Grounding 0 / 1 / 2 |
|---|---:|---:|---:|---:|---|
| A | 1.00 | 15/15 | 0/1 | 1.40 | 1 / 1 / 3 |
| B | 2.00 | 15/15 | 0/1 | 1.60 | 0 / 2 / 3 |
| C | 2.00 | 15/15 | 0/1 | 1.60 | 1 / 0 / 4 |

Metadata đúng nguồn khác với bằng chứng đủ để trả lời. Q19 có yêu cầu phần 3: A/B trả cả ba hit ở phần 2; C chỉ có hit thứ ba đúng phạm vi. B+filter là thí nghiệm riêng, không thay điểm của A/B/C chính.

Các nhãn được xem sau khi đã có điểm retrieval, cùng assistant viết pipeline và chấm nên có nguy cơ thiên lệch. Không thay đổi lựa chọn C đã khóa trước test.

## Coherence — 30 mẫu

- **A / position_01 / Điều 1 — 1/2:** Giữ trọn Điều 1–2 nhưng kết thúc giữa từ ở khoản 1 Điều 3 ("Bản đồ đ"); chunk chỉ mạch lạc một phần.
- **B / position_01 / Điều 1 — 2/2:** Trọn Điều 1: có tiêu đề và câu xác định phạm vi điều chỉnh, không đứt ý.
- **C / position_01 / Điều 1 — 2/2:** Trọn Điều 1: có tiêu đề và câu xác định phạm vi điều chỉnh, không đứt ý.
- **A / position_02 / Điều 30 — 1/2:** Có đủ tiêu đề và khoản 1 Điều 30; đầu còn đuôi Điều trước, cuối cắt khoản 2 tại "khấu trừ vào tiền".
- **B / position_02 / Điều 30 — 2/2:** Trọn Điều 30 với ba khoản lựa chọn hình thức trả tiền thuê đất; các chủ thể, điều kiện và hệ quả được giữ nguyên.
- **C / position_02 / Điều 30 — 2/2:** Có tiêu đề Điều 30 và trọn khoản 1: đủ chủ thể, điều kiện chuyển hình thức thuê, thời điểm xác định giá và phần thời gian còn lại.
- **A / position_03 / Điều 59 — 1/2:** Điều 59 khoản 1–5 đọc được; đầu là đuôi Điều 58, khoản 6 bị cắt ở "hằng", thiếu phần thời hạn công bố.
- **B / position_03 / Điều 59 — 2/2:** Trọn Điều 59, đủ chín khoản trách nhiệm, thời hạn công bố/báo cáo và kinh phí; không cắt giữa câu.
- **C / position_03 / Điều 59 — 2/2:** Có tiêu đề Điều 59 và trọn khoản 1 xác định trách nhiệm tổ chức/phê duyệt của UBND các cấp; tự hiểu được đơn vị trách nhiệm này.
- **A / position_04 / Điều 88 — 1/2:** Giữ khoản 1 Điều 88 nhưng lẫn đuôi Điều trước; điểm a khoản 2 bị cắt giữa tên cơ quan, thiếu điều kiện hoàn chỉnh.
- **B / position_04 / Điều 88 — 2/2:** Trọn Điều 88, đủ nguyên tắc, điều kiện, thẩm quyền, trình tự cưỡng chế và trách nhiệm; các điểm liên kết đúng khoản.
- **C / position_04 / Điều 88 — 2/2:** Có tiêu đề Điều 88 và trọn khoản 1, gồm đủ điểm a–b về nguyên tắc và giờ bắt đầu cưỡng chế; không cắt danh mục.
- **A / position_05 / Điều 117 — 1/2:** Nội dung Điều 117 còn hiểu được nhưng mất đầu tiêu đề; sang Điều 118 và cắt giữa cụm "đất cơ s".
- **B / position_05 / Điều 117 — 2/2:** Trọn Điều 117, giữ quy tắc và ngoại lệ chuyển nhượng dự án; tiêu đề dính thân câu do reflow nhưng vẫn rõ nghĩa.
- **C / position_05 / Điều 117 — 2/2:** Trọn Điều 117, giữ quy tắc và ngoại lệ chuyển nhượng dự án; tiêu đề dính thân câu do reflow nhưng vẫn rõ nghĩa.
- **A / position_06 / Điều 146 — 1/2:** Tiêu đề và khoản 1 Điều 146 đầy đủ; đầu còn đuôi Điều trước, khoản 2 bị cắt giữa từ "hoặ", thiếu phạm vi cấm cấp giấy.
- **B / position_06 / Điều 146 — 2/2:** Trọn Điều 146 với ba khoản điều kiện cấp giấy/tách thửa; giữ các dẫn chiếu Điều 220, không cắt giữa câu.
- **C / position_06 / Điều 146 — 2/2:** Có tiêu đề Điều 146 và trọn khoản 1, giữ điều kiện thời điểm hình thành, diện tích và điều kiện được cấp giấy.
- **A / position_07 / Điều 175 — 1/2:** Điều 175 khoản 1 có đủ sáu điều kiện; đầu lẫn Điều 174 và khoản 2 bị cắt ở "quy định t", mất dẫn chiếu thời hạn.
- **B / position_07 / Điều 175 — 2/2:** Trọn Điều 175, đủ sáu điều kiện và khoản giới hạn thời hạn có dẫn chiếu; cần đọc Điều 172 nếu muốn biết con số cụ thể.
- **C / position_07 / Điều 175 — 2/2:** Trọn Điều 175, đủ sáu điều kiện và khoản giới hạn thời hạn có dẫn chiếu; cần đọc Điều 172 nếu muốn biết con số cụ thể.
- **A / position_08 / Điều 204 — 1/2:** Điều 204 khoản 1–2 có ý hoàn chỉnh; đầu là đuôi Điều trước, cuối chỉ còn "3. Người", thiếu chủ thể và nội dung khoản 3.
- **B / position_08 / Điều 204 — 2/2:** Trọn Điều 204 với sáu khoản về khu công nghệ cao, thời hạn và quyền/nghĩa vụ; không đứt danh mục.
- **C / position_08 / Điều 204 — 2/2:** Có tiêu đề Điều 204 và trọn khoản 1, giữ định nghĩa, yêu cầu quy hoạch và công trình phục vụ người lao động.
- **A / position_09 / Điều 233 — 1/2:** Có tiêu đề và phần dẫn khoản 1 Điều 233; đầu là đuôi Điều 232, điểm a bị cắt ở "sử d", danh mục thông tin chưa đủ.
- **B / position_09 / Điều 233 — 2/2:** Trọn Điều 233, đủ danh mục thông tin, trách nhiệm cập nhật và công khai; không cắt giữa ý.
- **C / position_09 / Điều 233 — 2/2:** Có tiêu đề Điều 233 và trọn khoản 1 với đủ điểm a–đ; chỉ là đơn vị danh mục thông tin, không phải toàn bộ trách nhiệm của Điều.
- **A / position_10 / Điều 260 — 1/2:** Có tiêu đề Điều 260 nhưng khoản 1 bị cắt tại "quyền và nghĩa vụ qu", mất dẫn chiếu cho hộ gia đình/cá nhân; đầu còn Điều 259.
- **B / position_10 / Điều 260 — 2/2:** Giữ đủ 16 khoản chuyển tiếp Điều 260; dài và có lời thông qua/chữ ký cuối văn bản nhưng các trường hợp pháp lý không bị cắt.
- **C / position_10 / Điều 260 — 2/2:** Có tiêu đề Điều 260 và trọn khoản 1; giữ mốc 01/7/2004, ít nhất 05 năm còn lại và dẫn chiếu quyền/nghĩa vụ riêng cho từng chủ thể.

## Grounding — 15 đánh giá

### A / q16 — 2/2

Đất ở thuộc nhóm sử dụng ổn định lâu dài hay nhóm sử dụng có thời hạn trong bản luật được cung cấp?

Rank 1 có tiêu đề Điều 171 và khoản 1 "Đất ở", đủ xác định ổn định lâu dài; nguồn phần 3 trang 1.

### A / q17 — 2/2

Cá nhân trực tiếp sản xuất nông nghiệp được giao hoặc công nhận đất trồng cây hằng năm trong hạn mức Điều 176 có thời hạn bao lâu; khi hết hạn có phải làm thủ tục gia hạn không?

Rank 3 chứa trọn điểm a khoản 1 Điều 172: đúng cá nhân trực tiếp sản xuất, loại đất và hạn mức, 50 năm và tiếp tục không làm thủ tục gia hạn; phần 3 trang 2.

### A / q18 — 1/2

Cá nhân chuyển đất trồng cây hằng năm sang đất rừng đặc dụng thì thời hạn sử dụng được xác định như thế nào?

Rank 1 chỉ giữ đuôi điểm b "ụng, đất rừng phòng hộ ... ổn định lâu dài", mất điều kiện chuyển TỪ đất trồng cây hằng năm SANG rừng đặc dụng; hai hit còn lại nói hạn mức. Có mảnh kết luận nhưng thiếu tiền đề.

### A / q19 — 0/2

Chỉ tra cứu phần 3 của bộ PDF: khi tách hoặc hợp thửa, khoản 1 Điều 220 yêu cầu thửa đất đã có những loại Giấy chứng nhận nào?

Cả ba hit ở phần 2, sai phạm vi phần 3; nói cấp giấy nhiều xã, thu hồi/cấp đổi giấy và giấy tờ lịch sử, không có điều kiện tại Điều 220 khoản 1 điểm a.

### A / q20 — 2/2

Thủ tục hòa giải tranh chấp đất đai tại Ủy ban nhân dân cấp xã có thời hạn tối đa bao lâu và tính từ mốc nào?

Rank 2 giữ trọn điểm c khoản 2 Điều 235: không quá 30 ngày kể từ ngày nhận đơn yêu cầu hòa giải, phần 3 trang 46; rank 1 bị cắt chưa đủ nhưng top-3 đủ.

### B / q16 — 2/2

Đất ở thuộc nhóm sử dụng ổn định lâu dài hay nhóm sử dụng có thời hạn trong bản luật được cung cấp?

Rank 1 giữ trọn Điều 171, khoản 1 nêu Đất ở dưới tiêu đề Đất sử dụng ổn định lâu dài; phần 3 trang 1.

### B / q17 — 1/2

Cá nhân trực tiếp sản xuất nông nghiệp được giao hoặc công nhận đất trồng cây hằng năm trong hạn mức Điều 176 có thời hạn bao lâu; khi hết hạn có phải làm thủ tục gia hạn không?

Rank 3 Điều 174 nói tiếp tục sử dụng không làm thủ tục gia hạn nhưng cho trường hợp NHẬN CHUYỂN QUYỀN, khác giao/công nhận đang hỏi; chỉ dẫn Điều 172, không có 50 năm. Không đủ để trả lời trọn câu.

### B / q18 — 2/2

Cá nhân chuyển đất trồng cây hằng năm sang đất rừng đặc dụng thì thời hạn sử dụng được xác định như thế nào?

Rank 1 Điều 173 khoản 1 điểm b giữ đủ loại đất trước/sau chuyển mục đích và kết luận ổn định lâu dài; phần 3 trang 3.

### B / q19 — 1/2

Chỉ tra cứu phần 3 của bộ PDF: khi tách hoặc hợp thửa, khoản 1 Điều 220 yêu cầu thửa đất đã có những loại Giấy chứng nhận nào?

Rank 1 Điều 146 khoản 3 có cùng bốn loại giấy và dẫn Điều 220, nhưng ở phần 2, cho trường hợp cấp lại sau tách/hợp; thiếu chính điều kiện Điều 220 trong phần 3 được yêu cầu. Không đủ grounding theo phạm vi câu hỏi.

### B / q20 — 2/2

Thủ tục hòa giải tranh chấp đất đai tại Ủy ban nhân dân cấp xã có thời hạn tối đa bao lâu và tính từ mốc nào?

Rank 1 có trọn Điều 235; điểm c khoản 2 nêu đủ 30 ngày và mốc nhận đơn, phần 3 trang 46. Không nhầm 30 ngày trưng dụng ở rank 2.

### C / q16 — 2/2

Đất ở thuộc nhóm sử dụng ổn định lâu dài hay nhóm sử dụng có thời hạn trong bản luật được cung cấp?

Rank 3 có Điều 171 khoản 1, đủ kết luận đất ở sử dụng ổn định lâu dài, phần 3 trang 1; hai rank đầu không trả lời câu hỏi.

### C / q17 — 0/2

Cá nhân trực tiếp sản xuất nông nghiệp được giao hoặc công nhận đất trồng cây hằng năm trong hạn mức Điều 176 có thời hạn bao lâu; khi hết hạn có phải làm thủ tục gia hạn không?

Cả ba hit là Điều 176 về HẠN MỨC diện tích, không có bằng chứng về thời hạn 50 năm hoặc miễn thủ tục gia hạn của Điều 172.

### C / q18 — 2/2

Cá nhân chuyển đất trồng cây hằng năm sang đất rừng đặc dụng thì thời hạn sử dụng được xác định như thế nào?

Rank 1 giữ tiêu đề Điều 173 và toàn khoản 1, điểm b đủ tiền đề chuyển đất trồng cây hằng năm sang rừng đặc dụng và kết luận ổn định lâu dài; phần 3 trang 3.

### C / q19 — 2/2

Chỉ tra cứu phần 3 của bộ PDF: khi tách hoặc hợp thửa, khoản 1 Điều 220 yêu cầu thửa đất đã có những loại Giấy chứng nhận nào?

Rank 3 đúng Điều 220 khoản 1 điểm a ở phần 3 trang 34, giữ đủ bốn loại giấy chứng nhận. Hai hit đầu sai phạm vi được ghi lỗi filter riêng; không xóa bằng chứng hợp lệ ở rank 3.

### C / q20 — 2/2

Thủ tục hòa giải tranh chấp đất đai tại Ủy ban nhân dân cấp xã có thời hạn tối đa bao lâu và tính từ mốc nào?

Rank 3 giữ Điều 235 khoản 2 điểm c, đủ thời hạn và mốc tính tại phần 3 trang 46; phân biệt với 30 ngày thực hiện quyết định tranh chấp ở rank 1 và 30 ngày làm việc đăng ký sau hòa giải ở rank 2.

## Metadata — 45 bản ghi

 Xem [ai_audit_source_checks.json](ai_audit_source_checks.json).

- **A / q16 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–1; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q16 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–4; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q16 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–2; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q17 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q17 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q17 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–2; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q18 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–3; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q18 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q18 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q19 / rank 1:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 67–67; A không có nhãn Điều, không phải trường bắt buộc; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **A / q19 / rank 2:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 73–74; A không có nhãn Điều, không phải trường bắt buộc; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **A / q19 / rank 3:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 48–49; A không có nhãn Điều, không phải trường bắt buộc; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **A / q20 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 45–46; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q20 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 46–46; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **A / q20 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 47–48; A không có nhãn Điều, không phải trường bắt buộc; không yêu cầu filter: N/A
- **B / q16 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–1; Điều 171; không yêu cầu filter: N/A
- **B / q16 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–3; Điều 172; không yêu cầu filter: N/A
- **B / q16 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–4; Điều 174; không yêu cầu filter: N/A
- **B / q17 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; Điều 176; không yêu cầu filter: N/A
- **B / q17 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 5–5; Điều 177; không yêu cầu filter: N/A
- **B / q17 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–4; Điều 174; không yêu cầu filter: N/A
- **B / q18 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–3; Điều 173; không yêu cầu filter: N/A
- **B / q18 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–4; Điều 174; không yêu cầu filter: N/A
- **B / q18 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–5; Điều 176; không yêu cầu filter: N/A
- **B / q19 / rank 1:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 66–67; Điều 146; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **B / q19 / rank 2:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 67–67; Điều 147; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **B / q19 / rank 3:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 46–47; Điều 136; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **B / q20 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 45–46; Điều 235; không yêu cầu filter: N/A
- **B / q20 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat1.pdf trang thân 91–93; Điều 90; không yêu cầu filter: N/A
- **B / q20 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 46–48; Điều 236; không yêu cầu filter: N/A
- **C / q16 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–3; Điều 172, khoản 5; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q16 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 2–2; Điều 172, khoản 3; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q16 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 1–1; Điều 171; không yêu cầu filter: N/A
- **C / q17 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–4; Điều 176, khoản 2; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q17 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 5–5; Điều 176, khoản 4; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q17 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–4; Điều 176, khoản 1; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q18 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 3–3; Điều 173, khoản 1; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q18 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 4–4; Điều 176, khoản 2; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q18 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 5–5; Điều 176, khoản 4; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q19 / rank 1:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 67–67; Điều 146, khoản 3; tiêu đề lặp có provenance riêng; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **C / q19 / rank 2:** metadata 1; filter 0. Đã đối chiếu text layer PDF và khoảng provenance; luatdat2.pdf trang thân 49–49; Điều 137, khoản 3; tiêu đề lặp có provenance riêng; yêu cầu part=3, toàn bộ nguồn chunk sai phạm vi
- **C / q19 / rank 3:** metadata 1; filter 1. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 34–35; Điều 220, khoản 1; tiêu đề lặp có provenance riêng; yêu cầu part=3, toàn bộ nguồn chunk đúng phạm vi
- **C / q20 / rank 1:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 48–48; Điều 236, khoản 4; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q20 / rank 2:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 46–46; Điều 235, khoản 4; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
- **C / q20 / rank 3:** metadata 1; filter N/A. Đã đối chiếu text layer PDF và khoảng provenance; luatdat3.pdf trang thân 45–46; Điều 235, khoản 2; tiêu đề lặp có provenance riêng; không yêu cầu filter: N/A
