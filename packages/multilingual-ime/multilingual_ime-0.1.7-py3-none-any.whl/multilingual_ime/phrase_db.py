import threading
from pathlib import Path

import sqlite3


class PhraseDataBase:
    def __init__(self, db_path: str) -> None:
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database file {db_path} not found")

        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._cursor = self._conn.cursor()
        self._lock = threading.Lock()

    def __del__(self) -> None:
        self._conn.commit()
        self._conn.close()

    def create_phrase_table_table(self) -> None:
        with self._lock:
            self._cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS phrase_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    initial_word TEXT,
                    phrase TEXT,
                    frequency INTEGER
                )
                """
            )

            self._cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS index_initial_word ON phrase_table (initial_word)"""
            )
            self._conn.commit()

    def getphrase(self, phrase: str) -> list[tuple[str, int]]:
        with self._lock:
            self._cursor.execute(
                "SELECT phrase FROM phrase_table WHERE phrase = ?", (phrase,)
            )
            return [row[0] for row in self._cursor.fetchall()]

    def get_phrase_with_prefix(self, prefix: str) -> list[tuple[str, int]]:
        if not prefix:
            return []
        with self._lock:
            self._cursor.execute(
                "SELECT initial_word, phrase, frequency FROM phrase_table WHERE initial_word = ?", (prefix,)
            )
            return [
                (phrase, frequency)
                for (initial_word, phrase, frequency) in self._cursor.fetchall()
            ]

    def insert(self, phrase: str, frequency: int) -> None:
        if not self.getphrase(phrase):
            with self._lock:
                self._cursor.execute(
                    "INSERT INTO phrase_table (phrase, frequency) VALUES (?, ?))", (phrase, frequency)
                )
                self._conn.commit()

    def update(self, phrase: str, frequency: int) -> None:
        if not self.getphrase(phrase):
            self.insert(phrase, frequency)

        with self._lock:
            self._cursor.execute(
                "UPDATE phrase_table SET frequency = ? WHERE phrase = ?", (frequency, phrase)
            )
            self._conn.commit()

    def delete(self, phrase: str) -> None:
        with self._lock:
            self._cursor.execute("DELETE FROM phrase_table WHERE phrase = ?", (phrase,))
            self._conn.commit()

    def increment_frequency(self, phrase: str) -> None:
        with self._lock:
            self._cursor.execute(
                "UPDATE phrase_table SET frequency = frequency + 1 WHERE phrase = ?", (phrase,)
            )
            self._conn.commit()


if __name__ == "__main__":
    db_path = Path(__file__).parent / "src" / "chinese_phrase.db"
    db = PhraseDataBase(db_path)
    db.create_phrase_table_table()
