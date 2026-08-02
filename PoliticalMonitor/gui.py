from datetime import datetime

import customtkinter as ctk
import ctypes

from article_card import ArticleCard
from notifier import get_next_popup, open_article


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PoliticalMonitorGUI(ctk.CTk):
    """Main application window for the political article monitor."""

    NEW_DURATION_MS = 5 * 60 * 1000

    def __init__(self):
        super().__init__()

        self.title("📡 속보단독 레이더 - Mark III")
        self.geometry("1000x760")
        self.minsize(760, 560)

        self.articles = []
        self._new_reset_jobs = {}
        self.auto_focus_breaking = True
        self.unread_breaking = 0

        self._build_ui()
        self.show_loading()
        self._bind_scroll_keys()
        self.popup_windows = []
        self.after(100, self._process_popup_queue)

    def _build_ui(self):
        self.configure(fg_color="#1e1e1e")

        toolbar = ctk.CTkFrame(self, fg_color="#252526", corner_radius=8)
        toolbar.pack(fill="x", padx=12, pady=(12, 8))

        ctk.CTkLabel(
            toolbar,
            text="📡 속보단독 레이더 - Mark III",
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

        self.tabview.set("🚨 속보")

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

        if article.get("type") == "속보" and article.get("new"):
            self.unread_breaking += 1
            if self.auto_focus_breaking:
                try:
                    if self.tabview.get() != "🚨 속보":
                        self.tabview.set("🚨 속보")
                except Exception:
                    pass

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
                f"전체 {len(self.articles)}건 | 🚨 {breaking} | ⭐ {exclusive} | "
                f"📰 {normal} | 🟡 NEW {new_count} | 🔴 미확인 속보 {self.unread_breaking}건"
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
            if self.unread_breaking:
                self.unread_breaking = 0
                self.update_status()
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
            value = (article.get("datetime") or article.get("published_time") or "").strip()

            for fmt in ("%Y-%m-%d %H:%M", "%Y.%m.%d %H:%M"):
                try:
                    return datetime.strptime(value[:16], fmt)
                except (TypeError, ValueError):
                    pass

            try:
                t = datetime.strptime(value, "%H:%M")
                return datetime.combine(datetime.today().date(), t.time())
            except (TypeError, ValueError):
                pass

            return datetime.min

        self.articles.sort(key=sort_key, reverse=True)


    def _process_popup_queue(self):
        article = get_next_popup()
        if article:
            self._show_popup(article)
        self.after(250, self._process_popup_queue)

    def _popup_color(self, media):
        if media == "연합뉴스":
            return "#1f6feb"
        if media == "뉴스1":
            return "#f57c00"
        return "#555555"

    def _show_popup(self, article):
        popup = ctk.CTkToplevel(self)
        popup.withdraw()
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(fg_color=self._popup_color(article.get("media","")))
        width, height = 320, 80
        popup.update_idletasks()
        user32=ctypes.windll.user32
        screen_w=user32.GetSystemMetrics(0)
        x=screen_w-width-150
        gap=36
        y=8+len(self.popup_windows)*(height+gap)
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.deiconify()
        self.popup_windows.append(popup)
        t=ctk.CTkLabel(popup,text=f"🚨 {article.get('media','뉴스')}",font=("맑은 고딕",14,"bold"),text_color="white")
        t.pack(anchor="w",padx=12,pady=(8,2))
        b=ctk.CTkLabel(popup,text=article.get("title",""),justify="left",wraplength=330,fg_color="white",text_color="black",corner_radius=5)
        b.pack(fill="both",expand=True,padx=5,pady=(0,5))
        def open_link(e=None):
            open_article(article)
            close()
        for w in (popup,t,b):
            w.bind("<Button-1>",open_link)
        def fade(alpha=1.0):
            alpha -= 0.03
            if alpha <= 0:
                close()
                return
            try:
                popup.attributes("-alpha", alpha)
                popup.after(16, lambda: fade(alpha))
            except Exception:
                close()
        def close():
            try:
                self.popup_windows.remove(popup)
            except: pass
            try: popup.destroy()
            except: pass
            self._reposition_popups()
        popup.after(4000,fade)

    def _reposition_popups(self):
        width, height = 320, 80
        user32=ctypes.windll.user32
        screen_w=user32.GetSystemMetrics(0)
        x=screen_w-width-150
        gap=36
        for i,p in enumerate(list(self.popup_windows)):
            try:
                p.geometry(f"{width}x{height}+{x}+{8+i*(height+gap)}")
            except Exception:
                pass


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
