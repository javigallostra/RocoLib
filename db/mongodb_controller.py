from bson.objectid import ObjectId

import functools
from datetime import datetime


def serializable(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if type(value) is dict and  '_id' in value:
            return make_object_serializable(value)
        elif type(value) == dict:
            for key, val in value.items():
                if type(val) == list:
                    value[key] = make_list_serializable(val)
                elif '_id' in val:
                    value[key] = make_object_serializable(val)
            return value
        elif type(value) == list:
            return make_list_serializable(value)
    return wrapper
        
def make_object_serializable(element):
    if not element:
        return {}
    if '_id' in element:
        element['_id'] = str(element['_id'])
    return element

def make_list_serializable(data):
    if not data:
        return []
    for element in data:
       make_object_serializable(element)
    return data

@serializable
def get_gyms(database):
    """
    Get the list of available gyms
    """
    return list(database['walls'].find())
    
@serializable
def get_gym_walls(gym, database):
    """
    Return the list of available walls for a specific
    Gym
    """
    return list(database[f'{gym}_walls'].find())

def get_gym_pretty_name(gym, database):
    """
    Get the actual Gym name from its path
    """
    data = database['walls'].find_one({'id': gym}, {'name':1})
    return data.get('name', '') if data else ''

def get_wall_name(gym_name, wall_section, database):
    """
    Get the actual wall name from its path
    """
    data = database[f'{gym_name}_walls'].find_one({'image': wall_section},{'name': 1})
    return data.get('name', '') if data else ''

def get_gym_section_name(gym, section, database):
    """
    Given a gym and a section image filename, return the 
    proper name of the section
    """
    return get_wall_name(gym, section, database)

def get_walls_radius_all(database):
    """
    Get the list of all radius used to paint the 
    circles in the different wall sections:
    {
        'sancu/s1': 0.0317124736, 
        'sancu/s2': 0.0317124736, 
        'sancu/s3': 0.0317124736, 
        'sancu/s4': 0.0317124736, 
        [...]
    }
    """
    gym_ids = [gym['id'] for gym in get_gyms(database)]
    walls_with_radius = {}
    for gym in gym_ids:
        gym_walls_list = get_gym_walls(gym, database)
        walls_with_radius = {
            **walls_with_radius,
            **{f"{gym}/{wall['image']}" : wall['radius'] for wall in gym_walls_list}
        }
    return walls_with_radius

@serializable
def get_boulders(gym, database):
    """
    Get the whole list of boulders for the specified gym
    """
    raw_boulder_data = list(database[f'{gym}_boulders'].find())
    return {'Items': raw_boulder_data}

@serializable
def get_routes(gym, database):
    """
    Get the whole list of routes for the specified gym
    """
    raw_route_data = list(database[f'{gym}_routes'].find())
    return {'Items': raw_route_data}

@serializable
def put_boulder(boulder_data, gym, database):
    """
    Store a new boulder for the specified gym
    """
    return database[f'{gym}_boulders'].insert_one(boulder_data)

@serializable
def put_route(route_data, gym, database):
    """
    Store a new route for the specified gym
    """
    return database[f'{gym}_routes'].insert_one(route_data)

@serializable
def put_boulder_in_ticklist(boulder_data, user_id, database, mark_as_done_clicked=False):
    # TODO: split in two functions, urgent refactor
    """
    Store a new boulder in the user's ticklist, change its
    is_done status or add a new climbed date
    """
    IS_DONE = 'is_done'
    IDEN = 'iden'
    user = database['users'].find_one({'id': user_id})
    # get ticklist
    ticklist = user.get('ticklist', [])
    # check if problem is already there
    boulder = list(filter(lambda x: x[IDEN]==boulder_data[IDEN], ticklist))
    # nothing changed, boulder already in ticklist and no status change
    if boulder and boulder[0][IS_DONE] == boulder_data[IS_DONE]:
        # boulder is in ticklist, has already been climbed, but a new mark as done event
        # has been triggered
        if boulder_data[IS_DONE] and mark_as_done_clicked:
            # add a new climbed date
            for index, t_boulder in enumerate(ticklist):
                if t_boulder[IDEN] == boulder_data[IDEN]:
                    ticklist[index][IS_DONE] = boulder_data[IS_DONE]
                    # if string, change to list
                    if type(ticklist[index]['date_climbed']) == str:
                        ticklist[index]['date_climbed'] = [
                            ticklist[index]['date_climbed'], 
                            datetime.today().strftime('%Y-%m-%d')
                        ]
                    else:
                        ticklist[index]['date_climbed'] += [datetime.today().strftime('%Y-%m-%d')]
                    user['ticklist'] = ticklist
                    database['users'].update_one({'id':user_id}, {'$set' : user})
        return ticklist
    # boulder is in ticklist but is_done has changed:
    elif boulder and boulder[0][IS_DONE] != boulder_data[IS_DONE]:
        for index, t_boulder in enumerate(ticklist):
            if t_boulder[IDEN] == boulder_data[IDEN]:
                ticklist[index][IS_DONE] = boulder_data[IS_DONE]
                ticklist[index]['date_climbed'] = [datetime.today().strftime('%Y-%m-%d')]
    # boulder is not in ticklist but it has been marked 
    # as climbed, add to ticklist
    elif boulder_data[IS_DONE]:
        boulder_data['date_climbed'] = [datetime.today().strftime('%Y-%m-%d')]
        ticklist.append(boulder_data)
    # update user's ticklist and return it
    user['ticklist'] = ticklist
    database['users'].update_one({'id':user_id}, {'$set' : user})
    return ticklist

@serializable
def delete_boulder_in_ticklist(boulder_data, user_id, database):
    """
    Delete the selected problem from the user's ticklist
    """
    user = database['users'].find_one({'id': user_id})
    filtered_list = []
    if user:
        # get ticklist
        ticklist = user.get('ticklist', [])
        # remove problem from list
        filtered_list = list(filter(lambda x: x['iden'] != boulder_data['iden'], ticklist))
        user['ticklist'] = filtered_list
        database['users'].update_one({'id': user_id}, {'$set' : user})
    return filtered_list

@serializable
def get_ticklist_boulder(boulder, database):
    """
    Given a ticklist problem, get the remaining problem fields
    """
    boulder_data = database[f'{boulder.gym}_boulders'].find_one(ObjectId(boulder.iden))
    boulder_data['gym'] = boulder.gym
    boulder_data['is_done'] = boulder.is_done
    # backwards compatibility
    if boulder.date_climbed:
        boulder_data['date_climbed'] = boulder.date_climbed if type(boulder.date_climbed) == list else [boulder.date_climbed]
    else:
        boulder_data['date_climbed'] = []
    return boulder_data
    
@serializable
def get_boulder_by_name(gym, name, database):
    """
    Given a boulder name and a Gym, return the boulder data
    """
    boulder = database[f'{gym}_boulders'].find_one({'name':name})
    return boulder if boulder else {}

@serializable
def update_boulder_by_id(gym, boulder_id, data, database):
    """
    Given a boulder id, a Gym, and new boulder data update the
    whole body of data for that boulder
    """
    data.pop('_id', None)
    return database[f'{gym}_boulders'].update_one({'_id': ObjectId(boulder_id)}, {'$set' : data})

@serializable
def get_boulders_filtered(gym, database, conditions=None, equals=None, ranged=None, contains=None):
    """
    Given a gym and a set of conditions return the list of boulders
    that fulfill them
    """
    # if there are no conditions, return everything
    if not conditions:
        return {'Items': list(database[f'{gym}_boulders'].find())}
    
    # if there are conditions, apply filters
    query = {}
    for key, value in conditions.items():
        if key in equals:
            # build query
            query[key] = value
    # get data
    filtered_boulder_data = list(database[f'{gym}_boulders'].find(query))

    if not filtered_boulder_data:
        filtered_boulder_data = list(database[f'{gym}_boulders'].find())

    to_be_removed = []
    for key, val in conditions.items():
        for boulder in filtered_boulder_data:
            if key in contains and val.lower() not in boulder[key].lower():
                to_be_removed.append(str(boulder['_id']))
            elif key in equals and val.lower() != boulder[key].lower():
                to_be_removed.append(str(boulder['_id']))
            elif key in ranged and (int(boulder[key]) < int(val)-0.5 or  int(boulder[key]) > int(val)+0.5):
                to_be_removed.append(str(boulder['_id']))

    return {'Items': [boulder for boulder in filtered_boulder_data if str(boulder['_id']) not in to_be_removed]}

## User related functions
@serializable
def save_user(user_data, database):
    """
    Persist user data
    """
    return database['users'].insert_one(user_data)

@serializable
def get_user_data_by_id(user_id, database):
    """
    Given a user id get its data
    """
    user = database['users'].find_one({'id': user_id})
    return user if user else {}

@serializable
def get_user_data_by_email(email, database):
    """
    Given a user email get its data
    """
    user = database['users'].find_one({'email': email})
    return user if user else {}
