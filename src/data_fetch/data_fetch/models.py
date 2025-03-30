from datetime import datetime

from pydantic import BaseModel


class FetchedData(BaseModel):
    source: str
    created_at: datetime

class TelegramFetchedData(FetchedData):
    author: str
    content: str

class DummyFetchedData(FetchedData):
    dummy_content: str

class TelegramApiCredentials(BaseModel):
    api_id: str
    api_hash: str
