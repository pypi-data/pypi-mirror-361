import boto3
from botocore.exceptions import ClientError
from finalsa.dynamo.client.interface import SyncDynamoClient
from typing import List, Dict, Optional, Generator, Any
import logging

logger = logging.getLogger(__name__)


class DynamoClientImpl(SyncDynamoClient):
    """
    Implementation of DynamoDB client using boto3.
    
    This class provides a high-level interface to DynamoDB operations
    with improved error handling, pagination support, and modern UpdateExpression syntax.
    """

    def __init__(self, region_name: Optional[str] = None, **kwargs):
        """
        Initialize the DynamoDB client.
        
        Args:
            region_name: AWS region name (e.g., 'us-east-1')
            **kwargs: Additional boto3 client configuration options
        """
        config = {}
        if region_name:
            config['region_name'] = region_name
        config.update(kwargs)
        
        self.client = boto3.client("dynamodb", **config)

    def write_transaction(self, transactions: List, max_num_transactions: Optional[int] = 99) -> None:
        """
        Execute write transactions in batches.
        
        Args:
            transactions: List of transaction items
            max_num_transactions: Maximum number of transactions per batch (default: 99, max: 100)
        """
        if not transactions:
            return
            
        # Ensure max_num_transactions doesn't exceed DynamoDB limit
        max_num_transactions = min(max_num_transactions or 99, 100)
        
        grouped_transactions = []
        group = []
        
        for transaction in transactions:
            group.append(transaction)
            if len(group) == max_num_transactions:
                grouped_transactions.append(group.copy())
                group = []
                
        if group:
            grouped_transactions.append(group)
            
        for group in grouped_transactions:
            try:
                self.client.transact_write_items(TransactItems=group)
                logger.debug(f"Successfully executed transaction batch with {len(group)} items")
            except ClientError as e:
                logger.error(f"Transaction failed: {e}")
                raise

    def query(self, table_name: str, **kwargs) -> Dict:
        """Query items from a table."""
        try:
            return self.client.query(TableName=table_name, **kwargs)
        except ClientError as e:
            logger.error(f"Query failed for table {table_name}: {e}")
            raise

    def put(self, table_name: str, item: Dict) -> None:
        """Put an item into a table."""
        try:
            self.client.put_item(TableName=table_name, Item=item)
            logger.debug(f"Successfully put item in table {table_name}")
        except ClientError as e:
            logger.error(f"Put failed for table {table_name}: {e}")
            raise

    def get(self, table_name: str, key: Dict) -> Dict:
        """Get an item from a table, returning the full response."""
        try:
            return self.client.get_item(TableName=table_name, Key=key)
        except ClientError as e:
            logger.error(f"Get failed for table {table_name}: {e}")
            raise

    def delete(self, table_name: str, key: Dict) -> None:
        """Delete an item from a table."""
        try:
            self.client.delete_item(TableName=table_name, Key=key)
            logger.debug(f"Successfully deleted item from table {table_name}")
        except ClientError as e:
            logger.error(f"Delete failed for table {table_name}: {e}")
            raise

    def scan(self, table_name: str, **kwargs) -> Dict:
        """Scan items from a table."""
        try:
            return self.client.scan(TableName=table_name, **kwargs)
        except ClientError as e:
            logger.error(f"Scan failed for table {table_name}: {e}")
            raise

    def scan_pages(self, table_name: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Scan items from a table with automatic pagination.
        
        Yields each page of results until all items are scanned.
        
        Args:
            table_name: Name of the table to scan
            **kwargs: Additional scan parameters
            
        Yields:
            Dict: Each page of scan results
        """
        scan_kwargs = kwargs.copy()
        
        while True:
            try:
                response = self.client.scan(TableName=table_name, **scan_kwargs)
                yield response
                
                # Check if there are more items to scan
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
                    
                # Set up for next page
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
                
            except ClientError as e:
                logger.error(f"Scan page failed for table {table_name}: {e}")
                raise

    def update(self, table_name: str, key: Dict, update_expression: str, 
               expression_attribute_names: Optional[Dict] = None,
               expression_attribute_values: Optional[Dict] = None) -> Dict:
        """
        Update an item using UpdateExpression syntax.
        
        Args:
            table_name: Name of the table
            key: Primary key of the item to update
            update_expression: UpdateExpression string (e.g., 'SET #n = :val')
            expression_attribute_names: Mapping of attribute name placeholders
            expression_attribute_values: Mapping of attribute value placeholders
            
        Returns:
            Dict: Response from DynamoDB including updated attributes
        """
        update_kwargs = {
            'TableName': table_name,
            'Key': key,
            'UpdateExpression': update_expression,
            'ReturnValues': 'ALL_NEW'  # Return all updated attributes
        }
        
        if expression_attribute_names:
            update_kwargs['ExpressionAttributeNames'] = expression_attribute_names
            
        if expression_attribute_values:
            update_kwargs['ExpressionAttributeValues'] = expression_attribute_values
            
        try:
            return self.client.update_item(**update_kwargs)
        except ClientError as e:
            logger.error(f"Update failed for table {table_name}: {e}")
            raise

    def batch_get_item(self, request_items: Dict) -> Dict:
        """
        Get multiple items from multiple tables in a single request.
        
        Args:
            request_items: Dict mapping table names to their respective keys
            
        Returns:
            Dict: Response containing retrieved items and any unprocessed keys
        """
        try:
            return self.client.batch_get_item(RequestItems=request_items)
        except ClientError as e:
            logger.error(f"Batch get item failed: {e}")
            raise

    def batch_write_item(self, request_items: Dict) -> Dict:
        """
        Write multiple items to multiple tables in a single request.
        
        Args:
            request_items: Dict mapping table names to their respective write requests
            
        Returns:
            Dict: Response containing any unprocessed items
        """
        try:
            return self.client.batch_write_item(RequestItems=request_items)
        except ClientError as e:
            logger.error(f"Batch write item failed: {e}")
            raise
