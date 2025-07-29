from typing import List, Dict, Optional, Generator, Any
from finalsa.dynamo.client.interface import SyncDynamoClient as Interface
from .implementation import DynamoClientTestImpl as Impl


class SyncDynamoClientTestImpl(Interface):

    def __init__(self):
        self.__impl__ = Impl()

    def write_transaction(self, transactions: List, max_num_transactions: Optional[int] = 99) -> None:
        grouped_transactions = []
        group = []
        count = 0
        while len(transactions) > 0:
            group.append(transactions.pop(0))
            count += 1
            if count == max_num_transactions:
                grouped_transactions.append(group.copy())
                group = []
                count = 0
        if len(group) > 0:
            grouped_transactions.append(group)
        for group in grouped_transactions:
            self.__impl__.write_transaction(group)

    def query(self, table_name: str, **kwargs):
        return self.__impl__.query(table_name, **kwargs)

    def get(self, table_name: str, key: Dict) -> Dict:
        return self.__impl__.get(table_name, key)

    def put(self, table_name: str, item: Dict) -> None:
        self.__impl__.put(table_name, item)

    def delete(self, table_name: str, key: Dict) -> None:
        self.__impl__.delete(table_name, key)

    def scan(self, table_name: str, **kwargs) -> Dict:
        return self.__impl__.scan(table_name, **kwargs)

    def scan_pages(self, table_name: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Mock implementation of multipage scanning for tests."""
        # For testing, we'll simulate pagination by breaking items into smaller chunks
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

    def update(self, table_name: str, key: Dict, update_expression: str, 
               expression_attribute_names: Optional[Dict] = None,
               expression_attribute_values: Optional[Dict] = None) -> Dict:
        """
        Update method that supports both old and new signatures for backwards compatibility.
        """
        return self.__impl__.update(
            table_name, 
            key, 
            update_expression, 
            expression_attribute_names, 
            expression_attribute_values
        )

    def batch_get_item(self, request_items: Dict) -> Dict:
        """Mock implementation of batch get item for tests."""
        responses = {"Responses": {}}
        
        for table_name, request in request_items.items():
            items = []
            for key in request.get("Keys", []):
                item = self.__impl__.get(table_name, key)
                if item:
                    items.append(item)
            responses["Responses"][table_name] = items
            
        return responses

    def batch_write_item(self, request_items: Dict) -> Dict:
        """Mock implementation of batch write item for tests."""
        for table_name, requests in request_items.items():
            for request in requests:
                if "PutRequest" in request:
                    self.__impl__.put(table_name, request["PutRequest"]["Item"])
                elif "DeleteRequest" in request:
                    self.__impl__.delete(table_name, request["DeleteRequest"]["Key"])
                    
        return {"UnprocessedItems": {}}
    
    def clear(self):
        self.__impl__.clear()


def seed(table: str, items: List[Dict], client: Optional[SyncDynamoClientTestImpl] = None):
    if client is None:
        client = SyncDynamoClientTestImpl()
    for item in items:
        client.put(table, item)
