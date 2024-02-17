import json
import sqlite3
import threading
from typing import Optional

from data.base import DataManager
from data.user import User


class SQLiteManager(DataManager):

    _local = threading.local()

    def _initialize_thread_local_connection(self):
        if not hasattr(SQLiteManager._local, "conn"):
            SQLiteManager._local.conn = sqlite3.connect(
                self.path, check_same_thread=False
            )
            SQLiteManager._local.path = self.path
            self.create_table_if_not_exists()

    def get_thread_local_connection(self):
        if (
            not hasattr(SQLiteManager._local, "conn")
            or SQLiteManager._local.conn is None
        ):
            SQLiteManager._local.conn = sqlite3.connect(
                self.path, check_same_thread=False
            )
        return SQLiteManager._local.conn

    def __init__(self, path: str):
        self.path = path
        self._initialize_thread_local_connection()

    def create_table_if_not_exists(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                token TEXT,
                config TEXT,
                notifications TEXT
            )
        """
        )
        self.conn.commit()

    @property
    def conn(self):
        return self.get_thread_local_connection()

    def subscribe_user(self, user: User) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, token, config, notifications) VALUES (?, ?, ?, ?, ?)",
            (
                user.user_id,
                user.username,
                user.token,
                user.config.model_dump_json(),
                json.dumps([n.model_dump() for n in user.notifications]),
            ),
        )
        self.conn.commit()

    def unsubscribe_user(self, user_id: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def backup(self) -> None:
        # Perform backup operation as per your requirements
        pass

    def get_users(self) -> list[User]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id, username, token, config, notifications FROM users"
        )
        rows = cursor.fetchall()
        users = []
        for row in rows:
            user = User(
                user_id=row[0],
                username=row[1],
                token=row[2],
                config=json.loads(row[3]),
                notifications=json.loads(row[4]),
            )
            users.append(user)
        return users

    def get(self, user_id: str) -> Optional[User]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT username, token, config, notifications FROM users WHERE user_id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return User(
                user_id=user_id,
                username=row[0],
                token=row[1],
                config=json.loads(row[2]),
                notifications=json.loads(row[3]),
            )
        return None

    def save(self, user: User) -> None:
        cursor = self.conn.cursor()
        self.insert_or_replace_user(cursor, user)
        self.conn.commit()

    def __getitem__(self, user_id: str) -> User:
        user = self.get(user_id)
        if user is None:
            raise KeyError(f"User with user_id {user_id} not found")
        return user

    def save_all(self, users: list[User]) -> None:
        cursor = self.conn.cursor()
        for user in users:
            self.insert_or_replace_user(cursor, user)
        self.conn.commit()

    @staticmethod
    def insert_or_replace_user(cursor, user):
        cursor.execute(
            "REPLACE INTO users (user_id, username, token, config, notifications) VALUES (?, ?, ?, ?, ?)",
            (
                user.user_id,
                user.username,
                user.token,
                user.config.model_dump_json(),
                json.dumps([n.model_dump() for n in user.notifications], default=str),
            ),
        )
