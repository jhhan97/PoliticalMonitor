import re
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config import HEADERS


BASE_URL = "https://www.yna.co.kr"
LIST_URL = "https://www.yna.co.kr/politics/national-assembly"
MAX_ARTICLES = 10


def extract_datetime(soup):
    """Return the original publication time in YYYY-MM-DD HH:MM format."""
    for prop in (
        "article:published_time",
        "og:article:published_time",
        "article:modified_time",
        "og:article:modified_time",
    ):
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            match = re.search(
                r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})",
                tag["content"],
            )
            if match:
                year, month, day, hour, minute = match.groups()
                return f"{year}-{month}-{day} {hour}:{minute}"

    time_tag = soup.find("time")
    if time_tag:
        value = time_tag.get("datetime") or time_tag.get_text(" ", strip=True)
        match = re.search(
            r"(\d{4})[-.](\d{2})[-.](\d{2}).*?(\d{2}):(\d{2})",
            value,
        )
        if match:
            year, month, day, hour, minute = match.groups()
            return f"{year}-{month}-{day} {hour}:{minute}"

    text = soup.get_text(" ", strip=True)
    for pattern in (
        r"(20\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})",
        r"(20\d{2})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})",
    ):
        match = re.search(pattern, text)
        if match:
            year, month, day, hour, minute = match.groups()
            return f"{year}-{month}-{day} {hour}:{minute}"

    return ""


def is_politics_article(url):
    """Accept only article links explicitly classified by Yonhap as politics."""
    parsed = urlparse(url)
    if not parsed.path.startswith("/view/AKR"):
        return False

    section = parse_qs(parsed.query).get("section", [""])[0]
    section = unquote(section).strip().lower()
    return section.startswith("politics/")


def get_links():
    links = []
    seen_paths = set()

    response = requests.get(LIST_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for anchor in soup.select("a[href]"):
        full_url = urljoin(BASE_URL, anchor.get("href", ""))

        if not is_politics_article(full_url):
            continue

        article_path = urlparse(full_url).path
        if article_path in seen_paths:
            continue

        seen_paths.add(article_path)
        links.append(full_url)

        if len(links) == MAX_ARTICLES:
            break

    return links


def fetch():
    articles = []

    for url in get_links():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            title_tag = soup.find("meta", property="og:title")
            title = title_tag.get("content", "") if title_tag else ""
            if not title and soup.title:
                title = soup.title.get_text(strip=True)

            articles.append(
                {
                    "media": "연합뉴스",
                    "title": title,
                    "url": url,
                    "datetime": extract_datetime(soup),
                }
            )
        except Exception:
            pass

    articles.sort(key=lambda item: item.get("datetime", ""), reverse=True)
    return articles
