import argparse
import os
from typing import Optional
import pymongo

from PIL import Image
from shutil import copyfile


# TODO: warn user if gym name already exists
# TODO: check DDBB operation results

# gym name as command line args -> gym_code, gym_name, images_path

walls_path = './static/images/walls'
image_extensions = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')


class Coordinates():
    def __init__(self, latitude: Optional[float] = None, longitude: Optional[float] = None):
        self.latitude: float = latitude
        self.longitude: float = longitude

    def has_values(self) -> bool:
        return self.latitude is not None and self.longitude is not None

    def get_coords(self) -> list[float]:
        return [self.latitude, self.longitude]


def is_image(filename: str) -> bool:
    """
    Test if a file is an image
    """
    return filename.lower().endswith(image_extensions)


def is_JPG(filename: str) -> bool:
    """
    Test if an image is in JPG format
    """
    return filename.endswith('.JPG')


def convert_to_JPG(filename: str, gym_code=None, is_fullpath: bool = True) -> None:
    """
    Convert an image to JPG
    """
    if not is_fullpath:
        filename = f'{walls_path}/{gym_code}/{filename}'
    im = Image.open(filename)
    rgb_im = im.convert('RGB')
    rgb_im.save(f'{os.path.splitext(filename)[0]}.JPG')
    os.remove(filename)


def move_to_gym_dir(filename: str, images_path: str, gym_code: str):
    """
    Move a file from a source directory (images_path + filename) to
    the directory inside the application were wall images will be searched
    """
    return copyfile(f'{images_path}/{filename}', f'{walls_path}/{gym_code}/{filename}')


def create_walls_collection(gym_code: str, radius: float = 0.02) -> None:
    """
    Create the new gym collection and include its walls
    """
    with open('creds.txt') as f:
        creds = f.readline()
    myclient = pymongo.MongoClient(creds)
    db = myclient['RocoLib']
    gym_collection = db[f'{gym_code}_walls']
    # Prompt user for wall names
    for wall in os.listdir(f'{walls_path}/{gym_code}'):
        name = input(f'Wall name for image {wall}: ')
        wall_data = {
            'image': os.path.splitext(wall)[0],
            'name': name,
            'radius': radius,
            'latest': True
        }
        gym_collection.insert_one(wall_data)


def create_boulders_collection(gym_code) -> None:
    """
    Not sure this is required. The collection will be created
    when the first boulder is inserted.
    """
    pass


def add_gym_to_gyms_list(gym_code: str, gym_name: str, coordinates: Coordinates = Coordinates()) -> None:
    """
    Add the new gym to the list of supported gyms
    """
    with open('creds.txt') as f:
        creds = f.readline()
    myclient = pymongo.MongoClient(creds)
    db = myclient['RocoLib']
    walls_collection = db['walls']
    wall_data = {'name': gym_name, 'id': gym_code,
                 'coordinates': coordinates.get_coords()}
    walls_collection.insert_one(wall_data)


def add_new_gym(gym_code: str, gym_name: str, images_path: str, location: list[float]) -> None:
    """
    Add a new gym to the application. To do so, at least
    the gym_code and gym_name are required. The location and
    path to wall images is optional. The process consists in
    the following steps:
        1. Create new gym's dir inside the static folder
        2. Get wall images, tranform them if required,
           and move them to the gym's dir
        2. Create gym walls collections and add the
           specified walls
        3. Add gym to walls collection
    """

    # Local work
    print(f'Creating {gym_code} folder...')
    created = create_gym_folder(gym_code)
    if not created:
        return
    if images_path:
        # Find all images, convert them to JPG and move them to the
        # gym folder
        print(f'Adding images to folder...')
        for filename in os.listdir(images_path):
            if is_image(filename):
                new_path = move_to_gym_dir(filename, images_path, gym_code)
                if not is_JPG(new_path):
                    convert_to_JPG(new_path, is_fullpath=True)
    # Add gym to DDBB
    coords = Coordinates()
    if location:
        coords = Coordinates(location[0], location[1])
    print(f'Creating collection...')
    create_walls_collection(gym_code)
    create_boulders_collection(gym_code)
    print(f'Listing gym...')
    add_gym_to_gyms_list(gym_code, gym_name, coordinates=coords)
    print(f'Done! {gym_name} successfully created!')


def create_gym_folder(gym_code: str) -> bool:
    """
    Create a new folder inside the wall images directory
    """
    try:
        os.makedirs(f'./static/images/walls/{gym_code}')
        return True
    except FileExistsError:
        print('Gym code already in use, please use a different one')
    return False


parser = argparse.ArgumentParser(description='Rocolib gym creation tool')
parser.add_argument(
    '-c',
    '--code',
    help='New Gym internal code',
    type=str,
    required=True
)
parser.add_argument(
    '-n',
    '--name',
    help='New Gym name to display',
    type=str,
    required=True
)
parser.add_argument(
    '-i',
    '--images',
    help='Path to the folder that contains gym wall images',
    type=str,
    required=False
)
parser.add_argument(
    '-l',
    '--location',
    help='Gym coordinates',
    nargs=2,
    metavar=('latitude', 'longitude'),
    type=float,
    required=False
)
args = parser.parse_args()

if __name__ == '__main__':
    add_new_gym(args.code, args.name, args.images, args.location)
