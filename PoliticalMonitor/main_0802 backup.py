import threading
import time

from config import CHECK_INTERVAL
from breaking_engine import get_breaking_articles
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

        time.sleep(CHECK_INTERVAL)



def breaking_worker(app):
    """속보 전용 Worker"""

    import random

    print("===== BREAKING WORKER RUNNING =====")

    while True:
        try:
            articles = get_breaking_articles()

            if articles:
                print(f"[속보] 새 기사 {len(articles)}건")

            for article in articles:
                article["new"] = True
                app.after(0, lambda item=article: app.add_article(item))
                notify(article)

        except Exception as error:
            print("breaking worker error:", error)

        time.sleep(random.uniform(2.8, 3.3))


def main():
    app = PoliticalMonitorGUI()

    def _start():
        print("===== START THREAD =====")
        load_initial(app)
        print("===== LOAD END =====")
        threading.Thread(target=general_worker, args=(app,), daemon=True).start()
        threading.Thread(target=breaking_worker, args=(app,), daemon=True).start()
        print("===== GENERAL WORKER START =====")
        print("===== BREAKING WORKER START =====")
    threading.Thread(target=_start, daemon=True).start()

    app.mainloop()


if __name__ == "__main__":
    main()
