import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    )
}

url = "https://search.naver.com/search.naver?ssc=tab.news.all&query=%EC%86%8D%EB%B3%B4&sm=tab_opt&sort=1&photo=0&field=0&pd=0&mynews=1&office_type=1&office_section_code=2&news_office_checked=1421&nso=so%3Add%2Cp%3Aall%2Ca%3Aall&is_sug_officeid=0&office_category=0&service_area="

r = requests.get(url, headers=HEADERS, timeout=10)

print(r.status_code)

with open("naver.html", "w", encoding="utf-8") as f:
    f.write(r.text)

print("저장 완료")

if __name__ == "__main__":
    import requests

    url = "https://search.naver.com/search.naver?ssc=tab.news.all&query=%EC%86%8D%EB%B3%B4&sm=tab_opt&sort=1&photo=0&field=0&pd=0&mynews=1&office_type=1&office_section_code=2&news_office_checked=1421&nso=so%3Add%2Cp%3Aall%2Ca%3Aall&is_sug_officeid=0&office_category=0&service_area="

    r = requests.get(url, headers=HEADERS, timeout=10)

    print(r.status_code)
    print(r.text[:5000])
