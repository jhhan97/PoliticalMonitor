import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from config import HEADERS

BASE_URL = "https://www.news1.kr"


def extract_datetime(soup):
    # 1순위 : JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or script.get_text()
        if not text:
            continue

        match = re.search(
            r'"datePublished"\s*:\s*"([^"]+)"',
            text
        )

        if match:
            value = match.group(1)

            m = re.search(
                r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})",
                value
            )

            if m:
                y, mo, d, h, mi = m.groups()
                return f"{y}-{mo}-{d} {h}:{mi}"

    # 2순위 : 페이지 전체에서 검색
    text = soup.get_text(" ", strip=True)

    m = re.search(
        r"(20\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})",
        text
    )

    if m:
        y, mo, d, h, mi = m.groups()
        return f"{y}-{mo}-{d} {h}:{mi}"

    m = re.search(
        r"(20\d{2})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})",
        text
    )

    if m:
        y, mo, d, h, mi = m.groups()
        return f"{y}-{mo}-{d} {h}:{mi}"

    return ""


def fetch():

    list_url = "https://www.news1.kr/politics/assembly"

    articles = []
    seen = set()

    try:

        res = requests.get(
            list_url,
            headers=HEADERS,
            timeout=10
        )

        soup = BeautifulSoup(
            res.text,
            "html.parser"
        )

        links = soup.select("a[href]")

        for link in links:

            href = link.get("href")

            if not href:
                continue

            full_url = urljoin(
                BASE_URL,
                href
            )

            if not re.search(
                r"/politics/assembly/\d+",
                full_url
            ):
                continue

            if full_url in seen:
                continue

            seen.add(full_url)

            try:

                article = requests.get(
                    full_url,
                    headers=HEADERS,
                    timeout=10
                )

                article_soup = BeautifulSoup(
                    article.text,
                    "html.parser"
                )

                title = ""

                og = article_soup.find(
                    "meta",
                    property="og:title"
                )

                if og:
                    title = og.get("content", "")

                if not title:
                    title = article_soup.title.text.strip()

                dt = extract_datetime(article_soup)

                articles.append(
                    {
                        "media": "뉴스1",
                        "title": title,
                        "url": full_url,
                        "datetime": dt,
                    }
                )

            except Exception:
                pass

    except Exception:
        pass

    articles.sort(
        key=lambda x: x["datetime"],
        reverse=True
    )

    return articles[:10]
