from abc import ABC, abstractmethod

from data_fetch.models import TelegramApiCredentials


class BaseKeyStore(ABC):
    @abstractmethod
    def telegram_api_credentials(self) -> TelegramApiCredentials:
        pass