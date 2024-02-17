import json
import shutil
import threading
from datetime import datetime
from pathlib import Path

from data.base import DataManager
from data.user import User


FILENAME = "data.json"
FILE_LOCK = threading.Lock()


class JsonManager(DataManager):

    file_lock = FILE_LOCK

    def __init__(self, path: Path | str):
        if isinstance(path, str):
            path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        main_file = path / FILENAME
        if not main_file.exists():
            with main_file.open("w") as f:
                json.dump({}, f)
        self.path = path
        self.file = main_file

    def subscribe_user(self, user: User) -> None:
        with self.file_lock:
            with self.file.open("r") as f:
                data = json.load(f)
                if data.get(user.user_id):
                    # Already subscribed
                    return
                data[user.user_id] = user.model_dump()
            with self.file.open("w") as f:
                json.dump(data, f, indent=2)

    def unsubscribe_user(self, user_id: str) -> None:
        with self.file_lock:
            with self.file.open("r") as f:
                data = json.load(f)
                try:
                    del data[user_id]
                except KeyError:
                    pass
            with self.file.open("w") as f:
                json.dump(data, f, indent=2)

    def backup(self) -> None:
        with self.file_lock:
            shutil.copy(
                self.file,
                self.path / f"{FILENAME}.bak-{datetime.now().strftime('%Y%m%d-%H%M')}",
            )

    def get_users(self) -> list[User]:
        with self.file_lock:
            with self.file.open("r") as f:
                data = json.load(f)
                return [User(**u) for u in data.values()]

    def get(self, user_id: str) -> User:
        with self.file_lock:
            with self.file.open("r") as f:
                return User(**json.load(f).get(user_id))

    def save(self, user: User) -> None:
        with self.file_lock:
            with self.file.open("r") as f:
                data = json.load(f)
                data[user.user_id] = user.model_dump()
            with self.file.open("w") as f:
                json.dump(data, f, indent=2)

    def __getitem__(self, user_id: str) -> User:
        with self.file_lock:
            with self.file.open("r") as f:
                return User(**(json.load(f)[user_id]))

    def save_all(self, users: list[User]) -> None:
        with self.file_lock:
            data = {user.user_id: user.model_dump() for user in users}
            with self.file.open("r") as f:
                local_users = json.load(f)
                local_users.update(data)
            with self.file.open("w") as f:
                json.dump(local_users, f, indent=2)
