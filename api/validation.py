
from typing import List, Tuple
from pymongo.database import Database
from db.mongodb_controller import get_gyms, get_gym_walls

def is_gym_valid(gym_id: str, db: Database)-> bool:
    """
    Check if the gym is valid via its id. 
    If contained in the database, it is valid.
    """
    return gym_id in [gym.get('id', '') for gym in get_gyms(db)]

def is_section_valid(gym_id: str, section: str, db: Database)-> bool:
    """
    Check if the section is valid via its image_path.
    If contained in the database, it is valid.
    """
    # if is_gym_valid(gym_id, db):
    return section in [wall.get('image_path', '') for wall in get_gym_walls(gym_id, db)]
    # return False

def validate_gym_and_section(gym_id: str, wall_section: str, db: Database) -> Tuple[bool, List[str]]:
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
            {'wall_section': f'Wall section {wall_section} does not exist'}
        ) if not valid_section else None
    return valid_gym and valid_section, errors
