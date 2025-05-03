from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel
from torch import Tensor

type Embedings = Tensor


class InputDataModel(BaseModel):
    source: str
    created_at: datetime
    content: str


class InputMessagingDataModel(InputDataModel):
    author: str


class CleanedDataModel(InputDataModel):
    cleaned_content: str


class ChunkedDataModel(CleanedDataModel):
    chunks: list[str]


class EmbeddedModel(CleanedDataModel):
    embeddings: list[Embedings]

    def to_payload(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "created_at": self.created_at,
        }
