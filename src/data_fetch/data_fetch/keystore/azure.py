import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from loguru import logger

from data_fetch.keystore.base import BaseKeyStore
from data_fetch.models import TelegramApiCredentials


class AzureKeyStore(BaseKeyStore):
    logger.info("Using Azure keyvault as keystore")
    
    TELEGRAM_API_HASH_SECRET_NAME = "telegram-api-hash"
    TELEGRAM_API_ID_SECRET_NAME = "telegram-api-id"

    def __init__(self, key_vault_name: str):
        self.key_vault_name = key_vault_name
        self.key_vault_url = f"https://{key_vault_name}.vault.azure.net"
        self.client = SecretClient(vault_url=self.key_vault_url, credential=DefaultAzureCredential())

    def telegram_api_credentials(self) -> TelegramApiCredentials:
        logger.info("Retrieving Telegram API credentials from azure keyvault")

        api_id = self.client.get_secret(self.TELEGRAM_API_ID_SECRET_NAME).value
        if api_id is None:
            raise ValueError(f"{self.TELEGRAM_API_ID_SECRET_NAME} secret is not set")

        api_hash = self.client.get_secret(self.TELEGRAM_API_HASH_SECRET_NAME).value
        if api_hash is None:
            raise ValueError(f"{self.TELEGRAM_API_HASH_SECRET_NAME} secret is not set")
        
        logger.info("Telegram API credentials successfully retrieved from azure keyvault")
        return TelegramApiCredentials(api_id=api_id, api_hash=api_hash)