import json
from flask import url_for
from db import mongodb_controller as db_controller
from config import *


def parse_boulder_from_request(request):
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

def get_stats(db):
    """
    Gt current app stats from DDBB: Number of problems, routes and Gyms.
    """
    gyms = db_controller.get_gyms(db)
    total_gyms = len(gyms)
    total_boulders = 0
    total_routes = 0
    for gym in gyms:
        try:
            total_boulders += len(db_controller.get_boulders(gym['id'], db)[ITEMS])
        except:
            pass
        try:
            total_routes += len(db_controller.get_routes(gym['id'], db)[ITEMS])
        except:
            pass
    
    return {
        'Boulders': total_boulders,
        'Routes': total_routes,
        'Gyms': total_gyms
    }
