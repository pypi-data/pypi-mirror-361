from typing import List, Dict, AsyncGenerator, Any
from finalsa.dynamo.client.interface import AsyncDynamoClient as Interface
from .implementation import DynamoClientTestImpl as Impl


class AsyncDynamoClientTestImpl(Interface):

    def __init__(self):
        self.__impl__ = Impl()

    async def write_transaction(self, transactions: List, max_num_transactions: int = 99) -> None:
        self.__impl__.write_transaction(transactions)

    async def query(self, table_name: str, **kwargs) -> Dict:
        return self.__impl__.query(table_name, **kwargs)

    async def get(self, table_name: str, key: Dict) -> Dict:
        return self.__impl__.get(table_name, key)

    async def put(self, table_name: str, item: Dict) -> None:
        self.__impl__.put(table_name, item)

    async def delete(self, table_name: str, key: Dict) -> None:
        self.__impl__.delete(table_name, key)

    async def scan(self, table_name: str, **kwargs) -> Dict:
        return self.__impl__.scan(table_name, **kwargs)

    async def scan_pages(self, table_name: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Mock implementation of multipage scanning for tests."""
        # For testing, we'll simulate pagination by creating multiple pages
        result = self.__impl__.scan(table_name, **kwargs)
        items = result.get("Items", [])
        
        # Simulate pagination by breaking items into smaller chunks
        page_size = kwargs.get("Limit", 10)
        total_items = len(items)
        
        if total_items == 0:
            yield {"Items": [], "Count": 0, "ScannedCount": 0}
            return
        
        # Create pages
        for i in range(0, total_items, page_size):
            page_items = items[i:i + page_size]
            page_result = {
                "Items": page_items,
                "Count": len(page_items),
                "ScannedCount": len(page_items)
            }
            
            # Add LastEvaluatedKey if there are more items
            if i + page_size < total_items:
                page_result["LastEvaluatedKey"] = {"id": f"page_{i // page_size}"}
            
            yield page_result

    async def update(self, table_name: str, key: Dict, item: Dict) -> Dict:
        return self.__impl__.update(table_name, key, item)

    def clear(self):
        self.__impl__.clear()
