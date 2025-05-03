import os

from loguru import logger

from data_fetch.keystore.base import BaseKeyStore
from data_fetch.models import TelegramApiCredentials


class EnvKeyStore(BaseKeyStore):
    logger.info("Using EnvKeyStore as keystore")

    def telegram_api_credentials(self) -> TelegramApiCredentials:
        logger.info(
            "Retrieving Telegram API credentials from environment variables"
        )

        api_id_env = os.getenv("TELEGRAM_API_ID", None)
        if api_id_env is None:
            raise ValueError("TELEGRAM_API_ID is not set")

        api_hash_env = os.getenv("TELEGRAM_API_HASH", None)
        if api_hash_env is None:
            raise ValueError("TELEGRAM_API_HASH is not set")

        return TelegramApiCredentials(api_id=api_id_env, api_hash=api_hash_env)
