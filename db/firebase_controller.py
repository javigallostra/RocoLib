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

def init_db_connection():
    """
    Connect to the DB where gym, wall and problem data
    is stored
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(rocolib_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL' : 'https://rocolib.firebaseio.com'
        })

def get_gym_walls(gym=None):
    """
    Return the list of available walls for a specific
    Gym
    """
    init_db_connection()
    return db.reference(gym).child('walls').get()

def get_gym_section_name(gym=None, section=None):
    """
    Given a gym and a section image filename, return the 
    proper name of the section
    """
    init_db_connection()
    gym_walls = db.reference(gym).child('walls').get()
    name = [wall['name'] for wall in gym_walls if wall['image'] == section]
    return name[0] if len(name)>=1 else ""

def get_gyms():
    """
    Get the list of available gyms
    """
    init_db_connection()
    return db.reference('walls').get()

def get_walls_radius_all():
    """
    Get the list of all radius used to paint the 
    circles in the different wall sections
    """
    gyms = get_gyms()
    walls = [[get_gym_walls(gym['value']), gym['value']] for gym in gyms]
    walls_with_radius = {}
    for walls_list in walls:
        walls_with_radius = {
            **walls_with_radius,
            **{ walls_list[-1]+'/'+wall['image']: wall['radius'] for wall in walls_list[0] }
        }
    return walls_with_radius

def get_connection(gym='/sancu'):
    """
    Connect to DB and return data for specified gym
    or default, if none is provided
    """
    # Create connection
    init_db_connection()
    return db.reference(gym)

def get_boulders(gym='/sancu'):
    """
    Get the whole list of boulders for the specified gym
    """
    collection = get_connection(gym)
    raw_data = collection.child('boulders').get()
    boulder_data = {'Items': [val for key, val in raw_data.items()]}
    return boulder_data

def get_routes(gym='/sancu'):
    """
    Get the whole list of routes for the specified gym
    """
    collection = get_connection(gym)
    raw_data = collection.child('routes').get()
    route_data = {'Items': [val for key, val in raw_data.items()]}
    return route_data

def put_boulder(boulder_data, gym='/sancu'):
    """
    Store a new boulder for the specified gym
    """
    collection = get_connection(gym)
    return collection.child('boulders').push(boulder_data)

def put_route(route_data, gym='/sancu'):
    """
    Store a new route for the specified gym
    """
    collection = get_connection(gym)
    return collection.child('routes').push(route_data)


def get_boulder_by_name(gym=None, name=None):
    """
    Given a boulder name and a Gym, return the boulder data
    """
    # if there are conditions, apply filters
    collection = get_connection(gym).child('boulders')
    return collection.order_by_child('name').equal_to(name).get()

def update_boulder_by_id(gym=None, boulder_id=None, data=None):
    """
    Given a boulder id, a Gym, and new boulder data update the
    whole body of data for that boulder
    """
    collection = get_connection(gym).child('boulders/{}'.format(boulder_id))
    collection.set(data)

def get_boulders_filtered(gym='/sancu', conditions=None, equals=None, ranged=None, contains=None):
    """
    Given a gym and a set of conditions return the list of boulders
    that fulfill them
    """
    # if there are no conditions, return everything
    if not conditions:
        return get_boulders(gym)
    
    # if there are conditions, apply filters
    collection = get_connection(gym).child('boulders')
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
            elif key in ranged and (int(b_val[key]) < int(val)-0.5 or  int(b_val[key]) > int(val)+0.5):
                to_be_removed.append(b_key)

    return {'Items': [val for key, val in fb_data.items() if key not in to_be_removed]}
    
if __name__ == '__main__':
    print(get_gym_walls('/sancu'))
    print(get_walls_radius_all())
