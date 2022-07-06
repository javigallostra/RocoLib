
from typing import List, Tuple
from pymongo.database import Database
from db.mongodb_controller import get_gyms, get_gym_walls
import bson


def is_gym_valid(gym_id: str, db: Database) -> Tuple[bool, List[dict]]:
    """
    Check if the gym is valid via its id. 
    If contained in the database, it is valid.
    """
    if not gym_id in [gym.get('id', '') for gym in get_gyms(db)]:
        return False, [dict(gym_id='Gym not found')]
    return True, []


def is_section_valid(gym_id: str, wall_section: str, db: Database) -> Tuple[bool, List[dict]]:
    """
    Check if the section is valid via its image_path.
    If contained in the database, it is valid.
    """
    if not wall_section in [wall.get('image', '') for wall in get_gym_walls(gym_id, db)]:
        return False, [dict(wall_section='Wall section not found')]
    return True, []
    # return False


def validate_gym_and_section(gym_id: str, wall_section: str, db: Database) -> Tuple[bool, List[dict]]:
    """
    Validate that the provided gym and wall section pair are valid. 
    If the gym is contained in the database and the wall section is
    contained in the walls of the specified gym, the pair is valid.
    """
    valid_gym = is_gym_valid(gym_id, db)
    valid_section = is_section_valid(gym_id, wall_section, db)
    errors = []
    if not valid_gym or not valid_section:
        errors.append(
            {'gym_id': f'Gym {gym_id} does not exist'}
        ) if not valid_gym else None
        errors.append(
            {'wall_section': f'Wall section {wall_section} does not exist in gym {gym_id}'}
        ) if not valid_section else None
    return valid_gym and valid_section, errors

def is_rating_valid(rating: int) -> Tuple[bool, List[dict]]:
    """
    Validate that the provided rating is valid,
    which means an int between 0 and 5.

    :param rating: boulder rating
    :type rating: int
    :return: rating validity
    :rtype: bool
    """
    if rating in range(0, 6) and type(rating) == int:
        return True, []
    return False, [dict(rating='Invalid rating. Rating should be an int in the range [0, 5]')]

def is_bson_id_valid(id: str) -> Tuple[bool, List[dict]]:
    """
    Validate that the provided id is valid

    :param id: id to validate
    :type id: str
    :return: id validity
    :rtype: bool
    """
    if not bson.objectid.ObjectId.is_valid(id):
        return False, [dict(bson_id='Invalid BSON Id format')]
    return True, []