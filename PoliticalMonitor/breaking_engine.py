"""
breaking_engine.py (TEST VERSION)

속보 전용 엔진
현재는 fake_breaking.py만 호출한다.
실전에서는 yonhap_breaking, news1_breaking으로 교체 예정.
"""

from fetchers.fake_breaking import (get_breaking_articles as fetch_fake_breaking)

seen_breaking_urls = set()


def get_breaking_articles():
    """새로운 속보만 반환"""

    try:
        articles = fetch_fake_breaking()
    except Exception as e:
        print("FAKE 속보 오류:", e)
        return []

    new_articles = []

    for article in articles:
        url = article["url"]

        if url in seen_breaking_urls:
            continue

        seen_breaking_urls.add(url)
        new_articles.append(article)

    if new_articles:
        print(f"[BREAKING ENGINE] 신규 속보 {len(new_articles)}건")

    return new_articles
