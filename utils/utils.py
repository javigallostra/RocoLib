import json
import math
import os
from typing import Tuple, Union
from flask import url_for
import datetime
from flask.globals import _app_ctx_stack, session
from flask.sessions import SessionMixin
from flask.wrappers import Request
import pymongo
from pymongo.database import Database
from werkzeug.utils import secure_filename

from db import mongodb_controller as db_controller
from config import *
from utils.typing import Data


def get_creds_file(env: str = '.env') -> str:
    """
    Get the name of the file where the credentials 
    to connect to the DDBB are stored.
    """
    creds = ''
    if os.path.isfile(env):
        with open(env, 'r') as f:
            creds = f.readline()
    return creds


def set_creds_file(creds: str = 'creds.txt') -> None:
    """
    Set the file from which to get the credentials
    """
    with open('.env', 'w') as f:
        f.write(creds)


def get_creds(file: str) -> Union[str, None]:
    """
    Get the credentials to connect to the DDBB
    """
    creds = None
    if os.path.isfile(file):
        if session.get('creds', ''):
            creds = session['creds']
        else:
            with open(file, 'r') as f:
                creds = f.readline()
            session['creds'] = creds
    else:
        try:
            creds = os.environ['MONGO_DB']
        except Exception:
            pass
    return creds


def get_db() -> Database:
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'database'):
        client = pymongo.MongoClient(
            get_creds(get_creds_file()),
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            # socketKeepAlive=True,
            connect=False,
            maxPoolsize=1)
        top.database = client[DB_NAME]
    return top.database


def make_boulder_data_valid_js(data: str) -> Data:
    """
    Replace boulder data from valid Python to valid JS
    """
    # TODO: what should happen with wrong data types? raise an Exception?
    if type(data) is not str:
        return dict()
    return json.loads(
        data
        .replace('\'', '"')
        .replace('True', 'true')
        .replace('False', 'false'))


def get_wall_image(gym: str, section: str, walls_path: str, static_assets_path: str = 'static') -> str:
    """
    Given a gym section, return its image url
    """
    return url_for(
        static_assets_path,
        filename='{}{}/{}.JPG'.format(walls_path, gym, section)
    )

def get_wall_json(gym: str, section: str, walls_path: str, static_assets_path: str = 'static') -> str:
    """
    Given a gym section, return its image url
    """
    return os.path.join(static_assets_path, '{}{}/{}.json'.format(walls_path, gym, section))
    # return url_for(
    #     static_assets_path,
    #     filename='{}{}/{}.json'.format(walls_path, gym, section)
    # )


def get_stats(database: Database) -> dict[str, int]:
    """
    Get current app stats from DDBB: Number of problems, routes and Gyms.
    """
    gyms = db_controller.get_gyms(database)
    total_gyms = len(gyms)
    total_boulders = 0
    total_routes = 0
    for gym in gyms:
        try:
            total_boulders += len(
                db_controller.get_boulders(gym.get('id', ''), database)[ITEMS])
        except Exception:
            pass
        try:
            total_routes += len(db_controller.get_routes(
                gym.get('id', ''), database)[ITEMS])
        except Exception:
            pass

    return {
        'Boulders': total_boulders,
        'Routes': total_routes,
        'Gyms': total_gyms
    }


def get_wall_radius(session: SessionMixin, database: Database, wall_path=None) -> float:
    """
    Gets the radius of the circe used to mark holds for
    a specific wall.
    Wall path is expected to be: 'gym/wall'.
    """
    if session.get('walls_radius', '') and session['walls_radius'].get(wall_path, ''):
        return session['walls_radius'][wall_path]
    return db_controller.get_walls_radius_all(database)[wall_path]


def get_boulders_list(gym: str, filters: Data, database: Database, session) -> list[Data]:
    """
    Given a gym and a set of filters return the list of
    boulders that match the specified criteria.
    """
    data = db_controller.get_boulders_filtered(
        gym=gym,
        database=database,
        conditions=filters,
        equals=EQUALS,
        ranged=RANGE,
        contains=CONTAINS
    )
    sections = set([b['section'] for b in data[ITEMS]])
    radius = {section: get_wall_radius(
        session, database, gym + '/' + section) for section in sections}
    return map_and_complete_boulder_data(data[ITEMS], radius)


def map_and_complete_boulder_data(data: list[Data], radius: dict[str, float]) -> list[Data]:
    """
    Given a list of boulders from de DDBB and a dictionary of wall_sections and its radius,
    return a list of boulders where the data has been mapped for user visualization.
    """
    # Map and complete boulder data
    for boulder in data:
        boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
        boulder['safe_name'] = secure_filename(boulder['name'])
        boulder['radius'] = radius[boulder['section']]
        boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
    return sorted(
        data,
        key=lambda x: datetime.datetime.strptime(
            x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True
    )


def get_closest_gym(long: float, lat: float, database: Database) -> str:
    """
    Find closest gym to a given set of coordinates 
    """
    return find_closest(db_controller.get_gyms(database), lat, long)


def find_closest(gyms: list[Data], lat: float, long: float) -> str:
    """
    Given a list of gyms and a pair of coordinates, find the closest gym
    to the pair of coordinates.

    This is a naive solution. If the number of gyms
    gets too big, this algorithm can be sped up
    by sorting the coordinates beforehand

    """
    closest_gym = None
    min_distance = -1
    for gym in gyms:
        coords = gym.get('coordinates', [])
        if not coords:
            continue
        dst = math.sqrt(abs(long - coords[0])**2 + abs(lat - coords[1])**2)
        if min_distance == -1 or dst < min_distance:
            min_distance = dst
            closest_gym = gym
    if closest_gym:
        return closest_gym.get('id', '')
    return gyms[0].get('id', '')

def load_data(request: Request) -> Tuple[dict, bool]:
  """
  Load data from the request body into a dict and return it

  :param request: HTTP/S Request
  :type request: Request
  :return: Dictionary with the data from the request and a boolean indicating if the data came from a form
  :rtype: Tuple[dict, bool]
  """
  # Handle the different content types
  request.get_data()  # required?
  if request.data:
    return json.loads(request.data), False
  elif request.form:
    return request.form, True
  elif request.json:
    return request.json, False
  else:
    return dict(), False
