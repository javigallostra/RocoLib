
from typing import List, Tuple
from pymongo.database import Database
from db.mongodb_controller import get_gyms, get_gym_walls
import bson


def is_gym_valid(gym_id: str, db: Database) -> Tuple[bool, dict]:
    """
    Check if the gym is valid via its id. 
    If contained in the database, it is valid.
    """
    if not gym_id:
        return False, dict(gym_id=f'Gym id is required')
    if not gym_id in [gym.get('id', '') for gym in get_gyms(db)]:
        return False, dict(gym_id=f'Gym {gym_id} not found')
    return True, dict()


def is_section_valid(gym_id: str, wall_section: str, db: Database) -> Tuple[bool, dict]:
    """
    Check if the section is valid via its image_path.
    If contained in the database, it is valid.
    """
    if not wall_section:
        return False, dict(wall_section=f'Wall section is required')        
    if not wall_section in [wall.get('image', '') for wall in get_gym_walls(gym_id, db)]:
        return False, dict(wall_section=f'Wall section {wall_section} not found')
    return True, dict()


def are_gym_and_section_valid(gym_id: str, wall_section: str, db: Database) -> Tuple[bool, dict]:
    """
    Validate that the provided gym and wall section pair are valid. 
    If the gym is contained in the database and the wall section is
    contained in the walls of the specified gym, the pair is valid.
    """
    errors = {}
    
    valid_gym, gym_errors = is_gym_valid(gym_id, db)
    if not valid_gym:
        errors |= gym_errors
    
    valid_section, section_errors = is_section_valid(gym_id, wall_section, db)
    if not valid_section:
        errors |= section_errors

    return valid_gym and valid_section, errors


def is_rating_valid(rating: int) -> Tuple[bool, dict]:
    """
    Validate that the provided rating is valid,
    which means an int between 0 and 5.

    :param rating: boulder rating
    :type rating: int
    :return: rating validity
    :rtype: bool
    """
    if type(rating) == int and rating in range(0, 6):
        return True, dict()
    return False, dict(rating=f'Invalid rating {rating}. Rating should be an int in the range [0, 5]')


def is_bson_id_valid(id: str) -> Tuple[bool, dict]:
    """
    Validate that the provided id is valid

    :param id: id to validate
    :type id: str
    :return: id validity
    :rtype: bool
    """
    if not id:
        return False, dict(bson_id=f'Id is required')
    if not bson.objectid.ObjectId.is_valid(id):
        return False, dict(bson_id=f'Invalid BSON Id format: {id}')
    return True, dict()
