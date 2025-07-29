from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Any, Optional


class AsyncDynamoClient(ABC):

    @abstractmethod
    async def write_transaction(self, transactions: List, max_num_transactions: int = 99) -> None:
        pass

    @abstractmethod
    async def query(self, table_name: str, **kwargs) -> Dict:
        pass

    @abstractmethod
    async def put(self, table_name: str, item: Dict) -> None:
        pass

    @abstractmethod
    async def delete(self, table_name: str, key: Dict) -> None:
        pass

    @abstractmethod
    async def scan(self, table_name: str, **kwargs) -> Dict:
        pass

    @abstractmethod
    def scan_pages(self, table_name: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Scan with multipage support using async generator"""
        pass

    @abstractmethod
    async def get(self, table_name: str, key: Dict) -> Dict:
        pass

    @abstractmethod
    async def update(self, table_name: str, key: Dict, update_expression: str, 
                     expression_attribute_names: Optional[Dict] = None,
                     expression_attribute_values: Optional[Dict] = None) -> Dict:
        pass
