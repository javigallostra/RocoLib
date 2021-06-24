import json
from flask import url_for


def load_boulder_from_request(request):
    """
    Replace boulder data from valid Python to valid JS
    """
    return json.loads(
        request.form.get('boulder_data')
        .replace('\'', '"')
        .replace('True', 'true')
        .replace('False', 'false'))


def get_wall_image(gym, section, walls_path, static_assets_path='static'):
    return url_for(
        static_assets_path,
        filename='{}{}/{}.JPG'.format(walls_path, gym, section)
    )
