from abc import ABC, abstractmethod

from data.user import User


class DataManager(ABC):
    @abstractmethod
    def subscribe_user(self, user: User) -> bool:
        pass

    @abstractmethod
    def unsubscribe_user(self, user_id: str) -> None:
        pass

    @abstractmethod
    def backup(self) -> None:
        pass

    @abstractmethod
    def get_users(self) -> list[User]:
        pass

    @abstractmethod
    def get(self, user_id: str) -> User:
        pass

    @abstractmethod
    def __getitem__(self, user_id: str) -> User:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass
