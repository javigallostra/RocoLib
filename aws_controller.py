import boto3
from decimal import Decimal
import json

dynamodb = boto3.resource('dynamodb', 'eu-west-3')
b_table = dynamodb.Table('Boulders')


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def get_items():
    return json.dumps(b_table.scan(), default=decimal_default)


def put_item(item):
    return b_table.put_item(Item=item)
