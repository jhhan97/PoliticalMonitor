PROGRAM_NAME = "속보 단독 체크머신"
VERSION = "3.0"

# =========================
# 정치 키워드
# =========================

KEYWORDS = [
    "민주당",
    "민주",
    "與",
    "국민의힘",
    "野",
    "조국혁신당",
    "선관위",
    "법사위",
    "국회",
]

# =========================
# 기사 분류
# =========================

BREAKING_WORDS = [
    "속보",
]

EXCLUSIVE_WORDS = [
    "단독",
]

# =========================
# 제외 키워드
# =========================

EXCLUDE = [
    "포토",
    "사진",
    "화보",
    "오늘의 운세",
    "주가",
    "사설",
    "칼럼",
]

# =========================
# 우선 언론사
# =========================

PRIORITY_MEDIA = [
    "연합뉴스",
    "뉴스1",
]

# =========================
# 언론사 URL
# =========================

MEDIA = {
    "yonhap": {
        "name": "연합뉴스",
        "url": "https://www.yna.co.kr/politics/all",
    },
    "news1": {
        "name": "뉴스1",
        "url": "https://www.news1.kr/politics",
    },
    "newsis": {
        "name": "뉴시스",
        "url": "https://www.newsis.com/politics",
    },
}

# =========================
# 크롤링 설정
# =========================

GENERAL_INTERVAL = 300      # 일반 기사 (5분)
BREAKING_INTERVAL = 3       # 속보 (3초)

LOOKBACK_MINUTES = 180

# =========================
# 저장 설정
# =========================

MAX_HISTORY = 500

DATABASE = "history.db"

BREAKING_HISTORY = "breaking_history.json"

# =========================
# 알림 설정
# =========================

USE_WINDOWS_NOTIFICATION = True

USE_TELEGRAM = False

TELEGRAM_TOKEN = ""

TELEGRAM_CHAT_ID = ""

# =========================
# 개발 옵션
# =========================

DEBUG = False

# =========================
# HTTP
# =========================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}
