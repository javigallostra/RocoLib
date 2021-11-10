import json
import math
import os
from typing import Union
from flask import url_for
import datetime
from flask.globals import _app_ctx_stack, session
from flask.sessions import SessionMixin
import pymongo
from pymongo.database import Database
from werkzeug.utils import secure_filename
from werkzeug.wrappers.request import Request

from db import mongodb_controller as db_controller
from config import *
from api.blueprint import get_gym_boulders, get_gym_pretty_name, get_gym_wall_name, get_gyms, get_gym_walls, boulder_create
from utils.typing import Data


def get_creds_file() -> str:
    """
    Get the credentials file
    """
    creds = None
    with open('.env', 'r') as f:
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


def load_boulder_from_request(request: Request) -> Data:
    """
    Replace boulder data from valid Python to valid JS
    """
    return json.loads(
        request.form.get('boulder_data')
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
                db_controller.get_boulders(gym['id'], database)[ITEMS])
        except Exception:
            pass
        try:
            total_routes += len(db_controller.get_routes(
                gym['id'], database)[ITEMS])
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
    # Map and complete boulder data
    for boulder in data[ITEMS]:
        boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
        boulder['safe_name'] = secure_filename(boulder['name'])
        boulder['radius'] = get_wall_radius(
            session, database, gym + '/' + boulder['section'])
        boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
    return sorted(
        data[ITEMS],
        key=lambda x: datetime.datetime.strptime(
            x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True
    )


def get_closest_gym(long: float, lat: float, database: Database) -> str:
    """
    Given a set of coordinates, return the closest gym
    to that pair of coordinates.

    This is a naive solution. If the number of gyms
    gets too big, this algorithm can be sped up
    by sorting the coordinates beforehand
    """
    gyms = db_controller.get_gyms(database)
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
        return closest_gym['id']
    return gyms[0]['id']


def generate_api_docs(app) -> None:
    """
    Generate the OpenAPI spec doc
    """
    # Generate API documentation
    from api.schemas import spec
    from api.schemas import GymListSchema
    from api.schemas import WallListSchema
    from api.schemas import GymNameSchema
    from api.schemas import WallNameSchema
    from api.schemas import GymBoulderListSchema
    from api.schemas import CreateBoulderRequestBody
    from api.schemas import CreateBoulderResponseBody
    from api.schemas import CreateBoulderErrorResponse
    spec.components.schema("Gyms", schema=GymListSchema)
    spec.components.schema("Walls", schema=WallListSchema)
    spec.components.schema("Boulders", schema=GymBoulderListSchema)
    spec.components.schema("GymName", schema=GymNameSchema)
    spec.components.schema("WallName", schema=WallNameSchema)
    spec.components.schema(
        "CreateBoulder", schema=CreateBoulderRequestBody)
    spec.components.schema("CreateBoulderResponse",
                           schema=CreateBoulderResponseBody)
    spec.components.schema("CreateBoulderErrorResponse",
                           schema=CreateBoulderErrorResponse)
    with app.test_request_context():
        spec.path(view=get_gyms)
        spec.path(view=get_gym_walls)
        spec.path(view=get_gym_pretty_name)
        spec.path(view=get_gym_wall_name)
        spec.path(view=get_gym_boulders)
        spec.path(view=boulder_create)
    with open('./static/swagger/swagger.json', 'w') as f:
        json.dump(spec.to_dict(), f)
