from fetchers.yonhap import fetch as fetch_yonhap
from fetchers.news1 import fetch as fetch_news1

# 이미 본 기사(URL 기준)
seen_urls = set()

# 프로그램 시작 직후 한 번만 사용하는 플래그
initialized = False


def get_current_articles():

    articles = []

    try:
        articles.extend(fetch_yonhap())
    except Exception:
        pass

    try:
        articles.extend(fetch_news1())
    except Exception:
        pass

    articles.sort(
        key=lambda x: x.get("datetime", ""),
        reverse=True
    )

    return articles[:20]


def get_new_articles():

    global initialized

    articles = get_current_articles()

    articles.sort(
        key=lambda x: x.get("datetime", ""),
        reverse=True
    )

    new_articles = []

    if not initialized:
        for article in articles:
            if article.get("type") == "breaking":
                continue

            seen_urls.add(article["url"])

        initialized = True
        return []

    for article in articles:

        url = article["url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)
        new_articles.append(article)

    print("새 기사:", len(new_articles))

    return new_articles
