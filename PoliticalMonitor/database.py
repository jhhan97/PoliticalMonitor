import sqlite3
from config import DATABASE, MAX_HISTORY


class HistoryDB:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS history(
                url TEXT PRIMARY KEY,
                title TEXT,
                media TEXT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def exists(self, url):
        self.cur.execute(
            "SELECT 1 FROM history WHERE url=?",
            (url,)
        )
        return self.cur.fetchone() is not None

    def add(self, title, media, url):
        try:
            self.cur.execute(
                "INSERT INTO history(title, media, url) VALUES(?,?,?)",
                (title, media, url)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass

        self.cleanup()

    def cleanup(self):
        self.cur.execute("SELECT COUNT(*) FROM history")
        count = self.cur.fetchone()[0]

        if count <= MAX_HISTORY:
            return

        remove = count - MAX_HISTORY

        self.cur.execute("""
            DELETE FROM history
            WHERE rowid IN (
                SELECT rowid
                FROM history
                ORDER BY created ASC
                LIMIT ?
            )
        """, (remove,))

        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = HistoryDB()
    print("DB 생성 완료")
    db.close()
