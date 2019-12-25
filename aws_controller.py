import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import json
import operator


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


def get_items_filtered(conditions=None):
    if not conditions:
        return get_items()

    first_expression = True
    condition = None
    for key, value in conditions.items():
        if first_expression:
            condition = Key(key).eq(value)
            first_expression = False
        else:
            condition = operator.__and__(condition, Key(key).eq(value))
    return json.dumps(b_table.scan(
        FilterExpression=condition
    ), default=decimal_default)
