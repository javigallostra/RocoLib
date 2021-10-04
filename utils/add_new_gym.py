import argparse
import os

# gym name as command line args -> gym_code, gym_name

def add_new_gym(gym_code, gym_name, images_path):
    # Required steps:
    # 1. Create folder
    # 2. Get wall images, tranform them if required,
    #    and move them to the gym's folder
    # 2. Create collections and fill data
    # 3. Add gym to walls collection
    create_gym_folder(gym_code)
    pass

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
    add_new_gym(args.code, args.name, args.images)