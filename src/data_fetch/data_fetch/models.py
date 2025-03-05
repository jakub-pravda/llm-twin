from datetime import datetime

from pydantic import BaseModel


class FetchedData(BaseModel):
    author: str
    content: str
    source: str
    created_at: datetime


class TelegramApiCredentials(BaseModel):
    api_id: str
    api_hash: str
