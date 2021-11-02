
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