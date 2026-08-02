import queue
import webbrowser
import winsound
from pathlib import Path

try:
    from plyer import notification
except Exception:
    notification = None

from config import USE_WINDOWS_NOTIFICATION

# -------------------------------
# 속보 알림음 파일
# 프로젝트/
#   notifier.py
#   sounds/
#       message_ping.wav
# -------------------------------
SOUND_FILE = Path(__file__).parent / "sounds" / "message_ping.wav"

# GUI가 가져갈 큐
popup_queue = queue.Queue()


def notify(article):
    """
    Worker Thread에서 호출.
    GUI Thread가 처리하도록 Queue에 넣기만 한다.
    """
    popup_queue.put(article)
    play_sound(article)


def get_next_popup():
    """
    GUI에서 주기적으로 호출.
    """
    try:
        return popup_queue.get_nowait()
    except queue.Empty:
        return None


def show_windows_notification(article):
    """
    백업용.
    현재는 사용 안 함.
    """
    if not USE_WINDOWS_NOTIFICATION:
        return

    if notification is None:
        return

    try:
        notification.notify(
            title=f"[{article.get('media','뉴스')}]",
            message=article.get("title", ""),
            app_name="속보단독 레이더 - Mark III",
            timeout=5
        )
    except Exception:
        pass


def play_sound(article):
    """
    속보 전용 효과음
    """
    try:
        winsound.PlaySound(
            str(SOUND_FILE),
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )
    except Exception:
        # wav 파일이 없으면 백업으로 기본 비프
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass


def send_telegram(article):
    """
    Mark III.5
    """
    pass


def open_article(article):
    try:
        webbrowser.open(article["url"])
    except Exception:
        pass
