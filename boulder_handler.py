from werkzeug.utils import secure_filename

import db.mongodb_controller as db_controller
# pylint: disable=unused-wildcard-import
from utils.utils import *
from config import *
from models import BoulderProblem

import datetime


def get_boulders_list(filters, gym, db) -> list:
    """
    Given a gym and a set of filters return the list of
    boulders that match the specified criteria.
    """
    data = db_controller.get_boulders_filtered(
        gym=gym,
        database=db,
        conditions=filters,
        equals=EQUALS,
        ranged=RANGE,
        contains=CONTAINS
    )
    # Map and complete boulder data
    boulders = [BoulderProblem(db, gym, b_info)
                for b_info in data[ITEMS]]
    return sorted(
        boulders,
        key=lambda boulder: datetime.datetime.strptime(
            boulder.time, '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True
    )


def get_boulder_by_name(name, gym, db) -> BoulderProblem:
    boulder_data = db_controller.get_boulder_by_name(
        gym=gym,
        name=name,
        database=db
    )
    return BoulderProblem(db, gym, boulder_data)


def update_boulder_by_id(boulder, gym, db):
    return db_controller.update_boulder_by_id(
        gym=gym,
        boulder_id=boulder.get_id(),
        data=boulder.serialize_for_db(),
        database=db
    )

def load_boulder_from_request(request, gym, db) -> BoulderProblem:
    boulder_data = parse_boulder_from_request(request)
    gym = boulder_data.pop('gym', gym)
    return BoulderProblem(db, gym, boulder_data)

def create_boulder(data, gym, db):
    db_controller.put_boulder(data, gym, db)