from fetchers.yonhap import fetch as fetch_yonhap
from fetchers.news1 import fetch as fetch_news1

# 이미 본 기사(URL 기준)
seen_urls = set()

# 프로그램 시작 직후 한 번만 사용하는 플래그
initialized = False


def get_current_articles():

    articles = []

    try:
        yh = fetch_yonhap()
        print("연합뉴스 수:", len(yh))
        articles.extend(yh)
    except Exception as e:
        print("연합뉴스 오류:", e)

    try:
        n1 = fetch_news1()
        print("뉴스1 수:", len(n1))
        articles.extend(n1)
    except Exception as e:
        print("뉴스1 오류:", e)

    articles.sort(
        key=lambda x: x.get("datetime", ""),
        reverse=True
    )

    print("최종 기사 수:", len(articles))

    return articles[:20]


def get_new_articles():

    global initialized

    articles = get_current_articles()

    new_articles = []

    # 프로그램 처음 실행 시에는
    # 기존 기사들을 '이미 본 기사'로만 등록하고
    # NEW나 알림은 보내지 않는다.
    if not initialized:

        for article in articles:
            seen_urls.add(article["url"])

        initialized = True

        return []

    # 이후부터는 URL이 처음 등장한 기사만 반환
    for article in articles:

        url = article["url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)
        new_articles.append(article)

    return new_articles
