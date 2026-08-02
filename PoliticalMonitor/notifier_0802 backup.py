import webbrowser

from plyer import notification

from config import USE_WINDOWS_NOTIFICATION


def notify(article):

    if not USE_WINDOWS_NOTIFICATION:
        return

    try:

        media = article.get("media", "뉴스")
        article_type = article.get("type")

        if article_type:
            title = f"[{media}] {article_type}"
        else:
            title = f"[{media}]"

        notification.notify(
            title=title,
            message=article.get("title", ""),
            app_name="Political Monitor",
            timeout=8
        )

    except Exception as e:
        print("알림 오류:", e)


def open_article(article):

    try:
        webbrowser.open(article["url"])

    except Exception as e:
        print("브라우저 오류:", e)


if __name__ == "__main__":

    test_article = {
        "media": "연합뉴스",
        "title": "Political Monitor 알림 테스트입니다.",
        "url": "https://www.yna.co.kr"
    }

    notify(test_article)

    print("알림 테스트 완료")
