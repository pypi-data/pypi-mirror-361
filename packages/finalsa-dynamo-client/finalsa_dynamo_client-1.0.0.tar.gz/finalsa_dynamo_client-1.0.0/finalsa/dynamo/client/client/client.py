from finalsa.dynamo.client.interface import SyncDynamoClient as Interface
from .implementation import DynamoClientImpl as Impl
from typing import List, Dict, Optional, Generator, Any


class SyncDynamoClient(Interface):
    """
    High-level synchronous DynamoDB client.
    
    This client provides a clean, consistent interface for DynamoDB operations
    with improved error handling, pagination support, and modern UpdateExpression syntax.
    """

    def __init__(self, region_name: Optional[str] = None, **kwargs):
        """
        Initialize the sync DynamoDB client.
        
        Args:
            region_name: AWS region name (e.g., 'us-east-1')
            **kwargs: Additional boto3 client configuration options
        """
        self.__client__ = Impl(region_name=region_name, **kwargs)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup if needed."""
        # For sync client, no special cleanup needed, but we could add connection pooling later
        pass

    def write_transaction(self, transactions: List, max_num_transactions: Optional[int] = 99) -> None:
        """
        Execute a write transaction with multiple operations.
        
        Args:
            transactions: List of transaction items
            max_num_transactions: Maximum number of transactions per batch (default: 99)
        """
        return self.__client__.write_transaction(transactions, max_num_transactions)

    def query(self, table_name: str, **kwargs) -> Dict:
        """
        Query items from a table.
        
        Args:
            table_name: Name of the table to query
            **kwargs: Query parameters (KeyConditionExpression, FilterExpression, etc.)
            
        Returns:
            Dict: Query response from DynamoDB
        """
        return self.__client__.query(table_name, **kwargs)

    def put(self, table_name: str, item: Dict) -> None:
        """
        Put an item into a table.
        
        Args:
            table_name: Name of the table
            item: Item to insert (in DynamoDB format)
        """
        return self.__client__.put(table_name, item)

    def delete(self, table_name: str, key: Dict) -> None:
        """
        Delete an item from a table.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item to delete (in DynamoDB format)
        """
        return self.__client__.delete(table_name, key)

    def get(self, table_name: str, key: Dict) -> Dict:
        """
        Get an item from a table.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item to retrieve (in DynamoDB format)
            
        Returns:
            Dict: DynamoDB response (contains 'Item' key if found)
        """
        return self.__client__.get(table_name, key)

    def scan(self, table_name: str, **kwargs) -> Dict:
        """
        Scan items from a table.
        
        Args:
            table_name: Name of the table to scan
            **kwargs: Scan parameters (FilterExpression, Limit, etc.)
            
        Returns:
            Dict: Scan response from DynamoDB
        """
        return self.__client__.scan(table_name, **kwargs)

    def scan_pages(self, table_name: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Scan items from a table with automatic pagination.
        
        This method automatically handles pagination and yields each page of results.
        
        Args:
            table_name: Name of the table to scan
            **kwargs: Scan parameters (FilterExpression, Limit, etc.)
            
        Yields:
            Dict: Each page of scan results
            
        Example:
            for page in client.scan_pages("MyTable"):
                for item in page.get("Items", []):
                    print(item)
        """
        yield from self.__client__.scan_pages(table_name, **kwargs)

    def update(self, table_name: str, key: Dict, update_expression: str, 
               expression_attribute_names: Optional[Dict] = None,
               expression_attribute_values: Optional[Dict] = None) -> Dict:
        """
        Update an item in a table using modern UpdateExpression syntax.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item to update (in DynamoDB format)
            update_expression: UpdateExpression string (e.g., 'SET #n = :val, #c = #c + :inc')
            expression_attribute_names: Mapping for attribute name placeholders (e.g., {'#n': 'name'})
            expression_attribute_values: Mapping for attribute value placeholders (e.g., {':val': {'S': 'John'}})
            
        Returns:
            Dict: Update response with updated attributes
            
        Example:
            client.update(
                "MyTable",
                {"id": {"S": "123"}},
                "SET #n = :name, #c = #c + :inc",
                {"#n": "name", "#c": "count"},
                {":name": {"S": "John"}, ":inc": {"N": "1"}}
            )
        """
        return self.__client__.update(
            table_name, 
            key, 
            update_expression, 
            expression_attribute_names,
            expression_attribute_values
        )

    def batch_get_item(self, request_items: Dict) -> Dict:
        """
        Get multiple items from multiple tables in a single request.
        
        Args:
            request_items: Dict mapping table names to their respective keys
            
        Returns:
            Dict: Response containing retrieved items and any unprocessed keys
            
        Example:
            response = client.batch_get_item({
                "Table1": {
                    "Keys": [{"id": {"S": "1"}}, {"id": {"S": "2"}}]
                },
                "Table2": {
                    "Keys": [{"pk": {"S": "key1"}}]
                }
            })
        """
        return self.__client__.batch_get_item(request_items)

    def batch_write_item(self, request_items: Dict) -> Dict:
        """
        Write multiple items to multiple tables in a single request.
        
        Args:
            request_items: Dict mapping table names to their respective write requests
            
        Returns:
            Dict: Response containing any unprocessed items
            
        Example:
            response = client.batch_write_item({
                "Table1": [
                    {"PutRequest": {"Item": {"id": {"S": "1"}, "name": {"S": "John"}}}},
                    {"DeleteRequest": {"Key": {"id": {"S": "2"}}}}
                ]
            })
        """
        return self.__client__.batch_write_item(request_items)
