import argparse
import os

DEBUG = True

# gym name as command line args -> gym_code, gym_name

class Coordinates():
    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude

def is_image(filename):
    pass

def is_JPG(filename):
    pass

def convert_to_JPG(filename):
    pass

def move_to_gym_dir(images_path, filename):
    pass

def create_walls_collection(gym_code):
    pass

def create_boulders_collection(gym_code):
    pass

def add_gym_to_gyms_list(gym_code, gym_name, radius=0.02, coordinates=Coordinates()):
    pass

def add_new_gym(gym_code, gym_name, images_path, debug=False):
    # Required steps:
    # 1. Create folder
    # 2. Get wall images, tranform them if required,
    #    and move them to the gym's folder
    # 2. Create collections and fill data
    # 3. Add gym to walls collection
    if not debug:
        create_gym_folder(gym_code)
    if images_path:
        # Find all images, convert them to JPG and move them to the 
        # gym folder
        for filename in os.listdir(images_path):
            if is_image(filename):
                if not is_JPG(filename):
                    filename = convert_to_JPG(filename)
                move_to_gym_dir(filename)
    # Add gym to DDBB
    create_walls_collection(gym_code)
    create_boulders_collection(gym_code)
    add_gym_to_gyms_list(gym_code, gym_name)

def create_gym_folder(gym_code):
    """
    Create a new folder inside the wall images directory
    """
    os.makedirs(f"./static/images/walls/{gym_code}")

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
args = parser.parse_args()

if __name__ == "__main__":
    add_new_gym(args.code, args.name, args.images, debug=DEBUG)