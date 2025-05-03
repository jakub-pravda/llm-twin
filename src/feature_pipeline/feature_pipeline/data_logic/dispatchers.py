from abc import ABC, abstractmethod
from typing import Any, List

from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from loguru import logger
from sentence_transformers import SentenceTransformer
from torch import Tensor

from feature_pipeline.models.data_model import (
    ChunkedDataModel,
    CleanedDataModel,
    EmbeddedModel,
    Embedings,
    InputDataModel,
    InputMessagingDataModel,
)


class InputMessageFactory:
    # TODO don't use any, use TypeVar!
    def create_input_message(self, message: dict[str, Any]) -> InputDataModel:
        match message.get("src"):
            case "telegram":
                logger.debug("Handling incomming telegram message {}", message)
                return InputMessagingDataModel.validate(message)
            case _:
                logger.debug("Handling incomming message {}", message)
                return InputDataModel.validate(message)


class InputDataCleaningHandler:
    def clean(self, data_model: InputDataModel) -> CleanedDataModel:
        # TODO - is some cleaning needed? Maybe it depends on used model
        logger.info("Cleaned data handler {}", data_model)
        cleaned_model = CleanedDataModel(
            **data_model.model_dump(), cleaned_content=data_model.content
        )
        return cleaned_model


class ChunkingDataHandler:
    def __init__(
        self, embedding_model_id: str, embedding_model_max_input_length: int
    ) -> None:
        if not embedding_model_id:
            raise ValueError("Embedding id must be defined")
        if embedding_model_max_input_length < 0:
            raise ValueError(
                "Embedding model max input length must be 0 or positive number"
            )

        self.embeding_model_id = embedding_model_id
        self.embeding_model_max_input_length = embedding_model_max_input_length

    def __chunk(self, text: str) -> list[str]:
        logger.debug("Chunking following text: {}", text)
        character_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n"], chunk_size=500, chunk_overlap=0
        )
        text_split = character_splitter.split_text(text)

        # Check if each chunk fits required embedding model
        token_splitter = SentenceTransformersTokenTextSplitter(
            chunk_overlap=50,
            tokens_per_chunk=self.embeding_model_max_input_length,
            model_name=self.embeding_model_id,
        )

        chunks = []
        for section in text_split:
            chunks.extend(token_splitter.split_text(section))

        logger.debug("Returning following chunks: {}", chunks)
        return chunks

    def chunk_data_model(
        self, data_model: CleanedDataModel
    ) -> ChunkedDataModel:
        chunks = self.__chunk(data_model.cleaned_content)
        return ChunkedDataModel(**data_model.model_dump(), chunks=chunks)


class EmbedingFactory:
    def __init__(self) -> None:
        self.text_embeddings = EmbeddingTextDataHandler()

    # TODO better to use factory pattern
    def create(self, input: ChunkedDataModel) -> EmbeddedModel:
        match input.source:
            # TODO more embedings model will follow
            case _:
                embeddings: List[Embedings] = []
                for chunk in input.chunks:
                    embedding = self.text_embeddings.embedd(chunk)
                    # basically every embedding has it's own chunk
                    embeddings.append(embedding)
                return EmbeddedModel(
                    **input.model_dump(), embeddings=embeddings
                )


class EmbeddingDataHandler(ABC):
    model: Any

    @abstractmethod
    def embedd(self, text: str) -> Tensor:
        pass


class EmbeddingTextDataHandler(EmbeddingDataHandler):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def embedd(self, text: str) -> Tensor:
        logger.debug("Processing text embedding on text: {}", text)
        return self.model.encode(text)
