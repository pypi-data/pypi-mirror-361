from typing import List, Dict, Optional, Union, Any, Generator
from finalsa.dynamo.client.interface import SyncDynamoClient as Interface


def is_equal(item: Dict, key: Dict):
    for k, v in key.items():
        if item.get(k) != v:
            return False
    return True


def eval_expressions(item, filters, actions):
    for filter in filters:
        if filter[0] in actions and filter[1]['key'] in item:
            action_eval = actions[filter[0]](
                item[filter[1]['key']], filter[1]['value'])
            if not action_eval:
                return False
    return True


def get_key_from_dict(a: Dict) -> Dict:
    if 'Put' in a:
        table_name = a['Put']['TableName']
        item = a['Put']['Item']
    elif 'Update' in a:
        table_name = a['Update']['TableName']
        item = a['Update']['Key']
    elif 'Delete' in a:
        table_name = a['Delete']['TableName']
        item = a['Delete']['Key']
    else:
        return {}
    
    result = {'TableName': table_name}
    if 'PK' in item:
        result['PK'] = item['PK']
    if 'SK' in item:
        result['SK'] = item['SK']
    if 'id' in item:
        result['id'] = item['id']
    
    return result


def are_affecting_same_dict(a: Dict, b: Dict):
    return get_key_from_dict(a) == get_key_from_dict(b)


def begins_with(x: str, y):
    if isinstance(x, dict):
        return begins_with(x['S'], y)
    if isinstance(y, dict):
        return begins_with(x, y['S'])
    return x.startswith(y)


def ends_with(x: str, y):
    if isinstance(x, dict):
        return ends_with(x['S'], y)
    if isinstance(y, dict):
        return ends_with(x, y['S'])
    return x.endswith(y)


def contains(x: str, y):
    if isinstance(x, dict):
        return contains(x['S'], y)
    if isinstance(y, dict):
        return contains(x, y['S'])
    return y in x


def is_equal_val(x: str, y):
    if isinstance(x, dict):
        return is_equal_val(x['S'], y)
    if isinstance(y, dict):
        return is_equal_val(x, y['S'])
    return y == x


ACTIONS = {
    "begins_with": begins_with,
    'ends_with': ends_with,
    'contains': contains,
    '=': is_equal_val
}


def clean_transactions(transactions: List[Dict]) -> List[Dict]:
    unique_transactions = []
    for transaction in transactions:
        if not any(are_affecting_same_dict(transaction, unique_transaction) for unique_transaction in unique_transactions):
            unique_transactions.append(transaction)
    diff = list(filter(lambda x: x not in unique_transactions, transactions))
    if diff and len(diff) > 0:
        raise Exception(
            f"Transactions are affecting the same item: {diff}")
    return unique_transactions


class DynamoClientTestImpl(Interface):

    def __init__(self):
        self.tables = {}

    def get_table(self, TableName: str):
        if TableName not in self.tables:
            self.tables[TableName] = []
        return self.tables[TableName]

    def put_transaction(self, transaction: Dict):
        self.get_table(transaction['TableName'])
        item = transaction['Item']
        if 'PK' in item and 'SK' in item:
            self.delete(transaction['TableName'], {
                'PK': item['PK'],
                'SK': item['SK']
            })
        self.tables[transaction['TableName']].append(transaction['Item'])

    def delete_transaction(self, transaction: Dict):
        self.get_table(transaction['TableName'])
        self.tables[transaction['TableName']] = list(filter(
            lambda x: x != transaction['Item'], self.tables[transaction['TableName']]))

    def update_transaction(self, transaction: Dict):
        self.get_table(transaction['TableName'])
        for item in self.tables[transaction['TableName']]:
            if is_equal(item, transaction['Key']):
                update_expression = transaction['UpdateExpression']
                update_expression = update_expression.replace('SET', '')
                update_expression = update_expression.replace(' ', '')
                update_expression = update_expression.split(',')
                update_expression_dict = {}
                for expression in update_expression:
                    key, value = expression.split('=')
                    update_expression_dict[key] = value
                for key, value in update_expression_dict.items():
                    attr = transaction["ExpressionAttributeNames"][key]
                    val = transaction["ExpressionAttributeValues"][value]
                    item[attr] = val
                return
        raise Exception('Item not found')

    def write_transaction(self, transactions: List):
        accepted_transaction_types = ['Put', 'Update', 'Delete']
        transactions = clean_transactions(transactions)
        for transaction in transactions:
            for key in transaction:
                item = transaction[key]
                if key not in accepted_transaction_types:
                    raise Exception('Invalid transaction type')
                if key == 'Put':
                    self.put_transaction(item)
                elif key == 'Update':
                    self.update_transaction(item)
                elif key == 'Delete':
                    self.delete_transaction(item)

    def query(self, TableName: str, **kwargs):
        if TableName not in self.tables:
            return {'Items': [], 'Count': 0}
        expression_attribute_values = kwargs.get(
            'ExpressionAttributeValues', {})
        key_condition_expression = kwargs.get('KeyConditionExpression', '')
        key_condition_expression = key_condition_expression.replace(' ', '')
        key_condition_expression = key_condition_expression.split('AND')
        filters = []
        for expression in key_condition_expression:
            if 'begins_with' in expression:
                expression = expression.replace('begins_with', '')
                expression = expression.replace('(', '')
                expression = expression.replace(')', '')
                key, value = expression.split(',')
                filters.append(('begins_with', {
                    "key": key,
                    "value": expression_attribute_values[value]
                }))
            else:
                key, value = expression.split('=')
                filters.append(('=', {
                    "key": key,
                    "value": expression_attribute_values[value]
                }))
        items = []
        for item in self.tables[TableName]:
            if eval_expressions(item, filters, ACTIONS):
                items.append(item)
        return {'Items': items, 'Count': len(items)}

    def get(self, table_name: str, key: Dict):
        self.get_table(table_name)
        for i in self.tables[table_name]:
            if is_equal(i, key):
                return {"Item": i}
        return {}

    def put(self, table_name: str, item: Dict):
        self.get_table(table_name)
        self.tables[table_name].append(item)

    def delete(self, table_name: str, key: Dict):
        self.get_table(table_name)
        self.tables[table_name] = list(filter(
            lambda x: not is_equal(x, key), self.tables[table_name]))

    def scan(self, TableName: str, **kwargs):
        if TableName not in self.tables:
            return {'Items': []}

        if not kwargs or len(kwargs) == 0:
            return {'Items': self.tables[TableName]}
        filters = []
        if 'FilterExpression' in kwargs:
            expresions = kwargs['FilterExpression']
            expresions = expresions.replace(' ', '')
            expresions = expresions.split('AND')
            values = kwargs['ExpressionAttributeValues']

            for expresion in expresions:
                if 'begins_with' in expresion:
                    expresion = expresion.replace('begins_with', '')
                    expresion = expresion.replace('(', '')
                    expresion = expresion.replace(')', '')
                    key, value = expresion.split(',')
                    filters.append(('begins_with', {
                        "key": key,
                        "value": values[value]
                    }))

                elif 'ends_with' in expresion:
                    expresion = expresion.replace('ends_with', '')
                    expresion = expresion.replace('(', '')
                    expresion = expresion.replace(')', '')
                    key, value = expresion.split(',')
                    filters.append(('ends_with', {
                        "key": key,
                        "value": values[value]
                    }))
                elif 'contains' in expresion:
                    expresion = expresion.replace('contains', '')
                    expresion = expresion.replace('(', '')
                    expresion = expresion.replace(')', '')
                    key, value = expresion.split(',')
                    filters.append(('ends_with', {
                        "key": key,
                        "value": values[value]
                    }))
                else:
                    key, value = expresion.split('=')
                    filters.append(('=', {
                        "key": key,
                        "value": values[value]
                    }))

        items = []
        for item in self.tables[TableName]:
            if eval_expressions(item, filters, ACTIONS):
                items.append(item)
        return {'Items': items}

    def update(self, table_name: str, key: Dict, update_expression: Union[str, Dict], 
               expression_attribute_names: Optional[Dict] = None,
               expression_attribute_values: Optional[Dict] = None):
        """
        Update method that supports both old and new signatures for backwards compatibility.
        For testing purposes, we'll do a simple merge of values.
        """
        self.get_table(table_name)
        for i in self.tables[table_name]:
            if is_equal(i, key):
                # If it's the old signature (third param is a dict), use it directly
                if isinstance(update_expression, dict):
                    item = update_expression
                    for k, v in item.items():
                        i[k] = v
                else:
                    # New UpdateExpression signature - for testing, just merge expression_attribute_values
                    if expression_attribute_values:
                        for placeholder, value in expression_attribute_values.items():
                            # Simple mock: extract attribute name from expression and update
                            if expression_attribute_names:
                                for name_placeholder, attr_name in expression_attribute_names.items():
                                    if name_placeholder in update_expression:
                                        i[attr_name] = value
                            else:
                                # Fallback: try to find the attribute directly in the expression
                                # This is a very simplified parser for testing
                                pass
                return {"Attributes": i}
        return {'Attributes': None}

    def scan_pages(self, table_name: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Mock implementation of scan_pages for testing."""
        # Get all items using regular scan
        result = self.scan(table_name, **kwargs)
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

    def batch_get_item(self, request_items: Dict) -> Dict:
        """Mock implementation of batch_get_item for testing."""
        responses = {"Responses": {}}
        
        for table_name, request in request_items.items():
            items = []
            for key in request.get("Keys", []):
                response = self.get(table_name, key)
                if response.get("Item"):
                    items.append(response["Item"])
            responses["Responses"][table_name] = items
            
        return responses

    def batch_write_item(self, request_items: Dict) -> Dict:
        """Mock implementation of batch_write_item for testing."""
        for table_name, requests in request_items.items():
            for request in requests:
                if "PutRequest" in request:
                    self.put(table_name, request["PutRequest"]["Item"])
                elif "DeleteRequest" in request:
                    self.delete(table_name, request["DeleteRequest"]["Key"])
                    
        return {"UnprocessedItems": {}}

    def clear(self):
        self.tables = {}
