import threading
import time

from config import GENERAL_INTERVAL, BREAKING_INTERVAL

from fetchers.fake_breaking import get_breaking_articles as get_yonhap_breaking
from fetchers.fake_breaking_news1 import get_breaking_articles as get_news1_breaking


# 테스트용 속보 엔진



from gui import PoliticalMonitorGUI
from news_engine import get_current_articles, get_new_articles
from notifier import notify


def load_initial(app):
    """Load the existing article list without marking it as new."""
    try:
        articles = get_current_articles()
        for article in articles:
            article["new"] = False
            app.after(0, lambda item=article: app.add_article(item))
    except Exception as error:
        print("initial load error:", error)


def general_worker(app):
    """Add and notify only genuinely newly detected articles."""
    print("===== WORKER RUNNING =====")

    while True:
        try:
            articles = get_new_articles()
            print(f"새 기사: {len(articles)}")

            for article in articles:
                article["new"] = True
                app.after(0, lambda item=article: app.add_article(item))
                notify(article)

        except Exception as error:
            print("worker error:", error)

        time.sleep(GENERAL_INTERVAL)


def breaking_worker(app):
    """속보 전용 Worker"""

    print("===== BREAKING WORKER RUNNING =====")

    while True:
        try:
            articles = []

            # 연합뉴스 테스트 속보
            articles.extend(get_yonhap_breaking())

            # 뉴스1 테스트 속보
            articles.extend(get_news1_breaking())

            # 시간순 정렬
            articles.sort(
                key=lambda x: x.get("datetime", "")
            )

            if articles:
                print(f"[속보] 새 기사 {len(articles)}건")

            for article in articles:
                article["new"] = True
                app.after(
                    0,
                    lambda item=article: app.add_article(item)
                )
                notify(article)

        except Exception as error:
            print("breaking worker error:", error)

        time.sleep(BREAKING_INTERVAL)


def main():
    app = PoliticalMonitorGUI()

    def _start():
        print("===== START THREAD =====")

        threading.Thread(
            target=breaking_worker,
            args=(app,),
            daemon=True
        ).start()

        print("===== BREAKING WORKER START =====")

        load_initial(app)
        print("===== LOAD END =====")

        threading.Thread(
            target=general_worker,
            args=(app,),
            daemon=True
        ).start()

        print("===== GENERAL WORKER START =====")

    threading.Thread(target=_start, daemon=True).start()

    app.mainloop()


if __name__ == "__main__":
    main()
