from PIL import Image, ExifTags
import os


import argparse

parser = argparse.ArgumentParser(
    description='Rotate image according to EXIF metadata')
parser.add_argument('--directory', '-d', type=str,
                    help='image directory')


def main(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    for filepath in files:
        print("Processing image: {}".format(filepath))
        try:
            image = Image.open(filepath)
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = dict(image._getexif().items())

            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
            image.save(filepath)
            image.close()

        except (AttributeError, KeyError, IndexError):
            # cases: image don't have getexif
            pass


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.directory)
