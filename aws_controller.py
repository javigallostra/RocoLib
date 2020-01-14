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
    for hold in item['holds']:
        hold['x'] = Decimal(str(hold['x']))
        hold['y'] = Decimal(str(hold['y']))
    return b_table.put_item(Item=item)


def get_items_filtered(conditions=None, equals=None, contains=None):
    if not conditions:
        return get_items()

    first_expression = True
    condition = None
    for key, value in conditions.items():
        if first_expression:
            if key in equals:
                condition = Key(key).eq(value)
            if key in contains:
                condition = Key(key).begins_with(value)
            first_expression = False
        else:
            if key in equals:
                condition = operator.__and__(condition, Key(key).eq(value))
            if key in contains:
                condition = operator.__and__(
                    condition, Key(key).begins_with(value))
    return json.dumps(b_table.scan(
        FilterExpression=condition
    ), default=decimal_default)
