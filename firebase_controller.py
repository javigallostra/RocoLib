import urllib.request
import urllib.parse
import json
import math

from datetime import date
import re

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

rocolib_path = 'rocolib.json'

def get_walls():
    if not firebase_admin._apps:
        cred = credentials.Certificate(rocolib_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL' : 'https://rocolib.firebaseio.com'
        })
    return db.reference('walls').get()

def get_connection(wall='/sancu'):
    # Create connection
    if not firebase_admin._apps:
        cred = credentials.Certificate(rocolib_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL' : 'https://rocolib.firebaseio.com'
        })
    return db.reference(wall)

def get_boulders(wall='/sancu'):
    collection = get_connection(wall)
    raw_data = collection.child('boulders').get()
    boulder_data = {'Items': [val for key, val in raw_data.items()]}
    return boulder_data

def get_routes(wall='/sancu'):
    collection = get_connection(wall)
    raw_data = collection.child('routes').get()
    route_data = {'Items': [val for key, val in raw_data.items()]}
    return route_data

def put_boulder(boulder_data, wall='/sancu'):
    collection = get_connection(wall)
    return collection.child('boulders').push(boulder_data)

def put_route(route_data, wall='/sancu'):
    collection = get_connection(wall)
    return collection.child('routes').push(route_data)

def get_boulders_filtered(wall='/sancu', conditions=None, equals=None, contains=None):
    # if there are no conditions, return everything
    if not conditions:
        return get_boulders(wall)
    
    # if there are conditions, apply filters
    collection = get_connection(wall).child('boulders')
    fb_data = None
    for key, value in conditions.items():
        if key in equals:
            fb_data = collection.order_by_child(key).equal_to(value).get()
            break

    if fb_data is None:
        fb_data = collection.get()

    to_be_removed = []
    for key, val in conditions.items():
        for b_key, b_val in fb_data.items():
            if key in contains and val.lower() not in b_val[key].lower():
                to_be_removed.append(b_key)
            elif key in equals and val.lower() != b_val[key].lower():
                to_be_removed.append(b_key)

    return {'Items': [val for key, val in fb_data.items() if key not in to_be_removed]}
    
if __name__ == '__main__':
    print(get_walls())