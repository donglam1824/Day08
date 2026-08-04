import time
import random

def generate_mock_response(question: str) -> dict:
    """
    Simulates a backend LLM call. Returns a dictionary containing the answer,
    sources, and follow-up suggestions.
    """
    
    # Simulate network delay
    time.sleep(1.5)
    
    question_lower = question.lower()
    
    # Mock knowledge base routing based on keywords
    if "thuế" in question_lower or "hóa đơn" in question_lower:
        return _get_tax_response()
    elif "hủy" in question_lower or "hoàn" in question_lower or "trả" in question_lower:
        return _get_return_response()
    elif "đăng ký" in question_lower or "kinh doanh" in question_lower:
        return _get_registration_response()
    elif "sở hữu trí tuệ" in question_lower or "thương hiệu" in question_lower or "hình ảnh" in question_lower:
        return _get_ip_response()
    else:
        return _get_general_response()


def _get_tax_response():
    return {
        "answer": """### Kết luận ngắn
Bán hàng trên Shopee **có thể phải đóng thuế** nếu doanh thu từ kinh doanh của bạn vượt mức 100 triệu đồng/năm.

### Phân tích
Theo quy định hiện hành đối với cá nhân kinh doanh:
1. **Mức doanh thu chịu thuế**: Nếu tổng doanh thu từ hoạt động bán hàng (không chỉ trên Shopee mà tính tổng các nền tảng/cửa hàng) trên 100 triệu đồng/năm, bạn phải nộp thuế.
2. **Loại thuế phải nộp**:
   - Thuế Giá trị gia tăng (GTGT): 1%
   - Thuế Thu nhập cá nhân (TNCN): 0.5%
   - Lệ phí môn bài: Tùy bậc doanh thu (từ 300.000đ đến 1.000.000đ/năm).
   
Trường hợp là hộ kinh doanh cá thể hoặc doanh nghiệp, mức thuế suất sẽ áp dụng theo quy định dành cho mô hình đó. Mới đây, các sàn TMĐT như Shopee cũng được yêu cầu cung cấp thông tin người bán cho cơ quan thuế để phục vụ công tác quản lý.

### Bạn cần lưu ý
- Cơ quan thuế có thể truy thu thuế từ các năm trước nếu phát hiện bạn có doanh thu trên 100 triệu/năm nhưng chưa kê khai.
- Bạn nên chủ động ra chi cục thuế quận/huyện nơi cư trú để đăng ký thuế và kê khai.
""",
        "sources": [
            {
                "title": "Thông tư 40/2021/TT-BTC",
                "authority": "Bộ Tài chính",
                "article": "Hướng dẫn thuế GTGT, TNCN đối với cá nhân kinh doanh",
                "url": "#"
            },
            {
                "title": "Nghị định 91/2022/NĐ-CP",
                "authority": "Chính phủ",
                "article": "Sửa đổi Nghị định 126/2020/NĐ-CP, quy định trách nhiệm cung cấp thông tin của sàn TMĐT",
                "url": "#"
            }
        ],
        "suggestions": [
            "Làm sao để kê khai thuế cá nhân?",
            "Nếu bán lỗ thì có phải đóng thuế không?",
            "Quy định xuất hóa đơn điện tử"
        ]
    }

def _get_return_response():
    return {
        "answer": """### Kết luận ngắn
Người bán **có quyền từ chối** yêu cầu hoàn trả hàng nếu lý do hoàn trả không hợp lệ theo chính sách của Shopee hoặc không thuộc các trường hợp pháp luật quy định.

### Phân tích
**1. Theo chính sách của Sàn (Shopee):**
Shopee có quy định cụ thể về "Trả hàng/Hoàn tiền". Người mua được quyền trả hàng nếu:
- Giao sai sản phẩm, thiếu hàng.
- Hàng lỗi, hỏng hóc, bể vỡ trong quá trình vận chuyển.
- Hàng giả, hàng nhái, hoặc khác biệt rõ rệt so với mô tả.

**2. Quyền từ chối của Người bán:**
Nếu khách hàng trả hàng với lý do "Không thích nữa" (trừ khi shop tham gia chương trình cho phép điều này, ví dụ Shopee Mall) hoặc khách hàng làm hỏng sản phẩm, bạn có quyền nhấn "Từ chối" trên ứng dụng và cung cấp bằng chứng (video đóng gói, hình ảnh). Shopee sẽ đóng vai trò trung gian giải quyết tranh chấp (Dispute).

**3. Góc độ Luật Bảo vệ quyền lợi người tiêu dùng:**
Luật quy định người tiêu dùng có quyền yêu cầu bồi thường nếu hàng hóa không đúng như thông tin đã cung cấp. Tuy nhiên, nếu người bán đã cung cấp đúng hàng hóa và thông tin, người bán không có nghĩa vụ pháp lý phải nhận lại hàng chỉ vì người mua đổi ý, trừ khi có thỏa thuận khác.

### Bạn cần lưu ý
- **Bằng chứng là quan trọng nhất:** Luôn quay video quá trình đóng gói và dán mã vận đơn rõ ràng để làm bằng chứng khi có tranh chấp.
- Khi từ chối, hãy giao tiếp lịch sự với khách hàng để tránh bị đánh giá 1 sao.
""",
        "sources": [
            {
                "title": "Chính sách Trả hàng/Hoàn tiền",
                "authority": "Shopee Việt Nam",
                "article": "Quy định đối với người bán và người mua",
                "url": "#"
            },
            {
                "title": "Luật Bảo vệ quyền lợi người tiêu dùng 2023",
                "authority": "Quốc hội",
                "article": "Quyền và nghĩa vụ của người tiêu dùng trong TMĐT",
                "url": "#"
            }
        ],
        "suggestions": [
            "Cách cung cấp bằng chứng cho Shopee?",
            "Shopee xử lý tranh chấp mất bao lâu?",
            "Quy định bồi thường hàng vỡ hỏng"
        ]
    }

def _get_registration_response():
    return {
        "answer": """### Kết luận ngắn
Nếu bạn bán hàng thường xuyên và có thu nhập ổn định trên Shopee, bạn **cần phải đăng ký kinh doanh** (dưới hình thức Hộ kinh doanh cá thể hoặc Doanh nghiệp). Nếu chỉ bán thanh lý đồ cũ thỉnh thoảng, bạn không cần đăng ký.

### Phân tích
Theo Nghị định 39/2007/NĐ-CP và Nghị định 52/2013/NĐ-CP (về TMĐT):
- Cá nhân hoạt động thương mại một cách thường xuyên, liên tục, có mục đích sinh lời thì phải đăng ký kinh doanh.
- Các trường hợp được miễn đăng ký thường là người bán quà vặt, buôn chuyến, hoặc các dịch vụ cá nhân quy mô rất nhỏ (không có địa điểm cố định). Tuy nhiên, kinh doanh trên mạng hiện nay (có gian hàng, doanh thu đều) không thuộc diện được miễn.

Việc bán hàng trên Shopee là hoạt động cung cấp hàng hóa qua sàn giao dịch TMĐT. Do đó, bạn cần tuân thủ quy định đăng ký kinh doanh để hợp pháp hóa hoạt động và thực hiện nghĩa vụ thuế.

### Bạn cần lưu ý
- Hình thức phổ biến và dễ nhất cho cá nhân bán trên Shopee là **Đăng ký Hộ kinh doanh cá thể** tại UBND cấp Quận/Huyện.
- Việc đăng ký kinh doanh cũng giúp bạn dễ dàng đăng ký nhãn hiệu, bảo vệ thương hiệu và tham gia các chương trình như Shopee Mall.
""",
        "sources": [
            {
                "title": "Nghị định 52/2013/NĐ-CP",
                "authority": "Chính phủ",
                "article": "Quản lý hoạt động thương mại điện tử",
                "url": "#"
            },
            {
                "title": "Nghị định 01/2021/NĐ-CP",
                "authority": "Chính phủ",
                "article": "Về đăng ký doanh nghiệp và Hộ kinh doanh",
                "url": "#"
            }
        ],
        "suggestions": [
            "Thủ tục đăng ký Hộ kinh doanh?",
            "Bán hàng trên Shopee Mall cần điều kiện gì?",
            "Mức phạt nếu không đăng ký kinh doanh?"
        ]
    }

def _get_ip_response():
    return {
        "answer": """### Kết luận ngắn
Việc sử dụng hình ảnh sản phẩm, logo hoặc tên của thương hiệu khác để bán hàng mà **không có sự cho phép** (đại lý, phân phối) là **vi phạm pháp luật về Sở hữu trí tuệ** và chính sách của Shopee.

### Phân tích
- **Vi phạm bản quyền hình ảnh:** Những bức ảnh sản phẩm do thương hiệu tự chụp thuộc quyền tác giả của họ. Sao chép và đăng tải lại mà không xin phép là vi phạm quyền tác giả.
- **Vi phạm nhãn hiệu:** Sử dụng logo hoặc tên thương hiệu để bán hàng giả, hàng nhái, hoặc làm người tiêu dùng nhầm lẫn bạn là đại lý chính thức là vi phạm quyền đối với nhãn hiệu.
- **Hệ quả trên Shopee:** Chủ sở hữu thương hiệu có thể report gian hàng của bạn. Shopee sẽ tiến hành gỡ sản phẩm (xóa listing), khóa tài khoản, hoặc giữ tiền trong ví nếu xác định có vi phạm.

### Bạn cần lưu ý
- Nếu bạn là đại lý chính hãng, hãy chuẩn bị sẵn giấy chứng nhận phân phối, hóa đơn nhập hàng để cung cấp cho Shopee khi bị report.
- Tuyệt đối không bán hàng giả, hàng nhái các thương hiệu lớn, mức phạt hành chính theo quy định pháp luật rất cao, thậm chí có thể bị xử lý hình sự nếu quy mô lớn.
- Hãy tự chụp ảnh sản phẩm của mình để an toàn nhất.
""",
        "sources": [
            {
                "title": "Luật Sở hữu trí tuệ 2005 (sửa đổi, bổ sung 2022)",
                "authority": "Quốc hội",
                "article": "Quyền tác giả và Quyền sở hữu công nghiệp",
                "url": "#"
            },
            {
                "title": "Quy định về Hàng giả, Hàng nhái",
                "authority": "Shopee Việt Nam",
                "article": "Chính sách người bán",
                "url": "#"
            }
        ],
        "suggestions": [
            "Cách kháng nghị khi bị xóa sản phẩm?",
            "Bán hàng xách tay có vi phạm không?",
            "Thủ tục đăng ký nhãn hiệu của riêng mình?"
        ]
    }

def _get_general_response():
    return {
        "answer": """### Kết luận ngắn
Câu hỏi của bạn liên quan đến hoạt động thương mại điện tử, tuy nhiên tôi cần thêm một chút thông tin để đưa ra tư vấn pháp lý chính xác nhất.

### Phân tích
Hoạt động kinh doanh trên Shopee chịu sự điều chỉnh của nhiều hệ thống pháp luật khác nhau, bao gồm:
- **Luật Thương mại**: Quản lý hành vi mua bán hàng hóa.
- **Luật Giao dịch điện tử & Nghị định 52/2013/NĐ-CP**: Quản lý tính pháp lý của hợp đồng điện tử và nền tảng TMĐT.
- **Luật Bảo vệ quyền lợi người tiêu dùng**: Đảm bảo quyền lợi của khách mua hàng.
- **Pháp luật về Thuế**: Quản lý nghĩa vụ đóng góp ngân sách.

Để tôi có thể hỗ trợ tốt nhất, bạn có thể nêu rõ hơn ngữ cảnh không? Ví dụ:
- Bạn là người mua hay người bán?
- Vấn đề cụ thể bạn đang gặp phải là gì (Bị giữ tiền, bị khóa shop, khách đòi hoàn tiền,...)?

### Bạn cần lưu ý
Shopee có vai trò là "Thương nhân thiết lập website thương mại điện tử", họ có quyền đề ra các chính sách (Terms of Service) miễn là không trái với quy định pháp luật. Do đó, bên cạnh luật pháp, bạn cần tuân thủ "Tiêu chuẩn cộng đồng" và "Chính sách Người bán" của Shopee.
""",
        "sources": [
            {
                "title": "Nghị định 52/2013/NĐ-CP (sửa đổi bởi NĐ 85/2021/NĐ-CP)",
                "authority": "Chính phủ",
                "article": "Về thương mại điện tử",
                "url": "#"
            }
        ],
        "suggestions": [
            "Cách liên hệ bộ phận hỗ trợ Shopee?",
            "Shopee có quyền giữ tiền người bán không?",
            "Điều khoản chung cho người bán trên Shopee"
        ]
    }
