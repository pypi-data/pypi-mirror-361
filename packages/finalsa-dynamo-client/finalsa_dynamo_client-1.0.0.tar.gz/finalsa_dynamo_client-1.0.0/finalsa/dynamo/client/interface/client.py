from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Generator, Any


class SyncDynamoClient(ABC):

    @abstractmethod
    def write_transaction(self, transactions: List, max_num_transactions: int = 99) -> None:
        """Execute a write transaction with multiple operations."""
        pass

    @abstractmethod
    def query(self, table_name: str, **kwargs) -> Dict:
        """Query items from a table."""
        pass

    @abstractmethod
    def put(self, table_name: str, item: Dict) -> None:
        """Put an item into a table."""
        pass

    @abstractmethod
    def delete(self, table_name: str, key: Dict) -> None:
        """Delete an item from a table."""
        pass

    @abstractmethod
    def scan(self, table_name: str, **kwargs) -> Dict:
        """Scan items from a table."""
        pass

    @abstractmethod
    def scan_pages(self, table_name: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Scan items from a table with pagination support."""
        pass

    @abstractmethod
    def get(self, table_name: str, key: Dict) -> Dict:
        """Get an item from a table."""
        pass

    @abstractmethod
    def update(self, table_name: str, key: Dict, update_expression: str, 
               expression_attribute_names: Optional[Dict] = None,
               expression_attribute_values: Optional[Dict] = None) -> Dict:
        """Update an item in a table using UpdateExpression."""
        pass

    @abstractmethod
    def batch_get_item(self, request_items: Dict) -> Dict:
        """Get multiple items from multiple tables in a single request."""
        pass

    @abstractmethod
    def batch_write_item(self, request_items: Dict) -> Dict:
        """Write multiple items to multiple tables in a single request."""
        pass
