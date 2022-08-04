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
from werkzeug.local import LocalProxy
from urllib import parse as urlparse

from db import mongodb_controller as db_controller
from src.config import *
from src.typing import Data


def get_hold_detection_active(current_user):
    hold_detection = True
    if current_user.is_authenticated:
        hold_detection = not current_user.user_preferences.hold_detection_disabled
    return hold_detection


def get_creds_file(env: str = '.ddbb.env') -> str:
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
    with open('.ddbb.env', 'w') as f:
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


def get_db_connection() -> Database:
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


def get_current_gym(session, db):
    if session.get('gym', ''):
        return session['gym']
    gyms = db_controller.get_gyms(db)
    return gyms[0]['id']


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


def get_boulders_list(gym: str, filters: Data, database: Database, session, latest_walls_only: bool = True) -> list[Data]:
    """
    Given a gym and a set of filters return the list of
    boulders that match the specified criteria.
    """
    # if user is authenticated, check preferences to add query modifiers
    data = db_controller.get_boulders_filtered(
        gym=gym,
        database=database,
        latest_walls_only=latest_walls_only,
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
        boulder['age'] = get_time_since_creation(boulder['time'])
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
  # request.get_data()  # required?
  if request.json:
    return request.json, False
  elif request.form:
    return request.form, True
  elif request.data:
        try:
            return json.loads(request.data), False
        except json.JSONDecodeError:
            # try to load from query string
            return urlparse.parse_qs(request.data), False
  else:
    return dict(), False


def get_time_since_creation(time: str) -> str:
    """
    Get the time since creation in a readable user friendly
    format, where only the biggest unit (years, months, days, etc)
    is used for the representation

    :param time: creation time
    :type time: str
    :return: time since creation in a readable user friendly format
    :rtype: str
    """
    current = datetime.datetime.now()
    time = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')
    diff = current - time

    years, rem = divmod(diff.days, 365)
    months, days = divmod(rem, 30)
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    if years > 0:
        nb, name = years, 'years' if years > 1 else 'year'
    elif months > 0:
        nb, name = months, 'months' if months > 1 else 'month'
    elif days > 0:
        nb, name = days, 'days' if days > 1 else 'day'
    elif hours > 0:
        nb, name = hours, 'hours' if hours > 1 else 'hour'
    elif minutes > 0:
        nb, name = minutes, 'minutes' if minutes > 1 else 'minute'
    else:
        nb, name = seconds, 'seconds' if seconds != 1 else 'second'

    return f'{nb} {name}'


def get_boulder_from_request(request: LocalProxy, db: Database, session: LocalProxy, gym_code: str) -> Tuple[dict, str]:
    """
    Load boulder data from a given request

    :param request: HTTP/S Request
    :type request: LocalProxy
    :param db: DDBB connection
    :type db: Database
    :param session: current session
    :type session: LocalProxy
    :param gym_code: the gym code of the boulder
    :type gym_code: str
    :return: the boulder data and the path to the wall image
    :rtype: Tuple[dict, str]
    """
    if request.method == 'POST':
        return get_boulder_from_post_request(request, gym_code)
    return get_boulder_from_get_request(request, db, session)


def get_boulder_from_get_request(request: LocalProxy, db: Database, session: LocalProxy) -> Tuple[dict, str]:
    """
    Get boulder data from a GET request

    :param request: HTTP/S Request
    :type request: LocalProxy
    :param db: DDBB connection
    :type db: Database
    :param session: current session
    :type session: LocalProxy
    :return: the boulder data and the path to the wall image
    :rtype: Tuple[dict, str]
    """
    boulder = db_controller.get_boulder_by_name(
        gym=request.args.get('gym'),
        name=request.args.get('name'),
        database=db
    )
    return load_full_boulder_data(
        boulder,
        request.args.get('gym'),
        db,
        session
    )


def get_boulder_from_post_request(request: LocalProxy, gym_code: str) -> Tuple[dict, str]:
    """
    Get boulder data from a POST request

    :param request: HTTP/S Request
    :type request: LocalProxy
    :param gym_code: code of the gym the boulder belongs to
    :type gym_code: str
    :return: The boulder data and the path to the wall image
    :rtype: Tuple[dict, str]
    """
    boulder = make_boulder_data_valid_js(request.form.get('boulder_data'))
    if not boulder.get('gym', ''):
        boulder['gym'] = gym_code
    wall_image = get_wall_image(
        boulder['gym'], boulder['section'], WALLS_PATH)
    return boulder, wall_image


def get_hold_data(gym: str, section: str, static_folder_path: str) -> dict:
    """
    Get the computed hold polygon data for a given wall

    :param gym: code of the gym the wall belongs to
    :type gym: str
    :param section: wall section from which to get the hold data
    :type section: str
    :param static_folder_path: path to the folder with the static assets
    :type static_folder_path: str
    :return: the hols data for the specified wall
    :rtype: dict
    """
    # get hold data
    filename = get_wall_json(gym, section, WALLS_PATH, static_folder_path)
    hold_data = None
    if os.path.exists(filename):
        with open(filename) as f:
            hold_data = json.load(f)
    return hold_data


def load_full_boulder_data(boulder: dict, gym_code: str, db: Database, session: LocalProxy) -> Tuple[dict, str]:
    """
    Complete boulder data by adding the fields that can be lazily
    computed when loading a boulder and hence need not to be stored
    on the DDBB

    :param boulder: original boulder data as stored in the DDBB
    :type boulder: dict
    :param gym_code: the code of the gym the boulder belongs to
    :type gym_code: str
    :param db: DDBB connection
    :type db: Database
    :param session: current session
    :type session: LocalProxy
    :return: the boulder data with the additional fields and the path to the wall image
    :rtype: Tuple[dict, str]
    """
    boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
    boulder['safe_name'] = secure_filename(boulder['name'])
    boulder['radius'] = get_wall_radius(
        session,
        db,
        gym_code + '/' + boulder['section'])
    boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
    boulder['gym'] = gym_code
    wall_image = get_wall_image(
        gym_code, boulder['section'], WALLS_PATH)
    return boulder, wall_image


def load_next_or_current(
    boulder_id: str,
    gym_code: str,
    database: Database,
    session: LocalProxy
) -> Tuple[dict, str]:
    next_boulder = db_controller.get_next_boulder(
        boulder_id, gym_code, database)
    return load_boulder_to_show(next_boulder, gym_code, boulder_id, database, session)


def load_previous_or_current(
    boulder_id: str,
    gym_code: str,
    database: Database,
    session: LocalProxy
) -> Tuple[dict, str]:
    previous_boulder = db_controller.get_previous_boulder(
        boulder_id, gym_code, database)
    return load_boulder_to_show(previous_boulder, gym_code, boulder_id, database, session)


def load_boulder_to_show(
    candidate_boulder: dict,
    gym_code: str,
    current_boulder_id: str,
    database: Database,
    session: LocalProxy
) -> Tuple[dict, str]:
    if candidate_boulder:
        # load boulder
        boulder, wall_image = load_full_boulder_data(
            candidate_boulder,
            gym_code,
            database,
            session
        )
    else:
        # load current boulder
        current_boulder = db_controller.get_boulder_by_id(
            gym_code, current_boulder_id, database)
        boulder, wall_image = load_full_boulder_data(
            current_boulder,
            gym_code,
            database,
            session
        )
    return boulder, wall_image


def choose_language(request, langs) -> str:
    """
    Choose the first known user language else DEFAULT_LANG
    """
    user_lang = request.headers.get('Accept_Language').replace(
        '-', '_').split(';')[0].split(',')

    lang_matches = set(user_lang).intersection(langs.keys())
    if lang_matches:
        return lang_matches.pop()
    return DEFAULT_LANG


def update_user_prefs(request, current_user):
    should_save_user = False
    default_gym = request.form.get('gym')
    if default_gym != current_user.user_preferences.default_gym:
        current_user.user_preferences.default_gym = default_gym
        should_save_user = True
    if request.form.get('latestWallSwitch', False) != current_user.user_preferences.show_latest_walls_only:
        current_user.user_preferences.show_latest_walls_only = bool(
            request.form.get('latestWallSwitch', False))
        should_save_user = True
    if request.form.get('holdDetectionSwitch', False) != current_user.user_preferences.hold_detection_disabled:
        current_user.user_preferences.hold_detection_disabled = bool(
            request.form.get('holdDetectionSwitch', False))
        should_save_user = True
    return should_save_user, current_user
