import argparse
import pymongo
import shutil


# TODO: warn user if gym name already exists
# TODO: check DDBB operation results

# gym name as command line args -> gym_code, gym_name, images_path

walls_path = './static/images/walls'


def delete_walls_collection(gym_code: str) -> None:
    """
    Create the new gym collection and include its walls
    """
    with open('creds.txt') as f:
        creds = f.readline()
    myclient = pymongo.MongoClient(creds)
    db = myclient['RocoLib']
    gym_walls_collection = db[f'{gym_code}_walls']
    return gym_walls_collection.drop()


def delete_boulders_collection(gym_code: str) -> None:
    """
    Delete the whole boulder collection from the given gym
    """
    with open('creds.txt') as f:
        creds = f.readline()
    myclient = pymongo.MongoClient(creds)
    db = myclient['RocoLib']
    boulders_collection = db[f'{gym_code}_boulders']
    return boulders_collection.drop()


def delete_gym_from_gyms_list(gym_code: str) -> None:
    """
    Delete the gym from the list of supported gyms
    """
    with open('creds.txt') as f:
        creds = f.readline()
    myclient = pymongo.MongoClient(creds)
    db = myclient['RocoLib']
    walls_collection = db['walls']
    wall_to_delete = {'id': gym_code}
    walls_collection.delete_one(wall_to_delete)


def delete_gym_folder(gym_code: str) -> None:
    """
    Delete the gym static folder and its contents
    """
    shutil.rmtree(f'{walls_path}/{gym_code}')


def delete_gym(gym_code: str) -> None:
    """
    Delete a gym and its related content from the DDBB

    The related content includes boulders and walls data.
    Also remove the gym from the gym list.
    """
    sure = input(
        'This action cannot be undone. Are you sure you want to proceed? [Y/N]: ')
    if sure == 'Y':
        print('Deleting folder...')
        delete_gym_folder(gym_code)
        print('Deleting walls collection...')
        delete_walls_collection(gym_code)
        print('Deleting problems collection...')
        delete_boulders_collection(gym_code)
        print('Unlisting gym...')
        delete_gym_from_gyms_list(gym_code)
        print(f'Done! {gym_code} has been permanently removed.')


parser = argparse.ArgumentParser(description='Rocolib gym deletion tool')
parser.add_argument(
    '-c',
    '--code',
    help='Gym internal code',
    type=str,
    required=True
)

args = parser.parse_args()

if __name__ == '__main__':
    delete_gym(args.code)
