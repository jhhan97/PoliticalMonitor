"""
속보 전용 엔진

일반기사(news_engine)와 완전히 독립적으로 동작한다.

역할
- 속보 수집
- 중복 제거
- 속보 정렬
"""

from fetch.yonhap_breaking import fetch_yonhap_breaking
from fetch.news1_breaking import fetch_news1_breaking

seen_breaking_urls = set()


def get_breaking_articles():
    """
    새로운 속보만 반환한다.
    """

    articles = []

    # 연합뉴스 속보
    try:
        articles.extend(fetch_yonhap_breaking())
    except Exception as e:
        print("연합 속보 오류:", e)

    # 뉴스1 속보
    try:
        articles.extend(fetch_news1_breaking())
    except Exception as e:
        print("뉴스1 속보 오류:", e)

    # 최신순
    articles.sort(
        key=lambda x: x.get("datetime", ""),
        reverse=True
    )

    new_articles = []

    for article in articles:

        url = article["url"]

        if url in seen_breaking_urls:
            continue

        seen_breaking_urls.add(url)
        new_articles.append(article)

    return new_articles
