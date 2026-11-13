# Gate 3 — chunk mẫu
Đây là mẫu chunk trước retrieval. Chưa có điểm Hit@1/Hit@3 hoặc nhãn audit.

A: cửa sổ 512 token/overlap 64; biên token được điều chỉnh nhẹ để không cắt ký tự UTF-8.
B: mỗi Điều nguyên vẹn, giữ cả phần mở đầu/Chương/Mục thành đơn vị riêng.
C: Điều dài hơn 512 token được tách Khoản và lặp lại tiêu đề Điều. Khoản dài vẫn được giữ trọn nên chunk C có thể vượt 512 token; không bị cắt cụt.

Cần xem: có giữ đúng Điều/Khoản không; nội dung có bị mất hay lẫn Chương khác không; source/page và phần nối qua trang có truy vết đúng không.

Các đoạn mẫu dưới đây được chọn theo Điều 3, 91, 172 để phủ ba phần PDF, không dựa trên điểm retrieval. Mười vị trí coherence được định trước trong audit_positions.json; bảng audit_coherence.csv có 30 dòng nhãn trống để chấm sau.

## Điều 3 — cấu hình A

Chunk `e2a4d87f5558e64afb66e4a74d53adf2`; 512 token; Điều `None`; Khoản `None`; Chương `None`.

Nguồn/trang: `luatdat1.pdf:1`, `luatdat1.pdf:2`

```text
ệc quản lý, sử dụng đất đai.
Điều 3. Giải thích từ ngữ
Trong Luật này, các từ ngữ dưới đây được hiểu như sau:
1. Bản đồ địa chính là bản đồ thể hiện các thửa đất và các đối tượng địa lý có liên quan, lập theo đơn vị hành chính cấp xã hoặc theo đơn vị hành chính cấp huyện nơi không thành lập đơn vị hành chính cấp xã, được cơ quan nhà nước có thẩm quyền xác nhận.
2. Bản đồ hiện trạng sử dụng đất là bản đồ thể hiện sự phân bố các loại đất tại một thời điểm xác định, được lập theo từng đơn vị hành chính các cấp, theo từng vùng kinh tế - xã hội.
3. Bản đồ quy hoạch sử dụng đất là bản đồ được lập tại thời điểm đầu kỳ quy hoạch, thể hiện nội dung phân bố các loại đất tại thời điểm cuối kỳ quy hoạch của quy hoạch đó.
4. Bảo vệ, cải tạo, phục hồi đất là việc áp dụng các biện pháp quản lý, kỹ thuật, cơ giới, sinh học, hữu cơ tác động vào đất để xử lý đất bị ô nhiễm, phục hồi đất bị thoái hóa.
5. Bồi thường về đất là việc Nhà nước trả lại giá trị quyền sử dụng đất của diện tích đất thu hồi cho người có đ
```


## Điều 3 — cấu hình B

Chunk `9fc798bd11f09b15ad26d9ede53ad6fd`; 5331 token; Điều `3`; Khoản `None`; Chương `I`.

Nguồn/trang: `luatdat1.pdf:1`, `luatdat1.pdf:2`, `luatdat1.pdf:3`, `luatdat1.pdf:4`, `luatdat1.pdf:5`, `luatdat1.pdf:6`, `luatdat1.pdf:7`

```text
Điều 3. Giải thích từ ngữ
Trong Luật này, các từ ngữ dưới đây được hiểu như sau:
1. Bản đồ địa chính là bản đồ thể hiện các thửa đất và các đối tượng địa lý có liên quan, lập theo đơn vị hành chính cấp xã hoặc theo đơn vị hành chính cấp huyện nơi không thành lập đơn vị hành chính cấp xã, được cơ quan nhà nước có thẩm quyền xác nhận.
2. Bản đồ hiện trạng sử dụng đất là bản đồ thể hiện sự phân bố các loại đất tại một thời điểm xác định, được lập theo từng đơn vị hành chính các cấp, theo từng vùng kinh tế - xã hội.
3. Bản đồ quy hoạch sử dụng đất là bản đồ được lập tại thời điểm đầu kỳ quy hoạch, thể hiện nội dung phân bố các loại đất tại thời điểm cuối kỳ quy hoạch của quy hoạch đó.
4. Bảo vệ, cải tạo, phục hồi đất là việc áp dụng các biện pháp quản lý, kỹ thuật, cơ giới, sinh học, hữu cơ tác động vào đất để xử lý đất bị ô nhiễm, phục hồi đất bị thoái hóa.
5. Bồi thường về đất là việc Nhà nước trả lại giá trị quyền sử dụng đất của diện tích đất thu hồi cho người có đất thu hồi.
6. Cá nhân trực tiếp sản xuất nông nghiệp là cá nhân đã được Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất nông nghiệp; nhận chuyển quyền sử dụng đất nông nghiệp mà có thu nhập từ sản xuất nông nghiệp trên đất đó theo quy định của Chính phủ.
7. Chi phí đầu tư vào đất còn lại là chi phí hợp lý mà người sử dụng đất đã đầu tư trực tiếp vào đất phù hợp với mục đích sử dụng đất nhưng đến thời điểm Nhà nước thu hồi đất còn chưa thu hồi hết.
8. Chỉ tiêu sử dụng đất là diện tích đất của từng loại đất được xác định trong quy hoạch, kế hoạch sử dụng đất các cấp do cơ quan nhà nước có thẩm quyền xác định để phân bổ trong quá trình lập quy hoạch, kế hoạch sử dụng đất.
9. Chiếm đất là việc sử dụng đất do Nhà nước đã quản lý mà chưa được cơ quan nhà nước có thẩm quyền cho phép hoặc sử dụng đất của người sử dụng đất hợp pháp khác mà chưa được người đó cho phép.
10. Chủ đầu tư dự án đầu tư có sử dụng đất (sau đây gọi là chủ đầu tư) là nhà đầu tư theo quy định của pháp luật về đầu tư, pháp luật có liên quan đã được lựa chọn để thực hiện dự án đầu tư có sử dụng đất và được giao đất, cho thuê đất, chuyển mục đích sử dụng đất theo quy định của Luật này.
11. Chuyển mục đích sử dụng đất là việc người sử dụng đất được thay đổi từ mục đích sử dụng đất này sang mục đích sử dụng đất khác theo quy định của Luật này.
12. Chuyển quyền sử dụng đất là việc chuyển giao quyền sử dụng đất từ người này sang người khác thông qua hình thức chuyển đổi, chuyển nhượng, thừa kế, tặng cho quyền sử dụng đất, góp vốn bằng quyền sử dụng đất.
13. Cộng đồng dân cư là cộng đồng người Việt Nam sinh sống trên cùng địa bàn thôn, làng, ấp, bản, bon, buôn, phum, sóc, tổ dân phố và điểm dân cư tương tự có cùng phong tục, tập quán hoặc có chung dòng họ trên lãnh thổ nước Cộng hòa xã hội chủ nghĩa Việt Nam.
14. Cơ sở dữ liệu quốc gia về đất đai là tập hợp các cơ sở dữ liệu đất đai trong đó dữ liệu được sắp xếp, tổ chức để truy cập, khai thác, chia sẻ, quản lý và cập nhật thông qua phương tiện điện tử.
15. Đăng ký đất đai, tài sản gắn liền với đất là việc người sử dụng đất, người sở hữu tài sản gắn liền với đất, người được giao quản lý đất kê khai quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất với cơ quan nhà nước có thẩm quyền để được ghi nhận theo quy định của Luật này.
16. Đất đang có tranh chấp là thửa đất có tranh chấp đất đai mà đang trong quá trình được cơ quan có thẩm quyền giải quyết.
17. Điều chỉnh thời hạn sử dụng đất là việc cơ quan nhà nước có thẩm quyền cho phép thay đổi thời hạn sử dụng đất trong quá trình sử dụng đất.
18. Gia hạn sử dụng đất là việc cơ quan nhà nước có thẩm quyền cho phép tiếp tục sử dụng đất khi hết thời hạn theo mục đích đang sử dụng theo quy định của Luật này.
19. Giá đất là giá trị của quyền sử dụng đất tính bằng tiền trên một đơn vị diện tích đất.
20. Giá trị quyền sử dụng đất là giá trị bằng tiền của quyền sử dụng đất đối với một diện tích đất, loại đất tại thời điểm được xác định với thời hạn sử dụng đã được xác định.
21. Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất là chứng thư pháp lý để Nhà nước xác nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất hợp pháp của người có quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất. Tài sản gắn liền với đất được cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất là nhà ở, công trình xây dựng gắn liền với đất theo quy định của pháp luật. Giấy chứng nhận về quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất theo quy định của các luật có
liên quan được thực hiện theo quy định của Luật này có giá trị pháp lý tương đương như Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất tại Luật này.
22. Góp vốn bằng quyền sử dụng đất là sự thỏa thuận giữa các bên về chuyển quyền sử dụng đất thông qua việc góp quyền sử dụng đất để tạo thành vốn điều lệ của tổ chức kinh tế, bao gồm góp vốn để thành lập tổ chức kinh tế hoặc góp thêm vốn điều lệ của tổ chức kinh tế đã được thành lập.
23. Hệ thống thông tin quốc gia về đất đai là hệ thống tổng hợp các yếu tố hạ tầng kỹ thuật công nghệ thông tin, phần mềm, dữ liệu được xây dựng thành một hệ thống tập trung, thống nhất trên phạm vi cả nước để quản lý, vận hành, cập nhật, khai thác thông tin đất đai.
24. Hỗ trợ khi Nhà nước thu hồi đất là chính sách của Nhà nước nhằm trợ giúp cho người có đất thu hồi, chủ sở hữu tài sản gắn liền với đất để ổn định đời sống, sản xuất và phát triển ngoài các khoản đã bồi thường theo quy định của Luật này.
25. Hộ gia đình sử dụng đất là những người có quan hệ hôn nhân, huyết thống, nuôi dưỡng theo quy định của pháp luật về hôn nhân và gia đình, đang sống chung và có quyền sử dụng đất chung tại thời điểm được Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất, nhận chuyển quyền sử dụng đất trước ngày Luật này có hiệu lực thi hành.
26. Hợp tác sản xuất, kinh doanh bằng quyền sử dụng đất là sự thỏa thuận giữa các bên, theo đó người sử dụng đất dùng quyền sử dụng đất của mình để hợp tác sản xuất, kinh doanh mà không làm thay đổi quyền sử dụng đất của người sử dụng đất.
27. Hủy hoại đất là hành vi làm biến dạng địa hình, làm suy giảm chất lượng đất, gây ô nhiễm đất mà làm mất hoặc giảm khả năng sử dụng đất theo mục đích đã được xác định.
28. Kế hoạch sử dụng đất là việc phân kỳ quy hoạch sử dụng đất theo thời gian để thực hiện.
29. Kiểm kê đất đai là việc Nhà nước tổ chức điều tra, tổng hợp, đánh giá trên hồ sơ địa chính và trên thực địa về hiện trạng sử dụng đất tại thời điểm kiểm kê và biến động đất đai giữa 02 lần kiểm kê.
30. Lấn biển là việc mở rộng diện tích đất trong phạm vi từ đường mép nước biển thấp nhất trung bình trong nhiều năm về phía biển thuộc vùng biển Việt Nam.
31. Lấn đất là việc người sử dụng đất chuyển dịch mốc giới hoặc ranh giới thửa đất để mở rộng diện tích đất sử dụng mà không được cơ quan nhà nước có thẩm quyền cho phép hoặc không được người sử dụng hợp pháp diện tích đất bị lấn đó cho phép.
32. Nhà nước cho thuê quyền sử dụng đất (sau đây gọi là Nhà nước cho thuê đất) là việc cơ quan nhà nước có thẩm quyền ban hành quyết định cho thuê đất cho đối tượng có nhu cầu sử dụng đất.
33. Nhà nước công nhận quyền sử dụng đất là việc cơ quan nhà nước có thẩm quyền cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất lần đầu cho người đang sử dụng đất ổn định đối với thửa đất xác định theo quy định của Luật này.
34. Nhà nước giao quyền sử dụng đất (sau đây gọi là Nhà nước giao đất) là việc cơ quan nhà nước có thẩm quyền ban hành quyết định giao đất cho đối tượng có nhu cầu sử dụng đất.
35. Nhà nước thu hồi đất là việc cơ quan nhà nước có thẩm quyền ban hành quyết định thu lại quyền sử dụng đất của người sử dụng đất hoặc thu lại đất của người đang sử dụng đất hoặc thu lại đất đang được Nhà nước giao quản lý.
36. Quy hoạch sử dụng đất là việc phân bổ chỉ tiêu sử dụng đất và khoanh vùng đất đai cho các mục đích phát triển kinh tế - xã hội, quốc phòng, an ninh, bảo vệ môi trường và thích ứng với biến đổi khí hậu trên cơ sở tiềm năng đất đai và nhu cầu sử dụng đất của các ngành, lĩnh vực đối với từng đơn vị hành chính cho thời kỳ xác định.
37. Quyền thuê trong hợp đồng thuê đất là quyền của người sử dụng đất được hình thành khi Nhà nước cho thuê đất thu tiền thuê đất hằng năm. Người sử dụng đất được chuyển nhượng quyền thuê trong hợp đồng thuê đất; người nhận chuyển nhượng quyền thuê trong hợp đồng thuê đất được kế thừa các quyền và nghĩa vụ của người sử dụng đất theo quy định của Luật này và quy định khác của pháp luật có liên quan.
38. Sử dụng đất ổn định là việc sử dụng đất vào một mục đích chính nhất định kể từ thời điểm bắt đầu sử dụng đất vào mục đích đó đến thời điểm cơ quan nhà nước có thẩm quyền xem xét việc sử dụng đất ổn định.
39. Tái định cư là việc Nhà nước thực hiện bồi thường bằng đất ở hoặc bằng nhà ở tại khu tái định cư hoặc địa điểm khác phù hợp cho người có đất thu hồi hoặc hỗ trợ bằng giao đất ở, nhà ở tái định cư cho người không đủ điều kiện bồi thường về đất ở theo quy định của Luật này nhưng không còn chỗ ở nào khác.
40. Thoái hóa đất là tình trạng đất bị thay đổi đặc tính, tính chất vốn có ban đầu theo chiều hướng xấu do tác động của điều kiện tự nhiên, con người.
41. Thống kê đất đai là việc Nhà nước tổng hợp, đánh giá trên hồ sơ địa chính về hiện trạng sử dụng đất tại thời điểm thống kê và biến động đất đai giữa 02 lần thống kê.
42. Thửa đất là phần diện tích đất được giới hạn bởi ranh giới mô tả trên hồ sơ địa chính hoặc được xác định trên thực địa.
43. Thửa đất chuẩn là thửa đất có các đặc tính về diện tích, hình thể, kích thước mang tính đại diện cho các thửa đất trong vùng giá trị, được chọn làm thửa đất chuẩn để định giá cho các thửa đất khác trong vùng giá trị.
44. Tiền sử dụng đất là số tiền mà người sử dụng đất phải trả cho Nhà nước khi được Nhà nước giao đất có thu tiền sử dụng đất, cho phép chuyển mục đích sử dụng đất hoặc các trường hợp sử dụng đất mà phải nộp tiền sử dụng đất theo quy định của pháp luật.
45. Tiền thuê đất là số tiền mà người sử dụng đất phải trả cho Nhà nước khi được Nhà nước cho thuê đất, cho phép chuyển mục đích sử dụng đất để cho thuê đất hoặc các trường hợp sử dụng đất mà phải nộp tiền thuê đất theo quy định của pháp luật.
46. Tổ chức kinh tế có vốn đầu tư nước ngoài là tổ chức kinh tế phải đáp ứng điều kiện và thực hiện thủ tục đầu tư quy định đối với nhà đầu tư nước ngoài theo quy định của Luật Đầu tư để thực hiện dự án có sử dụng đất.
47. Tranh chấp đất đai là tranh chấp về quyền, nghĩa vụ của người sử dụng đất giữa hai hoặc nhiều bên trong quan hệ đất đai.
48. Vùng giá trị là khu vực các thửa đất liền kề nhau, có cùng mục đích sử dụng và có các yếu tố tương đồng về vị trí, khả năng sinh lợi, điều kiện kết cấu hạ tầng và yếu tố khác ảnh hưởng đến giá đất.
49. Vùng phụ cận là vùng đất tiếp giáp với các điểm kết nối giao thông và các tuyến giao thông có tiềm năng phát triển theo quy hoạch.
```

## Điều 3 — cấu hình C

Chunk `b1d6c1eac664db0f5a23bcb8b2a48412`; 140 token; Điều `3`; Khoản `1`; Chương `I`.

Nguồn/trang: `luatdat1.pdf:1`

```text
Điều 3. Giải thích từ ngữ
1. Bản đồ địa chính là bản đồ thể hiện các thửa đất và các đối tượng địa lý có liên quan, lập theo đơn vị hành chính cấp xã hoặc theo đơn vị hành chính cấp huyện nơi không thành lập đơn vị hành chính cấp xã, được cơ quan nhà nước có thẩm quyền xác nhận.
```

## Điều 91 — cấu hình A

Chunk `1bdf85f80f1b0ec8ab8820ef761eb00a`; 512 token; Điều `None`; Khoản `None`; Chương `None`.

Nguồn/trang: `luatdat1.pdf:93`, `luatdat2.pdf:1`

```text
 Chính phủ quy định chi tiết Điều này. (Xem tiếp Công báo số 365 + 366)
VĂN BẢN QUY PHẠM PHÁP LUẬT CHỦ TỊCH NƯỚC - QUỐC HỘI Luật số 31/2024/QH15 ngày 18 tháng 01 năm 2024 Luật Đất đai (Tiếp theo Công báo số 363 + 364)
Chương VII
BỒI THƯỜNG, HỖ TRỢ, TÁI ĐỊNH CƯ KHI NHÀ NƯỚC THU HỒI ĐẤT
Mục 1
QUY ĐỊNH CHUNG
Điều 91. Nguyên tắc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất
1. Việc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất phải bảo đảm dân chủ, khách quan, công bằng, công khai, minh bạch, kịp thời và đúng quy định của pháp luật; vì lợi ích chung, sự phát triển bền vững, văn minh và hiện đại của cộng đồng, của địa phương; quan tâm đến đối tượng chính sách xã hội, đối tượng trực tiếp sản xuất nông nghiệp.
2. Việc bồi thường về đất được thực hiện bằng việc giao đất có cùng mục đích sử dụng với loại đất thu hồi, trường hợp không có đất để bồi thường thì được bồi thường bằng tiền theo giá đất cụ thể của loại đ
```

## Điều 91 — cấu hình B

Chunk `34f73b63f599f0665e4d5de44613c3fa`; 1430 token; Điều `91`; Khoản `None`; Chương `VII`.

Nguồn/trang: `luatdat2.pdf:1`, `luatdat2.pdf:2`

```text
Điều 91. Nguyên tắc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất
1. Việc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất phải bảo đảm dân chủ, khách quan, công bằng, công khai, minh bạch, kịp thời và đúng quy định của pháp luật; vì lợi ích chung, sự phát triển bền vững, văn minh và hiện đại của cộng đồng, của địa phương; quan tâm đến đối tượng chính sách xã hội, đối tượng trực tiếp sản xuất nông nghiệp.
2. Việc bồi thường về đất được thực hiện bằng việc giao đất có cùng mục đích sử dụng với loại đất thu hồi, trường hợp không có đất để bồi thường thì được bồi thường bằng tiền theo giá đất cụ thể của loại đất thu hồi do Ủy ban nhân dân cấp có thẩm quyền quyết định tại thời điểm phê duyệt phương án bồi thường, hỗ trợ, tái định cư. Trường hợp người có đất thu hồi được bồi thường bằng đất, bằng nhà ở mà có nhu cầu được bồi thường bằng tiền thì được bồi thường bằng tiền theo nguyện vọng đã đăng ký khi lập phương án bồi thường, hỗ trợ, tái định cư. Đối với người có đất thu hồi nếu có nhu cầu và địa phương có điều kiện về quỹ đất, quỹ nhà ở thì được xem xét bồi thường bằng đất khác mục đích sử dụng với loại đất thu hồi hoặc bằng nhà ở.
3. Chủ sở hữu tài sản theo quy định của pháp luật dân sự mà bị thiệt hại về tài sản thì được bồi thường thiệt hại; chủ cơ sở sản xuất, kinh doanh phải ngừng sản xuất, kinh doanh do Nhà nước thu hồi đất thì được xem xét hỗ trợ.
4. Nhà nước có trách nhiệm hỗ trợ cho người có đất thu hồi, chủ sở hữu tài sản để tạo điều kiện cho người có đất thu hồi, chủ sở hữu tài sản có việc làm, có thu nhập, ổn định đời sống, sản xuất.
5. Khu tái định cư phải hoàn thiện các điều kiện về hạ tầng kỹ thuật, hạ tầng xã hội đồng bộ theo quy hoạch chi tiết được cơ quan có thẩm quyền phê duyệt; đồng thời phải phù hợp với truyền thống văn hóa, phong tục, tập quán của cộng đồng dân cư nơi có đất thu hồi. Khu tái định cư có thể bố trí cho một hoặc nhiều dự án.
6. Ủy ban nhân dân cấp tỉnh, Ủy ban nhân dân cấp huyện có trách nhiệm tổ chức lập và thực hiện dự án tái định cư để bảo đảm chủ động trong việc bố trí tái định cư cho người có đất thu hồi. Việc phê duyệt phương án bồi thường, hỗ trợ, tái định cư và việc bố trí tái định cư phải được hoàn thành trước khi có quyết định thu hồi đất.
7. Khi Nhà nước thu hồi đất theo quy định tại Điều 78 và Điều 79 của Luật này mà phần diện tích còn lại của thửa đất sau khi thu hồi nhỏ hơn diện tích tối thiểu theo quy định của Ủy ban nhân dân cấp tỉnh về diện tích tối thiểu tại khoản 2 Điều 220 của Luật này, nếu người sử dụng đất đồng ý thu hồi đất thì Ủy ban nhân dân cấp có thẩm quyền quyết định thu hồi đất và thực hiện việc bồi thường, hỗ trợ, quản lý diện tích đất này theo quy định của pháp luật. Kinh phí bồi thường, hỗ trợ trong trường hợp thu hồi đất quy định tại khoản này được tính vào kinh phí bồi thường, hỗ trợ, tái định cư của dự án đầu tư.
```

## Điều 91 — cấu hình C

Chunk `8d0cc3d6ab6ffb7ceba75ce32973b9a4`; 221 token; Điều `91`; Khoản `1`; Chương `VII`.

Nguồn/trang: `luatdat2.pdf:1`

```text
Điều 91. Nguyên tắc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất
1. Việc bồi thường, hỗ trợ, tái định cư khi Nhà nước thu hồi đất phải bảo đảm dân chủ, khách quan, công bằng, công khai, minh bạch, kịp thời và đúng quy định của pháp luật; vì lợi ích chung, sự phát triển bền vững, văn minh và hiện đại của cộng đồng, của địa phương; quan tâm đến đối tượng chính sách xã hội, đối tượng trực tiếp sản xuất nông nghiệp.
```


## Điều 172 — cấu hình A

Chunk `d79d7c54ed4f4746ceb6bda9caa33dc6`; 512 token; Điều `None`; Khoản `None`; Chương `None`.

Nguồn/trang: `luatdat3.pdf:1`, `luatdat3.pdf:2`

```text
ất quy định tại khoản 3 Điều 173 và khoản 2 Điều 174 của Luật này.
Điều 172. Đất sử dụng có thời hạn
1. Trừ các trường hợp quy định tại Điều 171 của Luật này, thời hạn sử dụng đất khi được Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất được quy định như sau:
a) Thời hạn giao đất, công nhận quyền sử dụng đất nông nghiệp đối với cá nhân trực tiếp sản xuất nông nghiệp sử dụng đất trồng cây hằng năm, đất nuôi trồng thủy sản, đất làm muối, đất trồng cây lâu năm, đất rừng sản xuất là rừng trồng trong hạn mức quy định tại Điều 176 của Luật này là 50 năm. Khi hết thời hạn sử dụng đất, thì được tiếp tục sử dụng đất theo thời hạn quy định tại điểm này mà không phải làm thủ tục gia hạn;
b) Thời hạn cho thuê đất nông nghiệp đối với cá nhân không quá 50 năm. Khi hết thời hạn thuê đất, cá nhân nếu có nhu cầu thì được Nhà nước xem xét tiếp tục cho thuê đất nhưng không quá 50 năm;
c) Thời hạn giao đất, cho thuê đất để thực hiện các dự án đầu tư có sử dụng đất được xem xét, quyết định theo thời hạn hoạt động của dự án
```


## Điều 172 — cấu hình B

Chunk `64a26df959e371803d3093386f70d887`; 1468 token; Điều `172`; Khoản `None`; Chương `XIII`.

Nguồn/trang: `luatdat3.pdf:1`, `luatdat3.pdf:2`, `luatdat3.pdf:3`

```text
Điều 172. Đất sử dụng có thời hạn
1. Trừ các trường hợp quy định tại Điều 171 của Luật này, thời hạn sử dụng đất khi được Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất được quy định như sau:
a) Thời hạn giao đất, công nhận quyền sử dụng đất nông nghiệp đối với cá nhân trực tiếp sản xuất nông nghiệp sử dụng đất trồng cây hằng năm, đất nuôi trồng thủy sản, đất làm muối, đất trồng cây lâu năm, đất rừng sản xuất là rừng trồng trong hạn mức quy định tại Điều 176 của Luật này là 50 năm. Khi hết thời hạn sử dụng đất, thì được tiếp tục sử dụng đất theo thời hạn quy định tại điểm này mà không phải làm thủ tục gia hạn;
b) Thời hạn cho thuê đất nông nghiệp đối với cá nhân không quá 50 năm. Khi hết thời hạn thuê đất, cá nhân nếu có nhu cầu thì được Nhà nước xem xét tiếp tục cho thuê đất nhưng không quá 50 năm;
c) Thời hạn giao đất, cho thuê đất để thực hiện các dự án đầu tư có sử dụng đất được xem xét, quyết định theo thời hạn hoạt động của dự án đầu tư hoặc đơn xin giao đất, thuê đất nhưng không quá 50 năm. Đối với các dự án có thời hạn hoạt động trên 50 năm theo quy định của Luật Đầu tư thì thời hạn giao đất, cho thuê đất theo thời hạn của dự án nhưng không quá 70 năm. Khi hết thời hạn, người sử dụng đất nếu có nhu cầu tiếp tục sử dụng thì được Nhà nước xem xét gia hạn sử dụng đất nhưng không quá thời hạn quy định tại khoản này. Trường hợp không phải lập dự án đầu tư thì thời hạn sử dụng đất được xem xét trên cơ sở đơn xin giao đất, cho thuê đất nhưng không quá 50 năm;
d) Thời hạn cho thuê đất xây dựng trụ sở làm việc của tổ chức nước ngoài có chức năng ngoại giao không quá 99 năm. Khi hết thời hạn, tổ chức nước ngoài có chức năng ngoại giao nếu có nhu cầu sử dụng đất thì được Nhà nước xem xét gia hạn hoặc cho thuê đất khác; thời hạn gia hạn hoặc cho thuê đất khác không quá thời hạn quy định tại khoản này.
2. Thời hạn giao đất, cho thuê đất quy định tại Điều này được tính từ ngày có quyết định giao đất, cho thuê đất của cơ quan nhà nước có thẩm quyền.
3. Việc gia hạn sử dụng đất được thực hiện trong năm cuối của thời hạn sử dụng đất, trừ trường hợp quy định tại điểm a khoản 1 Điều này. Người sử dụng đất có nhu cầu gia hạn sử dụng đất phải nộp hồ sơ đề nghị gia hạn chậm nhất là 06 tháng trước khi hết thời hạn sử dụng đất. Quá thời hạn phải nộp hồ sơ đề nghị gia hạn mà người sử dụng đất không nộp hồ sơ đề nghị gia hạn thì không được gia hạn sử dụng đất, trừ trường hợp bất khả kháng. Trường hợp không được gia hạn sử dụng đất, cơ quan nhà nước có thẩm quyền thực hiện thu hồi đất theo quy định của Luật này.
4. Trường hợp không được gia hạn sử dụng đất, người sử dụng đất có trách nhiệm xử lý tài sản gắn liền với đất để hoàn trả mặt bằng cho Nhà nước. Quá thời
hạn 24 tháng kể từ thời điểm hết thời hạn sử dụng đất mà người sử dụng đất không xử lý tài sản thì Nhà nước thu hồi đất mà không bồi thường về đất và tài sản gắn liền với đất; trường hợp phải phá dỡ, chủ sở hữu tài sản phải chịu chi phí phá dỡ.
5. Chính phủ quy định chi tiết Điều này.
```

## Điều 172 — cấu hình C

Chunk `8f9858b390b20bbbd00836d99647486c`; 902 token; Điều `172`; Khoản `1`; Chương `XIII`.

Nguồn/trang: `luatdat3.pdf:1`, `luatdat3.pdf:2`

```text
Điều 172. Đất sử dụng có thời hạn
1. Trừ các trường hợp quy định tại Điều 171 của Luật này, thời hạn sử dụng đất khi được Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất được quy định như sau:
a) Thời hạn giao đất, công nhận quyền sử dụng đất nông nghiệp đối với cá nhân trực tiếp sản xuất nông nghiệp sử dụng đất trồng cây hằng năm, đất nuôi trồng thủy sản, đất làm muối, đất trồng cây lâu năm, đất rừng sản xuất là rừng trồng trong hạn mức quy định tại Điều 176 của Luật này là 50 năm. Khi hết thời hạn sử dụng đất, thì được tiếp tục sử dụng đất theo thời hạn quy định tại điểm này mà không phải làm thủ tục gia hạn;
b) Thời hạn cho thuê đất nông nghiệp đối với cá nhân không quá 50 năm. Khi hết thời hạn thuê đất, cá nhân nếu có nhu cầu thì được Nhà nước xem xét tiếp tục cho thuê đất nhưng không quá 50 năm;
c) Thời hạn giao đất, cho thuê đất để thực hiện các dự án đầu tư có sử dụng đất được xem xét, quyết định theo thời hạn hoạt động của dự án đầu tư hoặc đơn xin giao đất, thuê đất nhưng không quá 50 năm. Đối với các dự án có thời hạn hoạt động trên 50 năm theo quy định của Luật Đầu tư thì thời hạn giao đất, cho thuê đất theo thời hạn của dự án nhưng không quá 70 năm. Khi hết thời hạn, người sử dụng đất nếu có nhu cầu tiếp tục sử dụng thì được Nhà nước xem xét gia hạn sử dụng đất nhưng không quá thời hạn quy định tại khoản này. Trường hợp không phải lập dự án đầu tư thì thời hạn sử dụng đất được xem xét trên cơ sở đơn xin giao đất, cho thuê đất nhưng không quá 50 năm;
d) Thời hạn cho thuê đất xây dựng trụ sở làm việc của tổ chức nước ngoài có chức năng ngoại giao không quá 99 năm. Khi hết thời hạn, tổ chức nước ngoài có chức năng ngoại giao nếu có nhu cầu sử dụng đất thì được Nhà nước xem xét gia hạn hoặc cho thuê đất khác; thời hạn gia hạn hoặc cho thuê đất khác không quá thời hạn quy định tại khoản này.
```

## Bổ sung: Khoản dài nhất của C (kiểm tra giữ nguyên đơn vị)

Chunk `476da231d78b9d10e7dff1be91a48479`; 2107 token; Điều `137`; Khoản `1`; Chương `X`.

Nguồn/trang: `luatdat2.pdf:47`, `luatdat2.pdf:48`, `luatdat2.pdf:49`

```text
Điều 137. Cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất đối với hộ gia đình, cá nhân, cộng đồng dân cư đang sử dụng đất có giấy tờ về quyền sử dụng đất
1. Hộ gia đình, cá nhân đang sử dụng đất ổn định mà có một trong các loại giấy tờ được lập trước ngày 15 tháng 10 năm 1993 sau đây thì được cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất và không phải nộp tiền sử dụng đất:
a) Những giấy tờ về quyền được sử dụng đất do cơ quan có thẩm quyền cấp trong quá trình thực hiện chính sách đất đai của Nhà nước Việt Nam dân chủ Cộng hòa, Chính phủ Cách mạng lâm thời Cộng hòa miền Nam Việt Nam và Nhà nước Cộng hòa xã hội chủ nghĩa Việt Nam;
b) Một trong các giấy tờ về quyền sử dụng đất do cơ quan có thẩm quyền thuộc chế độ cũ cấp cho người sử dụng đất, gồm: Bằng khoán điền thổ; Văn tự đoạn mãi bất động sản có chứng nhận của cơ quan thuộc chế độ cũ; Văn tự mua bán nhà ở, tặng cho nhà ở, đổi nhà ở, thừa kế nhà ở mà gắn liền với đất ở có chứng nhận của cơ quan thuộc chế độ cũ; Bản di chúc hoặc giấy thỏa thuận tương phân di
sản về nhà ở được cơ quan thuộc chế độ cũ chứng nhận; Giấy phép cho xây cất nhà ở; Giấy phép hợp thức hóa kiến trúc của cơ quan thuộc chế độ cũ cấp; Bản án của Tòa án thuộc chế độ cũ đã có hiệu lực thi hành;
c) Giấy chứng nhận quyền sử dụng đất tạm thời được cơ quan nhà nước có thẩm quyền cấp hoặc có tên trong Sổ đăng ký ruộng đất, Sổ địa chính;
d) Giấy tờ chuyển nhượng quyền sử dụng đất, mua bán nhà ở gắn liền với đất ở, nay được Ủy ban nhân dân cấp xã xác nhận đã sử dụng đất trước ngày 15 tháng 10 năm 1993;
đ) Sổ mục kê, sổ kiến điền lập trước ngày 18 tháng 12 năm 1980 mà có tên người sử dụng đất;
e) Một trong các giấy tờ được lập trong quá trình thực hiện đăng ký ruộng đất theo Chỉ thị số 299/TTg ngày 10 tháng 11 năm 1980 của Thủ tướng Chính phủ về công tác đo đạc, phân hạng và đăng ký ruộng đất trong cả nước do cơ quan nhà nước đang quản lý mà có tên người sử dụng đất, bao gồm: Biên bản xét duyệt của Hội đồng đăng ký ruộng đất cấp xã xác định người đang sử dụng đất là hợp pháp; Bản tổng hợp các trường hợp sử dụng đất hợp pháp do Ủy ban nhân dân cấp xã hoặc Hội đồng đăng ký ruộng đất cấp xã hoặc cơ quan quản lý đất đai cấp huyện, cấp tỉnh lập; Đơn xin đăng ký quyền sử dụng ruộng đất; Giấy tờ về việc chứng nhận đã đăng ký quyền sử dụng đất của Ủy ban nhân dân cấp xã, cấp huyện hoặc cấp tỉnh cấp cho người sử dụng đất;
g) Giấy tờ về việc kê khai, đăng ký nhà cửa được Ủy ban nhân dân cấp xã, cấp huyện hoặc cấp tỉnh xác nhận mà trong đó có ghi diện tích đất có nhà;
h) Giấy tờ của đơn vị quốc phòng giao đất cho cán bộ, chiến sĩ làm nhà ở theo Chỉ thị số 282/CT-QP ngày 11 tháng 7 năm 1991 của Bộ trưởng Bộ Quốc phòng mà việc giao đất đó phù hợp với quy hoạch sử dụng đất làm nhà ở của cán bộ, chiến sĩ trong quy hoạch đất quốc phòng đã được phê duyệt tại thời điểm giao đất;
i) Dự án hoặc danh sách hoặc văn bản về việc di dân đi xây dựng khu kinh tế mới, di dân tái định cư được Ủy ban nhân dân cấp huyện, cấp tỉnh hoặc cơ quan có thẩm quyền phê duyệt mà có tên người sử dụng đất;
k) Giấy tờ có nội dung về quyền sở hữu nhà ở, công trình; giấy tờ về việc xây dựng, sửa chữa nhà ở, công trình được Ủy ban nhân dân cấp huyện, cấp tỉnh hoặc cơ quan quản lý nhà nước về nhà ở, xây dựng chứng nhận hoặc cho phép;
l) Giấy tờ tạm giao đất của Ủy ban nhân dân cấp huyện, cấp tỉnh; Đơn đề nghị được sử dụng đất được Ủy ban nhân dân cấp xã, hợp tác xã nông nghiệp phê duyệt, chấp thuận trước ngày 01 tháng 7 năm 1980 hoặc được Ủy ban nhân dân cấp huyện, cấp tỉnh phê duyệt, chấp thuận;
m) Giấy tờ của cơ quan nhà nước có thẩm quyền về việc giao đất cho cơ quan, tổ chức để bố trí đất cho cán bộ, công nhân viên tự làm nhà ở hoặc xây dựng nhà ở để phân hoặc cấp cho cán bộ, công nhân viên bằng vốn không thuộc ngân sách nhà nước hoặc do cán bộ, công nhân viên tự đóng góp xây dựng;
n) Giấy tờ khác về quyền sử dụng đất có trước ngày 15 tháng 10 năm 1993 do Ủy ban nhân dân cấp tỉnh quy định phù hợp với thực tiễn của địa phương.
```
