import asyncio
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Coroutine, Optional

import click
from loguru import logger

from data_fetch.constants import DATA_FETCH_DATABASE_NAME
from data_fetch.doc_storage import MongoDocumentStorage
from data_fetch.fetchers.base import BaseDataFetcher, DataFetcherArg
from data_fetch.keystore.azure import AzureKeyStore

DEFAULT_OFFSET_DATE = datetime.now() - timedelta(days=365)  # 1 year


# remark: this decorator serves as a workaround for the fact that click does not support async functions
def async_command(
    f: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.command()
@click.option(
    "--data-fetcher", type=DataFetcherArg, required=True, help="Data fetcher"
)
@click.option("--mongo-host", type=str, help="Mongo host", default="localhost")
@click.option("--mongo-port", type=int, help="Data fetcher", default=27017)
@click.option(
    "--azure-keyvault-name",
    type=str,
    help="Name of the azure keyvault from which to retrieve secrets",
    required=False,
    default=None,
)
@async_command
async def main(
    data_fetcher: DataFetcherArg,
    mongo_host: str,
    mongo_port: int,
    azure_keyvault_name: Optional[str],
) -> None:
    logger.info("Data fetch started")

    maybe_key_store = (
        AzureKeyStore(azure_keyvault_name)
        if azure_keyvault_name is not None
        else None
    )

    data_fetcher_maybe = BaseDataFetcher.get_fetcher_by_arg(
        data_fetcher, maybe_key_store
    )
    doc_storage = MongoDocumentStorage(
        mongo_host, mongo_port, DATA_FETCH_DATABASE_NAME
    )

    if data_fetcher_maybe is None:
        not_registered_data_fetcher_err = (
            f"Data fetcher {data_fetcher} not registered"
        )
        logger.error(not_registered_data_fetcher_err)
        raise ValueError(not_registered_data_fetcher_err)

    last_inserted = doc_storage.get_last_inserted(
        data_fetcher_maybe.FETCHER_NAME
    )
    offset_date = (
        last_inserted.created_at
        if last_inserted is not None
        else DEFAULT_OFFSET_DATE
    )
    logger.info("Starting data fetch from offset date: {}", offset_date)

    fetched_data_iterator_async = data_fetcher_maybe.fetch(offset_date)

    logger.info("Data fetch iterator created")
    await doc_storage.insert(
        fetched_data=fetched_data_iterator_async,
        collection=data_fetcher_maybe.FETCHER_NAME,
    )


if __name__ == "__main__":
    main()
