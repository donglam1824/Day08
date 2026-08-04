"""
Task 2 — Crawl bài viết/hướng dẫn hỗ trợ khách hàng về thương mại điện tử.

Hướng dẫn:
    1. Crawl tối thiểu 5 bài viết từ trung tâm trợ giúp công khai của một sàn TMĐT.
    2. Sử dụng Crawl4AI hoặc thư viện crawling tương tự.
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content).

Cài đặt:
    pip install crawl4ai
    playwright install chromium   # bắt buộc — pip install crawl4ai KHÔNG tự tải browser binary,
                                   # thiếu bước này sẽ báo lỗi
                                   # "BrowserType.launch: Executable doesn't exist"

Gợi ý chủ đề: theo dõi đơn hàng, đổi phương thức thanh toán, bằng chứng hoàn tiền,
mua hàng xuyên biên giới.

Lưu ý: một số trang help center dùng JavaScript render (SPA) — nếu crawl về chỉ thấy
tiêu đề mà không có nội dung, đổi sang bài viết khác cùng domain thay vì cố xử lý.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


ARTICLE_URLS = [
    # Theo dõi đơn hàng
    "https://help.shopee.vn/portal/4/article/79600-Theo-D%C3%B5i-%C4%90%C6%A1n-H%C3%A0ng-T%E1%BA%A1i-M%E1%BB%A5c-%22Tr%C3%B2-Chuy%E1%BB%87n-V%E1%BB%9Bi-Shopee%22",
    "https://help.shopee.vn/portal/4/article/79491-%5BThao-t%C3%A1c%5D-C%C3%A1ch-tra-c%E1%BB%A9u-m%C3%A3-v%E1%BA%ADn-%C4%91%C6%A1n-c%E1%BB%A7a-%C4%91%C6%A1n-h%C3%A0ng",
    # Đổi phương thức thanh toán
    "https://help.shopee.vn/portal/4/article/79555-%5BTh%C3%A0nh-vi%C3%AAn-m%E1%BB%9Bi%5D-T%C3%B4i-c%C3%B3-th%E1%BB%83-thay-%C4%91%E1%BB%95i-ph%C6%B0%C6%A1ng-th%E1%BB%A9c-thanh-to%C3%A1n-cho-%C4%91%C6%A1n-h%C3%A0ng-kh%C3%B4ng",
    # Bằng chứng hoàn tiền
    "https://help.shopee.vn/portal/4/article/79467-%5BTr%E1%BA%A3-h%C3%A0ng/Ho%C3%A0n-ti%E1%BB%81n%5D-H%C6%B0%E1%BB%9Bng-d%E1%BA%ABn-chu%E1%BA%A9n-b%E1%BB%8B-b%E1%BA%B1ng-ch%E1%BB%A9ng-khi-y%C3%AAu-c%E1%BA%A7u-Tr%E1%BA%A3-h%C3%A0ng/-Ho%C3%A0n-ti%E1%BB%81n",
    # Mua hàng xuyên biên giới
    "https://help.shopee.vn/portal/4/article/79377-%5BTh%C3%A0nh-vi%C3%AAn-m%E1%BB%9Bi%5D-T%C3%B4i-c%C3%B3-th%E1%BB%83-mua-h%C3%A0ng-tr%C3%AAn-Shopee-c%E1%BB%A7a-nh%E1%BB%AFng-qu%E1%BB%91c-gia-kh%C3%A1c-ngo%C3%A0i-Vi%E1%BB%87t-Nam-kh%C3%B4ng",
]


async def crawl_article(url: str) -> dict:
    """
    Crawl một bài viết và trả về dict chứa metadata + content.

    Returns:
        {
            "url": str,
            "title": str,
            "date_crawled": str (ISO format),
            "content_markdown": str
        }
    """
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return {
            "url": url,
            "title": result.metadata.get("title", "Unknown"),
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": result.markdown,
        }


async def crawl_all():
    """Crawl toàn bộ bài viết trong ARTICLE_URLS."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        article = await crawl_article(url)

        # Lưu file JSON
        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Saved: {filepath}")


if __name__ == "__main__":
    if not ARTICLE_URLS:
        print("⚠ Hãy điền ARTICLE_URLS trước khi chạy!")
        print("Gợi ý: tìm trang hướng dẫn/hỗ trợ khách hàng trên help center của sàn TMĐT")
    else:
        asyncio.run(crawl_all())
