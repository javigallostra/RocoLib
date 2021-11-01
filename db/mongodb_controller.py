from typing import Any, Optional

import functools
from datetime import datetime
from bson.objectid import ObjectId

from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult
from models import TickListProblem
from utils.typing import Data


def serializable(func):
    """
    Make sure that the value returned by a function
    is serializable. The main problem is that objects
    retrieved from the DDBB have an _id key whose value
    is an ObjectId(), which is not serializable.
    Another option would be to use json_util:
    https://pymongo.readthedocs.io/en/stable/api/bson/json_util.html
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if type(value) is dict and '_id' in value:
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


def make_object_serializable(element: Data) -> Data:
    """
    Make sure an element can be serialized
    """
    if not element:
        return {}
    if '_id' in element:
        element['_id'] = str(element['_id'])
    return element


def make_list_serializable(data: list[Data]) -> list[Data]:
    """
    Given a list, make sure all of its
    elements are serializable
    """
    if not data:
        return []
    for element in data:
        make_object_serializable(element)
    return data


@serializable
def get_gyms(database: Database) -> list[Data]:
    """
    Get the list of available gyms
    """
    return list(database['walls'].find())


@serializable
def get_gym_walls(gym: str, database: Database) -> list[Data]:
    """
    Return the list of available walls for a specific
    Gym
    """
    return list(database[f'{gym}_walls'].find())


def get_gym_pretty_name(gym: str, database: Database) -> str:
    """
    Get the actual Gym name from its path

    IF the gym cannot be found, return an empty string
    """
    data = database['walls'].find_one({'id': gym}, {'name': 1})
    return data.get('name', '') if data else ''


def get_wall_name(gym_name: str, wall_section: str, database: Database) -> str:
    """
    Get the actual wall name from its path as a string

    If the wall cannot be found, return an empty string
    """
    data = database[f'{gym_name}_walls'].find_one(
        {'image': wall_section}, {'name': 1})
    return data.get('name', '') if data else ''


def get_gym_section_name(gym: str, section, database: Database) -> str:
    """
    Given a gym and a section image filename, return the
    proper name of the section as a string
    """
    return get_wall_name(gym, section, database)


def get_walls_radius_all(database: Database) -> dict[str, float]:
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
            **{f"{gym}/{wall['image']}": wall['radius'] for wall in gym_walls_list}
        }
    return walls_with_radius


@serializable
def get_boulders(gym: str, database: Database) -> dict[str, list[Data]]:
    """
    Get the whole list of boulders for the specified gym

    The returned dictionary has one key-value pair.
    The key is 'Items' and the value is a list of raw boulder data.
    """
    raw_boulder_data = list(database[f'{gym}_boulders'].find())
    return {'Items': raw_boulder_data}


@serializable
def get_routes(gym: str, database: Database) -> dict[str, list[Data]]:
    """
    Get the whole list of routes for the specified gym

    The returned dictionary has one key-value pair.
    The key is 'Items' and the value is a list of raw route data.
    """
    raw_route_data = list(database[f'{gym}_routes'].find())
    return {'Items': raw_route_data}


@serializable
def put_boulder(boulder_data: Data, gym: str, database: Database) -> InsertOneResult:
    """
    Store a new boulder for the specified gym
    """
    return database[f'{gym}_boulders'].insert_one(boulder_data)


@serializable
def put_route(route_data: Data, gym: str, database: Database) -> InsertOneResult:
    """
    Store a new route for the specified gym
    """
    return database[f'{gym}_routes'].insert_one(route_data)


@serializable
def put_boulder_in_ticklist(boulder_data: Data, user_id: str, database: Database, mark_as_done_clicked: bool = False) -> list[Data]:
    """
    Store a new boulder in the user's ticklist, change its
    is_done status or add a new climbed date

    Return the updated ticklist
    """
    IS_DONE = 'is_done'
    IDEN = 'iden'
    DATE_CLIMBED = 'date_climbed'
    TICKLIST = 'ticklist'
    USERS = 'users'
    user: Data = database[USERS].find_one({'id': user_id})
    # get ticklist
    ticklist: list[Data] = user.get(TICKLIST, [])
    # check if problem is already in the user's ticklist
    boulder = list(filter(lambda x: x[IDEN] == boulder_data[IDEN], ticklist))
    # Boulder is not in ticklist
    if not boulder:
        # Add it to ticklist, either marked as done or not
        if boulder_data[IS_DONE] and mark_as_done_clicked:
            boulder_data[DATE_CLIMBED] = [
                datetime.today().strftime('%Y-%m-%d')]
        ticklist.append(boulder_data)
        update_user_ticklist(database, ticklist, user, user_id)
    # boulder is already in ticklist and marked as done
    elif boulder and mark_as_done_clicked and boulder_data[IS_DONE]:
        # find boulder index in ticklist
        index = find_boulder_index(boulder_data, ticklist)
        # mark boulder as done
        ticklist[index][IS_DONE] = boulder_data[IS_DONE]
        # Set climbed date. If string, change to list
        ticklist = set_climbed_date(ticklist, index)
        update_user_ticklist(database, ticklist, user, user_id)
    return ticklist


def update_user_ticklist(database: Database, ticklist: list[Data], user: Data, user_id: str) -> None:
    """
    Update a user's ticklist, both DDBB and in memory projections
    """
    user['ticklist'] = ticklist
    database['users'].update_one({'id': user_id}, {'$set': user})


def find_boulder_index(boulder_data: Data, boulders: list[Data]) -> int:
    """
    Given a list of boulders and the data from a single boulder,
    find the boulder in the list and return its index if found.
    Else return -1
    """
    IDEN = 'iden'
    for index, t_boulder in enumerate(boulders):
        if t_boulder[IDEN] == boulder_data[IDEN]:
            return index
    return -1


@serializable
def set_climbed_date(ticklist: list[Data], index: int, climbed_date: Optional[datetime] = None) -> list[Data]:
    """
    Given a list of boulders and an index, update the climbed
    date of the boulder at the given index

    Return the updated ticklist
    """
    DATE_CLIMBED = 'date_climbed'
    if not climbed_date:
        climbed_date = datetime.today()
    if type(ticklist[index][DATE_CLIMBED]) == str:
        ticklist[index][DATE_CLIMBED] = [
            ticklist[index][DATE_CLIMBED],
            climbed_date.strftime('%Y-%m-%d')
        ]
    else:
        ticklist[index][DATE_CLIMBED] += [climbed_date.strftime('%Y-%m-%d')]
    return ticklist


@serializable
def delete_boulder_in_ticklist(boulder_data: Data, user_id: str, database: Database) -> list[Data]:
    """
    Delete the selected problem from the user's ticklist

    Return the filtered list of boulders with the given one removed
    """
    user: Data = database['users'].find_one({'id': user_id})
    filtered_list: list[Data] = []
    if user:
        # get ticklist
        ticklist = user.get('ticklist', [])
        # remove problem from list
        filtered_list = list(
            filter(lambda x: x['iden'] != boulder_data['iden'], ticklist))
        user['ticklist'] = filtered_list
        database['users'].update_one({'id': user_id}, {'$set': user})
    return filtered_list


@serializable
def get_ticklist_boulder(boulder: TickListProblem, database: Database) -> Data:
    """
    Given a ticklist problem, get the remaining problem fields

    Return a boulder data with 'gym', 'is_done', and 'date_climbed' fields
    """
    boulder_data: Data = database[f'{boulder.gym}_boulders'].find_one(
        ObjectId(boulder.iden))
    boulder_data['gym'] = boulder.gym
    boulder_data['is_done'] = boulder.is_done
    # backwards compatibility
    if boulder.date_climbed:
        boulder_data['date_climbed'] = boulder.date_climbed if type(
            boulder.date_climbed) == list else [boulder.date_climbed]
    else:
        boulder_data['date_climbed'] = []
    return boulder_data


@serializable
def get_boulder_by_name(gym: str, name: str, database: Database) -> Data:
    """
    Given a boulder name and a Gym, return the boulder data

    Return an empty dictionary if the boulder is not found
    """
    boulder = database[f'{gym}_boulders'].find_one({'name': name})
    return boulder if boulder else {}


@serializable
def update_boulder_by_id(gym: str, boulder_id: str, data: Data, database: Database) -> UpdateResult:
    """
    Given a boulder id, a Gym, and new boulder data update the
    whole body of data for that boulder
    """
    data.pop('_id', None)
    return database[f'{gym}_boulders'].update_one({'_id': ObjectId(boulder_id)}, {'$set': data})


@serializable
def get_boulders_filtered(
        gym: str,
        database: Database,
        conditions: Optional[dict] = None,
        equals: Optional[list] = None,
        ranged: Optional[list] = None,
        contains: Optional[list] = None
    ) -> dict[str, list[Data]]:
    """
    Given a gym and a set of conditions return the list of boulders
    that fulfill them

    The returned dictionary has one key-value pair.
    The key is 'Items' and the value is a list of boulder data.
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
            elif key in ranged and (int(boulder[key]) < int(val) - 0.5 or int(boulder[key]) > int(val) + 0.5):
                to_be_removed.append(str(boulder['_id']))

    return {'Items': [boulder for boulder in filtered_boulder_data if str(boulder['_id']) not in to_be_removed]}

# User related functions


@serializable
def save_user(user_data: Data, database: Database) -> InsertOneResult:
    """
    Persist user data

    Insert user_data in the given database
    """
    return database['users'].insert_one(user_data)


@serializable
def get_user_data_by_id(user_id: str, database: Database) -> Data:
    """
    Given a user id get its data

    Return an empty dictionary if the user is not found
    """
    user = database['users'].find_one({'id': user_id})
    return user if user else {}


@serializable
def get_user_data_by_email(email: str, database: Database) -> Data:
    """
    Given a user email get its data

    Return an empty dictionary if the user is not found
    """
    user = database['users'].find_one({'email': email})
    return user if user else {}
