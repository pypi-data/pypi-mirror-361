from .client import SyncDynamoClientTestImpl
from .async_client import AsyncDynamoClientTestImpl
from typing import List, Dict, Union


def seed(
    table: str,
    items: List[Dict],
    client: Union[AsyncDynamoClientTestImpl,
                      SyncDynamoClientTestImpl] = SyncDynamoClientTestImpl()
):
    for item in items:
        client.__impl__.put(TableName=table, item=item)
