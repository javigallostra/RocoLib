from werkzeug.utils import secure_filename

from db import mongodb_controller
# pylint: disable=unused-wildcard-import
from utils.utils import *
from config import *
from models import TickListProblem


def get_wall_radius(wall_path, database):
    """
    Wall path is expected to be: 'gym/wall'
    """
    return mongodb_controller.get_walls_radius_all(database)[wall_path]


def delete_problem_from_ticklist(request, current_user, database):
    """
    Delete a problem from a user's ticklist
    """
    # needed values: gym, id, section, is_done
    boulder_data = load_boulder_from_request(request)
    boulder = {
        'gym': boulder_data.get('gym'),
        'iden':
            mongodb_controller.get_boulder_by_name(
                boulder_data.get('gym'),
                request.form.get('name'),
                database
        ).get('_id', ''),
        's_done': boulder_data.get('is_done'),
        'section': boulder_data.get('section')
    }
    # update user's ticklist
    return [
        TickListProblem(p) for p in mongodb_controller.delete_boulder_in_ticklist(boulder, current_user.id, database)
    ]


def load_user_ticklist(current_user, database):
    """
    Load a user's ticklist
    """
    # get boulders in ticklist and extra required values
    boulder_list = [
        mongodb_controller.get_ticklist_boulder(problem, database) for problem in current_user.ticklist
    ]
    unique_sections = dict()
    walls_list = []
    for boulder in boulder_list:
        boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
        boulder['safe_name'] = secure_filename(boulder['name'])
        boulder['radius'] = get_wall_radius(
            boulder['gym'] + '/' + boulder['section'], database)
        boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
        if boulder['gym'] not in unique_sections.keys() and boulder['section'] not in unique_sections.values():
            unique_sections[boulder['gym']] = boulder['section']
            walls_list.append({
                'gym_name': mongodb_controller.get_gym_pretty_name(boulder['gym'], database),
                'image': boulder['section'],
                'name': mongodb_controller.get_wall_name(boulder['gym'], boulder['section'], database)
            })
    return boulder_list, walls_list


def add_boulder_to_ticklist(request, current_user, database):
    """
    Add a boulder to a user's ticklist
    """
    # needed values: gym, id, section, is_done
    boulder = {
        'gym': request.form.get('gym'),
        'iden':
            mongodb_controller.get_boulder_by_name(
                request.form.get('gym'),
                request.form.get('name'),
                database
        ).get('_id', ''),
        'is_done': True if request.form.get('is_done', '') else False,
        'section': request.form.get('section')
    }
    # update user's ticklist
    return [
        TickListProblem(p) for p in mongodb_controller.put_boulder_in_ticklist(boulder, current_user.id, database)
    ]
