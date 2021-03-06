import json
from flask import url_for
import datetime
from werkzeug.utils import secure_filename

from db import mongodb_controller as db_controller
from config import *


def load_boulder_from_request(request):
    """
    Replace boulder data from valid Python to valid JS
    """
    return json.loads(
        request.form.get('boulder_data')
        .replace('\'', '"')
        .replace('True', 'true')
        .replace('False', 'false'))


def get_wall_image(gym, section, walls_path, static_assets_path='static'):
    return url_for(
        static_assets_path,
        filename='{}{}/{}.JPG'.format(walls_path, gym, section)
    )


def get_stats(database):
    """
    Gt current app stats from DDBB: Number of problems, routes and Gyms.
    """
    gyms = db_controller.get_gyms(database)
    total_gyms = len(gyms)
    total_boulders = 0
    total_routes = 0
    for gym in gyms:
        try:
            total_boulders += len(
                db_controller.get_boulders(gym['id'], database)[ITEMS])
        except:
            pass
        try:
            total_routes += len(db_controller.get_routes(
                gym['id'], database)[ITEMS])
        except:
            pass

    return {
        'Boulders': total_boulders,
        'Routes': total_routes,
        'Gyms': total_gyms
    }


def get_wall_radius(session, database, wall_path=None):
    """
    Gets the radius of the circe used to mark holds for
    a specific wall.
    Wall path is expected to be: 'gym/wall'.
    """
    if session.get('walls_radius', '') and session['walls_radius'].get(wall_path, ''):
        return session['walls_radius'][wall_path]
    return db_controller.get_walls_radius_all(database)[wall_path]


def get_boulders_list(gym, filters, database, session):
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
