from finalsa.dynamo.client.interface import AsyncDynamoClient as Interface
from typing import List, Dict, AsyncGenerator, Any, Optional
from .implementation import DynamoClientImpl as Impl
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor


class AsyncDynamoClient(Interface):

    def __init__(self, max_workers: Optional[int] = None):
        self.__client__ = Impl()
        self.__executor__ = ThreadPoolExecutor(max_workers=max_workers)

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool executor."""
        loop = asyncio.get_event_loop()
        partial_func = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(self.__executor__, partial_func)

    async def write_transaction(self, transactions: List, max_num_transactions: int = 99) -> None:
        await self._run_in_executor(
            self.__client__.write_transaction, 
            transactions, 
            max_num_transactions
        )

    async def query(self, table_name: str, **kwargs) -> Dict:
        return await self._run_in_executor(
            self.__client__.query, 
            table_name, 
            **kwargs
        )

    async def put(self, table_name: str, item: Dict) -> None:
        await self._run_in_executor(
            self.__client__.put, 
            table_name, 
            item
        )

    async def delete(self, table_name: str, key: Dict) -> None:
        await self._run_in_executor(
            self.__client__.delete, 
            table_name, 
            key
        )

    async def get(self, table_name: str, key: Dict) -> Dict:
        return await self._run_in_executor(
            self.__client__.get, 
            table_name, 
            key
        )

    async def scan(self, table_name: str, **kwargs) -> Dict:
        return await self._run_in_executor(
            self.__client__.scan, 
            table_name, 
            **kwargs
        )

    async def scan_pages(self, table_name: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Scan a table with multipage support using async generator.
        Yields each page of results as they become available.
        
        Usage:
            async for page in client.scan_pages("MyTable"):
                for item in page.get("Items", []):
                    # Process each item
                    pass
        """
        last_evaluated_key = None
        
        while True:
            scan_kwargs = kwargs.copy()
            if last_evaluated_key:
                scan_kwargs["ExclusiveStartKey"] = last_evaluated_key
            
            # Run the scan operation in the thread pool
            response = await self._run_in_executor(
                self.__client__.scan,
                table_name,
                **scan_kwargs
            )
            
            yield response
            
            # Check if there are more pages
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

    async def update(self, table_name: str, key: Dict, update_expression: str, 
                     expression_attribute_names: Optional[Dict] = None,
                     expression_attribute_values: Optional[Dict] = None) -> Dict:
        return await self._run_in_executor(
            self.__client__.update, 
            table_name, 
            key, 
            update_expression,
            expression_attribute_names,
            expression_attribute_values
        )

    def close(self):
        """Close the thread pool executor."""
        self.__executor__.shutdown(wait=True)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.close()
