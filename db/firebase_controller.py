import urllib.request
import urllib.parse
import json
import math

from datetime import date, datetime

import re

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# rocolib_path = '../rocolib.json' # For testing
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

def get_gym_pretty_name(gym):
    """
    Get the actual Gym name from its path
    """
    init_db_connection()
    data = db.reference('walls').order_by_child('value').equal_to(gym).get()
    return list(data.values())[0]['name']

def get_wall_name(gym_name, wall_section):
    """
    Get the actual wall name from its path
    """
    init_db_connection()
    data = db.reference(gym_name).child('walls').order_by_child('image').equal_to(wall_section).get()
    return list(data.values())[0]['name']

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

def get_users_connection():
    """
    Connect to DB and return data for specified gym
    or default, if none is provided
    """
    # Create connection
    init_db_connection()
    return db.reference("/users")

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

def put_boulder_in_ticklist(boulder_data, user_id):
    # TODO: split in two functions
    """
    Store a new boulder in the user's ticklist or change its
    is_done status
    """
    IS_DONE = 'is_done'
    IDEN = 'iden'
    collection = get_users_connection()
    user = collection.order_by_child('id').equal_to(user_id).get()
    # get ticklist
    ticklist = list(user.values())[0].get('ticklist', [])
    # check if problem is already there
    boulder = list(filter(lambda x: x[IDEN]==boulder_data[IDEN], ticklist))
    # nothing changed, boulder already in ticklist and no status change
    if boulder and boulder[0][IS_DONE] == boulder_data[IS_DONE]:
        return ticklist
    # boulder is in ticklist but is_done has changed:
    elif boulder and boulder[0][IS_DONE] != boulder_data[IS_DONE]:
        for index, t_boulder in enumerate(ticklist):
            if t_boulder[IDEN] == boulder_data[IDEN]:
                ticklist[index][IS_DONE] = boulder_data[IS_DONE]
                ticklist[index]['date_climbed'] = datetime.today().strftime('%Y-%m-%d')
    # boulder is not in ticklist, add to ticklist
    else:
        if boulder_data[IS_DONE] == True:
            boulder_data['date_climbed'] = datetime.today().strftime('%Y-%m-%d')
        ticklist.append(boulder_data)
    print(boulder_data)
    # update user's ticklist and return it 
    collection.child(f'{list(user.keys())[0]}/ticklist').set(ticklist)
    return ticklist

def delete_boulder_in_ticklist(boulder_data, user_id):
    """
    Delete the selected problem from the user's ticklist
    """
    collection = get_users_connection()
    user = collection.order_by_child('id').equal_to(user_id).get()
    # get ticklist
    ticklist = list(user.values())[0]['ticklist']
    # remove problem from list
    filtered_list = list(filter(lambda x: x['iden'] != boulder_data['iden'], ticklist))
    collection.child(f'{list(user.keys())[0]}/ticklist').set(filtered_list)
    return filtered_list

def put_route(route_data, gym='/sancu'):
    """
    Store a new route for the specified gym
    """
    collection = get_connection(gym)
    return collection.child('routes').push(route_data)


def get_ticklist_boulder(boulder=None):
    """
    Given a ticklist problem, get the remaining problem fields
    """
    boulder_data = get_connection(boulder.gym).child('boulders/{}'.format(boulder.iden)).get()
    boulder_data['gym'] = boulder.gym
    boulder_data['is_done'] = boulder.is_done
    boulder_data['date_climbed'] = boulder.date_climbed if boulder.date_climbed else ""
    return boulder_data
    
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
    
## User related functions
def save_user(user_data=None):
    """
    Persist user data
    """
    collection = get_connection('users')
    return collection.push(user_data)

def get_user_data_by_id(user_id=None):
    """
    Given a user id get its data
    """
    user = get_connection('users').order_by_child('id').equal_to(user_id).get()
    user_matches = [u for u in user.values()] # this should only return one match
    return user_matches[0] if user_matches else None

def get_user_data_by_email(email=None):
    """
    Given a user email get its data
    """
    user = get_connection('users').order_by_child('email').equal_to(email).get()
    user_matches = [u for u in user.values()] # this should only return one match
    return user_matches[0] if user_matches else None

if __name__ == '__main__':
    # testing
    # print(get_gym_walls('/sancu'))

    # print(get_walls_radius_all())
    
    # print(get_user_data_by_email("test@test.com"))

    # class A:
    #     def __init__(self, iden, gym):
    #         self.iden = iden
    #         self.gym = gym
    # print(get_ticklist_boulder(A('-M7qNHz4uLQKcgK-8Nmv','sancu')))

    print(get_wall_name("sancu", "s5"))
