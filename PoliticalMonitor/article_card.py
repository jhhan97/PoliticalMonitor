import webbrowser

import customtkinter as ctk


class ArticleCard(ctk.CTkFrame):
    """A compact article card with a temporary visual treatment for new items."""

    NORMAL_COLOR = "#252526"
    NEW_COLOR = "#403a20"
    FLASH_COLOR = "#5c5120"

    def __init__(self, master, article, is_new=False):
        self.article = article
        self.is_new = is_new

        super().__init__(
            master,
            corner_radius=9,
            fg_color=self.NEW_COLOR if is_new else self.NORMAL_COLOR,
            border_width=1,
            border_color="#6a5d1d" if is_new else "#3c3c3c",
        )

        self._build()
        self._bind_open(self)

        if is_new:
            self.after(80, self._play_new_animation)

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(9, 3))

        if self.is_new:
            self.new_label = ctk.CTkLabel(
                header,
                text="NEW",
                fg_color="#ffd600",
                text_color="#1b1b1b",
                corner_radius=5,
                font=("맑은 고딕", 11, "bold"),
                padx=8,
                pady=2,
            )
            self.new_label.pack(side="left", padx=(0, 6))
            self._bind_open(self.new_label)

        article_type = self.article.get("type", "일반")
        type_color = {
            "속보": "#d32f2f",
            "단독": "#b8860b",
            "일반": "#4b5563",
        }.get(article_type, "#4b5563")

        type_label = ctk.CTkLabel(
            header,
            text=article_type,
            fg_color=type_color,
            corner_radius=5,
            font=("맑은 고딕", 11, "bold"),
            padx=8,
            pady=2,
        )
        type_label.pack(side="left", padx=(0, 6))
        self._bind_open(type_label)

        media = self.article.get("media", "뉴스")
        media_color = {
            "뉴스1": "#f57c00",
            "연합뉴스": "#1976d2",
        }.get(media, "#616161")

        media_label = ctk.CTkLabel(
            header,
            text=media,
            fg_color=media_color,
            corner_radius=5,
            font=("맑은 고딕", 11, "bold"),
            padx=8,
            pady=2,
        )
        media_label.pack(side="left")
        self._bind_open(media_label)

        datetime_label = ctk.CTkLabel(
            header,
            text=self.article.get("datetime", ""),
            text_color="#b5b5b5",
            font=("맑은 고딕", 11),
        )
        datetime_label.pack(side="right")
        self._bind_open(datetime_label)

        title_label = ctk.CTkLabel(
            self,
            text=self.article.get("title", ""),
            anchor="w",
            justify="left",
            wraplength=820,
            font=("맑은 고딕", 14, "bold"),
        )
        title_label.pack(fill="x", padx=12, pady=(3, 10))
        self._bind_open(title_label)

    def _play_new_animation(self):
        """A short, non-blocking highlight pulse for a newly inserted card."""
        if not self.winfo_exists():
            return

        self.configure(fg_color=self.FLASH_COLOR, border_color="#ffd600")
        self.after(170, self._restore_new_color)

    def _restore_new_color(self):
        if self.winfo_exists():
            self.configure(fg_color=self.NEW_COLOR, border_color="#6a5d1d")

    def _bind_open(self, widget):
        widget.bind("<Double-Button-1>", self._open_article)
        widget.bind("<Enter>", lambda _event: self._hover(True))
        widget.bind("<Leave>", lambda _event: self._hover(False))
        try:
            widget.configure(cursor="hand2")
        except Exception:
            pass

    def _hover(self, entering):
        if not self.winfo_exists():
            return

        if entering:
            self.configure(
                border_color="#d7ba7d",
                fg_color="#4a4325" if self.is_new else "#313131"
            )
        else:
            self.configure(
                border_color="#6a5d1d" if self.is_new else "#3c3c3c",
                fg_color=self.NEW_COLOR if self.is_new else self.NORMAL_COLOR
            )

    def _open_article(self, _event=None):
        url = self.article.get("url")
        if not url:
            return

        original = self.NEW_COLOR if self.is_new else self.NORMAL_COLOR
        self.configure(fg_color="#3a3a3a")

        def _finish():
            if self.winfo_exists():
                self.configure(fg_color=original)
            webbrowser.open(url)

        self.after(100, _finish)
