from datetime import datetime

from pydantic import BaseModel, Field


class FetchedData(BaseModel):
    source: str
    created_at: datetime
    content: str


class TelegramFetchedData(FetchedData):
    author: str
    source: str = Field(default="telegram")


class DummyFetchedData(FetchedData):
    source: str = Field(default="dummy")


class TelegramApiCredentials(BaseModel):
    api_id: str
    api_hash: str
