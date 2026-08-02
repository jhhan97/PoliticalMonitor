from datetime import datetime

import customtkinter as ctk

from article_card import ArticleCard


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PoliticalMonitorGUI(ctk.CTk):
    """Main application window for the political article monitor."""

    NEW_DURATION_MS = 5 * 60 * 1000

    def __init__(self):
        super().__init__()

        self.title("Political Monitor")
        self.geometry("1000x760")
        self.minsize(760, 560)

        self.articles = []
        self._new_reset_jobs = {}

        self._build_ui()
        self.show_loading()
        self._bind_scroll_keys()

    def _build_ui(self):
        self.configure(fg_color="#1e1e1e")

        toolbar = ctk.CTkFrame(self, fg_color="#252526", corner_radius=8)
        toolbar.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(
            toolbar,
            text="Political Monitor",
            font=("맑은 고딕", 17, "bold"),
        ).pack(side="left", padx=14, pady=10)

        self.last_update_label = ctk.CTkLabel(
            toolbar,
            text="마지막 업데이트: -",
            text_color="#a8a8a8",
        )
        self.last_update_label.pack(side="right", padx=14)

        self.tabview = ctk.CTkTabview(
            self,
            fg_color="#1e1e1e",
            segmented_button_fg_color="#2d2d30",
            segmented_button_selected_color="#0e639c",
            segmented_button_selected_hover_color="#1177bb",
        )
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        self.tabview.add("🚨 속보")
        self.tabview.add("⭐ 단독")
        self.tabview.add("📰 일반")

        self.frames = {
            "속보": self._make_scroll_frame("🚨 속보"),
            "단독": self._make_scroll_frame("⭐ 단독"),
            "일반": self._make_scroll_frame("📰 일반"),
        }

        self.status_label = ctk.CTkLabel(
            self,
            text="전체 0건 | 🚨 0 | ⭐ 0 | 📰 0 | 🟡 NEW 0",
            anchor="w",
            fg_color="#007acc",
            corner_radius=0,
            font=("맑은 고딕", 12),
        )
        self.status_label.pack(fill="x", side="bottom")

    def _make_scroll_frame(self, tab_name):
        tab = self.tabview.tab(tab_name)
        frame = ctk.CTkScrollableFrame(tab, fg_color="#1e1e1e")
        frame.pack(fill="both", expand=True)
        return frame

    def add_article(self, article):
        """Add or update an article, preserving newest-first order."""
        url = article.get("url", "")
        if url:
            self.articles = [item for item in self.articles if item.get("url") != url]

        article.setdefault("type", "일반")
        article.setdefault("new", False)
        self.articles.append(article)
        self._sort_articles()

        if article["new"]:
            self._schedule_new_reset(article)

        self.refresh()

    def clear_articles(self):
        for job_id in self._new_reset_jobs.values():
            try:
                self.after_cancel(job_id)
            except Exception:
                pass
        self._new_reset_jobs.clear()
        self.articles.clear()
        self.refresh()

    def refresh(self):
        for frame in self.frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

        for article in self.articles:
            article_type = article.get("type", "일반")
            target = self.frames.get(article_type, self.frames["일반"])
            card = ArticleCard(target, article, is_new=article.get("new", False))
            card.pack(fill="x", padx=6, pady=5)

        self.last_update_label.configure(
            text=f"마지막 업데이트: {datetime.now():%H:%M:%S}"
        )
        self.hide_loading()
        self.update_status()

    def show_loading(self):
        self.loading_label=ctk.CTkLabel(self,text="기사를 불러오는 중...",font=("맑은 고딕",16,"bold"))
        self.loading_label.place(relx=0.5,rely=0.5,anchor="center")

    def hide_loading(self):
        if hasattr(self,"loading_label"):
            self.loading_label.destroy()

    def update_status(self):
        breaking = sum(item.get("type") == "속보" for item in self.articles)
        exclusive = sum(item.get("type") == "단독" for item in self.articles)
        normal = sum(item.get("type", "일반") == "일반" for item in self.articles)
        new_count = sum(bool(item.get("new")) for item in self.articles)

        self.status_label.configure(
            text=(
                f"전체 {len(self.articles)}건 | "
                f"🚨 {breaking} | ⭐ {exclusive} | 📰 {normal} | 🟡 NEW {new_count}"
            )
        )
        
    def _bind_scroll_keys(self):
        self.bind("<Up>", lambda e: self._scroll_current_tab(-15))
        self.bind("<Down>", lambda e: self._scroll_current_tab(15))

        self.bind("<Prior>", lambda e: self._scroll_current_tab(-18))   # PgUp
        self.bind("<Next>", lambda e: self._scroll_current_tab(18))     # PgDn

        self.bind("<Home>", lambda e: self._scroll_to(0))
        self.bind("<End>", lambda e: self._scroll_to(1))

    def _current_frame(self):
        tab = self.tabview.get()

        if "속보" in tab:
            return self.frames["속보"]

        if "단독" in tab:
            return self.frames["단독"]

        return self.frames["일반"]

    def _scroll_current_tab(self, amount):
        frame = self._current_frame()

        try:
            frame._parent_canvas.yview_scroll(amount, "units")
        except Exception:
            pass

    def _scroll_to(self, where):
        frame = self._current_frame()

        try:
            frame._parent_canvas.yview_moveto(where)
        except Exception:
            pass


    def _schedule_new_reset(self, article):
        key = article.get("url") or str(id(article))
        old_job = self._new_reset_jobs.pop(key, None)
        if old_job:
            try:
                self.after_cancel(old_job)
            except Exception:
                pass

        self._new_reset_jobs[key] = self.after(
            self.NEW_DURATION_MS,
            lambda: self._clear_new_flag(key),
        )

    def _clear_new_flag(self, key):
        self._new_reset_jobs.pop(key, None)
        changed = False

        for article in self.articles:
            article_key = article.get("url") or str(id(article))
            if article_key == key and article.get("new"):
                article["new"] = False
                changed = True
                break

        if changed:
            self.refresh()

    def _sort_articles(self):
        def sort_key(article):
            value = article.get("datetime") or article.get("published_time") or ""
            for fmt in ("%Y-%m-%d %H:%M", "%Y.%m.%d %H:%M"):
                try:
                    return datetime.strptime(value[:16], fmt)
                except (TypeError, ValueError):
                    pass
            return datetime.min

        self.articles.sort(key=sort_key, reverse=True)


if __name__ == "__main__":
    app = PoliticalMonitorGUI()
    app.add_article({
        "media": "뉴스1",
        "type": "속보",
        "title": "[테스트] 새 기사 카드입니다.",
        "url": "https://www.news1.kr",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "new": True,
    })
    app.mainloop()
