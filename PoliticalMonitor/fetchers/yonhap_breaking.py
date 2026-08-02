import requests
from bs4 import BeautifulSoup

from config import HEADERS
from config import POLITICAL_KEYWORDS

BASE_URL = "https://www.yna.co.kr"
LIST_URL = "https://www.yna.co.kr/theme/breaknews-history"

PRESS = "연합뉴스"

MAX_ARTICLES = 5

seen_urls = set()


def is_political(title):
    return any(keyword in title for keyword in POLITICAL_KEYWORDS)


def extract_datetime(article):
    """
    기사 시간 추출

    (연합뉴스 구조 확인 후 구현)
    """
    return article.select_one("span.txt-time").get_text(strip=True) if article.select_one("span.txt-time") else ""


def fetch_articles():

    articles = []

    try:

        res = requests.get(
            LIST_URL,
            headers=HEADERS,
            timeout=10
        )

        res.raise_for_status()

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        for item in soup.select("ul.list01 > li"):
            news = item.select_one("div.news-con")
            if not news:
                continue
            title_tag = news.select_one("span.title01")
            link_tag = news.select_one("a.tit-news")
            if not title_tag or not link_tag:
                continue
            title = title_tag.get_text(strip=True)
            url = link_tag.get("href","").strip()
            if url.startswith("/"):
                url = BASE_URL + url
            articles.append({
                "title": title,
                "url": url,
                "datetime": extract_datetime(news)
            })

    except Exception as e:

        print("[연합뉴스 속보] 오류:", e)

    return articles[:MAX_ARTICLES]


def get_breaking_articles():

    new_articles = []

    for article in fetch_articles():

        if not is_political(article["title"]):
            continue

        if article["url"] in seen_urls:
            continue

        seen_urls.add(article["url"])

        new_articles.append({

            "media": PRESS,

            "title": article["title"],

            "url": article["url"],

            "datetime": article["datetime"],

            "type": "breaking"

        })

    return new_articles
