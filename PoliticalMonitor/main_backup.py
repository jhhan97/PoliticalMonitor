import threading
import time

from config import CHECK_INTERVAL
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


def worker(app):
    """Add and notify only genuinely newly detected articles."""
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


def main():
    app = PoliticalMonitorGUI()

    threading.Thread(target=load_initial, args=(app,), daemon=True).start()
    def _start():
        load_initial(app)
        threading.Thread(target=worker,args=(app,),daemon=True).start()
    threading.Thread(target=_start,daemon=True).start()

    app.mainloop()


if __name__ == "__main__":
    main()
