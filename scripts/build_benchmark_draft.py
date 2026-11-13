"""Materialize the authored benchmark draft; refuse to overwrite a locked dataset."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return re.sub(r'\s+', ' ', text).strip()


# Quotes are copied from the supplied publication, not generated legal facts.
SPECS = [
    ('dev', 'direct', 1, 1, '1', 'Luật Đất đai trong bộ tài liệu này điều chỉnh những nội dung nào?',
     'Chế độ sở hữu đất đai; quyền hạn, trách nhiệm của Nhà nước đại diện chủ sở hữu toàn dân và quản lý đất đai; quản lý, sử dụng đất; quyền, nghĩa vụ của công dân và người sử dụng đất đối với đất thuộc lãnh thổ Việt Nam.',
     'Luật này quy định về chế độ sở hữu đất đai, quyền hạn và trách nhiệm của Nhà nước đại diện chủ sở hữu toàn dân về đất đai và thống nhất quản lý về đất đai, chế độ quản lý và sử dụng đất đai, quyền và nghĩa vụ của công dân, người sử dụng đất đối với đất đai thuộc lãnh thổ của nước Cộng hòa xã hội chủ nghĩa Việt Nam.', {}),
    ('dev', 'paraphrase', 1, 1, '3.1', 'Bản đồ thể hiện các thửa đất được lập theo đơn vị hành chính nào và ai xác nhận?',
     'Theo đơn vị hành chính cấp xã, hoặc cấp huyện nơi không thành lập đơn vị hành chính cấp xã; cơ quan nhà nước có thẩm quyền xác nhận.',
     '1. Bản đồ địa chính là bản đồ thể hiện các thửa đất và các đối tượng địa lý có liên quan, lập theo đơn vị hành chính cấp xã hoặc theo đơn vị hành chính cấp huyện nơi không thành lập đơn vị hành chính cấp xã, được cơ quan nhà nước có thẩm quyền xác nhận.', {}),
    ('dev', 'paraphrase', 1, 2, '3.9', 'Việc tự sử dụng đất do Nhà nước quản lý hoặc đất của người sử dụng hợp pháp khác mà chưa được cho phép được gọi là gì?',
     'Chiếm đất.',
     '9. Chiếm đất là việc sử dụng đất do Nhà nước đã quản lý mà chưa được cơ quan nhà nước có thẩm quyền cho phép hoặc sử dụng đất của người sử dụng đất hợp pháp khác mà chưa được người đó cho phép.', {}),
    ('dev', 'direct', 1, 10, '9.1', 'Căn cứ vào mục đích sử dụng, đất đai được chia thành những nhóm nào?',
     'Nhóm đất nông nghiệp, nhóm đất phi nông nghiệp và nhóm đất chưa sử dụng.',
     '1. Căn cứ vào mục đích sử dụng, đất đai được phân loại bao gồm nhóm đất nông nghiệp, nhóm đất phi nông nghiệp, nhóm đất chưa sử dụng.', {}),
    ('dev', 'explicit_filter', 1, 11, '11.1', 'Chỉ tra cứu phần 1 của bộ PDF: lấn đất, chiếm đất và hủy hoại đất có nằm trong các hành vi bị nghiêm cấm không?',
     'Có; khoản 1 Điều 11 liệt kê lấn đất, chiếm đất, hủy hoại đất.',
     'Điều 11. Hành vi bị nghiêm cấm trong lĩnh vực đất đai 1. Lấn đất, chiếm đất, hủy hoại đất.', {'part': 1}),
    ('dev', 'direct', 1, 21, '26.2', 'Người sử dụng đất có quyền hưởng thành quả lao động và kết quả đầu tư trên loại đất nào?',
     'Trên đất sử dụng hợp pháp.',
     '2. Hưởng thành quả lao động, kết quả đầu tư trên đất sử dụng hợp pháp.', {}),
    ('dev', 'paraphrase', 1, 25, '31.1', 'Về mục đích, ranh giới, độ sâu và chiều cao, nghĩa vụ sử dụng đất được quy định như thế nào?',
     'Sử dụng đúng mục đích, đúng ranh giới, đúng quy định về độ sâu trong lòng đất và chiều cao trên không; bảo vệ công trình công cộng trong lòng đất và tuân thủ quy định liên quan.',
     '1. Sử dụng đất đúng mục đích, đúng ranh giới thửa đất, đúng quy định về sử dụng độ sâu trong lòng đất và chiều cao trên không, bảo vệ các công trình công cộng trong lòng đất và tuân thủ quy định khác của pháp luật có liên quan.', {}),
    ('dev', 'exception', 1, 40, '45.1.a', 'Riêng điều kiện có Giấy chứng nhận tại điểm a khoản 1 Điều 45 có ngoại lệ cho việc thừa kế quyền sử dụng đất không? Không xét các điều kiện khác.',
     'Có. Thừa kế quyền sử dụng đất nằm trong các trường hợp ngoại lệ của điều kiện Giấy chứng nhận ở điểm a; câu trả lời không miễn các điều kiện khác.',
     'a) Có Giấy chứng nhận quyền sử dụng đất hoặc Giấy chứng nhận quyền sở hữu nhà ở và quyền sử dụng đất ở hoặc Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất hoặc Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất, trừ trường hợp thừa kế quyền sử dụng đất, chuyển đổi đất nông nghiệp khi dồn điền, đổi thửa, tặng cho quyền sử dụng đất cho Nhà nước, cộng đồng dân cư và trường hợp quy định tại khoản 7 Điều 124 và điểm a khoản 4 Điều 127 của Luật này;', {}),
    ('dev', 'direct', 1, 53, '60.4', 'Theo nguyên tắc lập quy hoạch sử dụng đất, quy hoạch của cấp dưới phải phù hợp với quy hoạch nào?',
     'Quy hoạch sử dụng đất của cấp trên.',
     'quy hoạch sử dụng đất của cấp dưới phải phù hợp với quy hoạch sử dụng đất của cấp trên;', {}),
    ('dev', 'direct', 1, 25, '29.1', 'Quyền đối với thửa đất liền kề bao gồm những nhu cầu hạ tầng nào được nêu trong khoản 1 Điều 29?',
     'Lối đi; cấp, thoát nước; tưới, tiêu nước trong canh tác; cấp khí ga; lắp đường dây tải điện, thông tin liên lạc; các nhu cầu cần thiết khác theo pháp luật.',
     '1. Quyền đối với thửa đất liền kề bao gồm quyền về lối đi; cấp nước, thoát nước; tưới nước, tiêu nước trong canh tác; cấp khí ga; lắp đường dây tải điện, thông tin liên lạc và các nhu cầu cần thiết khác theo quy định của pháp luật.', {}),
    ('dev', 'conditional', 2, 1, '91.2', 'Người bị thu hồi đất được bồi thường bằng đất hoặc nhà ở nhưng muốn nhận tiền thì xử lý theo nguyện vọng nào?',
     'Được bồi thường bằng tiền theo nguyện vọng đã đăng ký khi lập phương án bồi thường, hỗ trợ, tái định cư.',
     'Trường hợp người có đất thu hồi được bồi thường bằng đất, bằng nhà ở mà có nhu cầu được bồi thường bằng tiền thì được bồi thường bằng tiền theo nguyện vọng đã đăng ký khi lập phương án bồi thường, hỗ trợ, tái định cư.', {}),
    ('dev', 'explicit_filter', 2, 2, '91.6', 'Chỉ dùng phần 2 của bộ PDF: phê duyệt phương án bồi thường, hỗ trợ, tái định cư và bố trí tái định cư phải hoàn thành trước mốc nào?',
     'Trước khi có quyết định thu hồi đất.',
     'Việc phê duyệt phương án bồi thường, hỗ trợ, tái định cư và việc bố trí tái định cư phải được hoàn thành trước khi có quyết định thu hồi đất.', {'part': 2}),
    ('dev', 'conditional', 2, 5, '94.6', 'Người được bồi thường khi Nhà nước thu hồi đất nhưng còn chưa thực hiện nghĩa vụ tài chính về đất đai thì khoản tiền còn thiếu được xử lý ra sao?',
     'Trừ khoản tiền chưa thực hiện nghĩa vụ tài chính vào số tiền bồi thường để hoàn trả ngân sách nhà nước.',
     '6. Người sử dụng đất được bồi thường khi Nhà nước thu hồi đất mà chưa thực hiện nghĩa vụ tài chính về đất đai đối với Nhà nước theo quy định của pháp luật thì phải trừ đi khoản tiền chưa thực hiện nghĩa vụ tài chính vào số tiền được bồi thường để hoàn trả ngân sách nhà nước.', {}),
    ('dev', 'conditional', 2, 25, '121.1.b', 'Chuyển đất nông nghiệp sang đất phi nông nghiệp có thuộc trường hợp phải được cơ quan có thẩm quyền cho phép không?',
     'Có, thuộc điểm b khoản 1 Điều 121.',
     'Điều 121. Chuyển mục đích sử dụng đất 1. Các trường hợp chuyển mục đích sử dụng đất phải được cơ quan nhà nước có thẩm quyền cho phép bao gồm: a) Chuyển đất trồng lúa, đất rừng đặc dụng, đất rừng phòng hộ, đất rừng sản xuất sang loại đất khác trong nhóm đất nông nghiệp; b) Chuyển đất nông nghiệp sang đất phi nông nghiệp;', {}),
    ('dev', 'conditional', 2, 43, '135.1', 'Người dùng nhiều thửa đất nông nghiệp trong cùng một xã, phường hoặc thị trấn có thể yêu cầu cấp chung một Giấy chứng nhận không?',
     'Có; khi có yêu cầu được cấp một Giấy chứng nhận chung cho các thửa đất đó theo trường hợp nêu tại khoản 1 Điều 135.',
     'Trường hợp người sử dụng đất đang sử dụng nhiều thửa đất nông nghiệp tại cùng 01 xã, phường, thị trấn mà có yêu cầu thì được cấp 01 Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất chung cho các thửa đất đó.', {}),
    ('test', 'direct', 3, 1, '171.1', 'Đất ở thuộc nhóm sử dụng ổn định lâu dài hay nhóm sử dụng có thời hạn trong bản luật được cung cấp?',
     'Thuộc đất sử dụng ổn định lâu dài, khoản 1 Điều 171.',
     'Điều 171. Đất sử dụng ổn định lâu dài 1. Đất ở.', {}),
    ('test', 'conditional', 3, 2, '172.1.a', 'Cá nhân trực tiếp sản xuất nông nghiệp được giao hoặc công nhận đất trồng cây hằng năm trong hạn mức Điều 176 có thời hạn bao lâu; khi hết hạn có phải làm thủ tục gia hạn không?',
     '50 năm; khi hết hạn được tiếp tục sử dụng theo thời hạn quy định tại điểm a mà không phải làm thủ tục gia hạn.',
     'a) Thời hạn giao đất, công nhận quyền sử dụng đất nông nghiệp đối với cá nhân trực tiếp sản xuất nông nghiệp sử dụng đất trồng cây hằng năm, đất nuôi trồng thủy sản, đất làm muối, đất trồng cây lâu năm, đất rừng sản xuất là rừng trồng trong hạn mức quy định tại Điều 176 của Luật này là 50 năm. Khi hết thời hạn sử dụng đất, thì được tiếp tục sử dụng đất theo thời hạn quy định tại điểm này mà không phải làm thủ tục gia hạn;', {}),
    ('test', 'conditional', 3, 3, '173.1.b', 'Cá nhân chuyển đất trồng cây hằng năm sang đất rừng đặc dụng thì thời hạn sử dụng được xác định như thế nào?',
     'Ổn định lâu dài.',
     'b) Trường hợp chuyển đất trồng cây hằng năm, đất trồng cây lâu năm, đất rừng sản xuất, đất nuôi trồng thủy sản, đất làm muối sang đất rừng đặc dụng, đất rừng phòng hộ thì thời hạn sử dụng đất là ổn định lâu dài;', {}),
    ('test', 'explicit_filter', 3, 34, '220.1.a', 'Chỉ tra cứu phần 3 của bộ PDF: khi tách hoặc hợp thửa, khoản 1 Điều 220 yêu cầu thửa đất đã có những loại Giấy chứng nhận nào?',
     'Một trong các loại: Giấy chứng nhận quyền sử dụng đất; Giấy chứng nhận quyền sở hữu nhà ở và quyền sử dụng đất ở; Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất; Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất.',
     'Điều 220. Tách thửa đất, hợp thửa đất 1. Việc tách thửa đất, hợp thửa đất phải bảo đảm các nguyên tắc, điều kiện sau đây: a) Thửa đất đã được cấp một trong các loại giấy chứng nhận: Giấy chứng nhận quyền sử dụng đất, Giấy chứng nhận quyền sở hữu nhà ở và quyền sử dụng đất ở, Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất, Giấy chứng nhận quyền sử dụng đất, quyền sở hữu tài sản gắn liền với đất;', {'part': 3}),
    ('test', 'direct', 3, 46, '235.2.c', 'Thủ tục hòa giải tranh chấp đất đai tại Ủy ban nhân dân cấp xã có thời hạn tối đa bao lâu và tính từ mốc nào?',
     'Không quá 30 ngày kể từ ngày nhận được đơn yêu cầu hòa giải tranh chấp đất đai.',
     'c) Việc hòa giải tranh chấp đất đai tại Ủy ban nhân dân cấp xã được thực hiện trong thời hạn không quá 30 ngày kể từ ngày nhận được đơn yêu cầu hòa giải tranh chấp đất đai;', {}),
]


def main():
    folder = ROOT / 'benchmark'
    if (folder / 'LOCK.json').exists():
        raise SystemExit('Benchmark is locked; do not regenerate it after approval/retrieval.')
    pages = [json.loads(line) for line in (ROOT / 'results/pages.jsonl').read_text(encoding='utf-8').splitlines()]
    questions = []
    review = ['# Gate 2 — duyệt benchmark', '',
              '> DRAFT: chưa có nhãn gold được học viên duyệt. Không chạy retrieval trước khi xác nhận Gate 2.', '',
              'Corpus chỉ là bản Luật Đất đai được cung cấp, không phải nội dung tư vấn pháp lý hiện hành. Số trang bên dưới là trang vật lý PDF.', '',
              '15 câu dev dùng phần 1–2; 5 câu test dùng phần 3. Việc đọc test để duyệt gold trước retrieval được ghi nhận; không được điều chỉnh thuật toán theo kết quả test sau này.', '']
    for index, (split, kind, part, page, locator, question, answer, quote, filters) in enumerate(SPECS, 1):
        quote = normalized(quote)
        alternatives = [{'source_id': p['source_id'], 'page': p['page'], 'evidence_quote': quote}
                        for p in pages if quote in normalized(p['text'])]
        source_id = f'luatdat{part}'
        if not any(g['source_id'] == source_id and g['page'] == page for g in alternatives):
            raise ValueError(f'q{index:02d}: authored quote does not occur on intended page {source_id}:{page}')
        item = {'id': f'q{index:02d}', 'split': split, 'type': kind, 'question': question,
                'expected_answer': answer, 'gold_source_id': source_id, 'gold_page': page,
                'evidence_quote': quote, 'gold_evidence': alternatives, 'filter': filters,
                'legal_locator': locator, 'human_review': 'pending'}
        questions.append(item)
        review.extend([f'## {item["id"]} — {split} — {kind}', '', question, '',
                       f'**Đáp án dự kiến:** {answer}', '',
                       f'**Nguồn:** `{source_id}.pdf`, trang PDF {page}; vị trí Điều/Khoản/Điểm: `{locator}`.', '',
                       f'**Filter do câu hỏi cung cấp:** `{json.dumps(filters, ensure_ascii=False)}`', '',
                       f'**Evidence:** {quote}', '',
                       f'**Gold hợp lệ tìm thấy:** {len(alternatives)} vị trí. **Học viên duyệt:** [ ]', ''])
    payload = ''.join(json.dumps(q, ensure_ascii=False) + '\n' for q in questions)
    (folder / 'questions.jsonl').write_text(payload, encoding='utf-8', newline='\n')
    (folder / 'REVIEW.md').write_text('\n'.join(review) + '\n', encoding='utf-8')
    print(f'Draft: {len(questions)} questions; SHA256={hashlib.sha256(payload.encode()).hexdigest()}')


if __name__ == '__main__':
    main()
