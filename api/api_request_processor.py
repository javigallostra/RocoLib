import ast
import datetime
from distutils.log import error
import db.mongodb_controller as db_controller

from flask import jsonify
from marshmallow import ValidationError
from api.schemas import BoulderFields
from api.validation import is_bson_id_valid, is_gym_valid, is_rating_valid, are_gym_and_section_valid

from src.config import *
from src import ticklist_handler
from src.models import User
from src.utils import load_data

def process_get_gyms_request(db):
    return jsonify(dict(gyms=db_controller.get_gyms(db))), 200

def process_get_gym_walls_request(request, db, gym_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    latest = request.args.get('latest', False)
    return jsonify(dict(walls=db_controller.get_gym_walls(gym_id, db, latest=latest))), 200

def process_get_gym_pretty_name(db, gym_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(name=db_controller.get_gym_pretty_name(gym_id, db))), 200

def process_get_gym_wall_name(db, gym_id, wall_section):
    valid, errors = are_gym_and_section_valid(gym_id, wall_section, db)
    if not valid:
          return jsonify(dict(errors=errors)), 404
    return jsonify(dict(name=db_controller.get_wall_name(gym_id, wall_section, db))), 200

def process_get_gym_boulders_request(db, gym_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(boulders=db_controller.get_boulders(gym_id, db).get(ITEMS, []))), 200

def process_get_boulder_by_id_request(db, gym_id, boulder_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(boulder=db_controller.get_boulder_by_id(gym_id, boulder_id, db))), 200

def process_get_boulder_by_name_request(db, gym_id, boulder_name):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(boulder=db_controller.get_boulder_by_name(gym_id, boulder_name, db))), 200

def process_boulder_create_request(request, db, gym_id, wall_section):
    valid, errors = are_gym_and_section_valid(gym_id, wall_section, db)
    if not valid:
          return jsonify(dict(created=False, errors=errors)), 404

    if request.method == 'POST':
        boulder_fields = BoulderFields()
        # Get boulder data from request
        base_data = {
            boulder_fields.rating: 0,
            boulder_fields.raters: 0,
            boulder_fields.section: wall_section,
            boulder_fields.time: datetime.datetime.now().isoformat()}

        request_data, from_form = load_data(request)
        for key, val in request_data.items():
          base_data[key.lower()] = val
          if from_form and key.lower() == boulder_fields.holds:
            base_data[key.lower()] = ast.literal_eval(val)

        # Validate Boulder Schema
        try:
          from api.schemas import CreateBoulderRequestValidator
          # Will raise ValidationError if not valid
          _ = CreateBoulderRequestValidator().load(base_data)
          resp = db_controller.put_boulder(base_data, gym=gym_id, database=db)
          if resp is None:
              return jsonify(dict(created=False)), 500
          return jsonify(dict(created=True, _id=resp)), 201
        except ValidationError as err:
          return jsonify(dict(created=False, errors=err.messages)), 400

def process_rate_boulder_request(request, db, gym_id, boulder_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    
    if request.method == 'POST':
      data, _ = load_data(request)
      # validate gym
      if not is_gym_valid(gym_id, db):
        return jsonify(dict(rated=False, errors={'gym_id': 'Gym not found'})), 404
      # validate rating
      if not is_rating_valid(data.get('rating', -1)):
        return jsonify(dict(rated=False, errors={'rating': 'Rating not valid, should be an int between 0 and 5'})), 400
      if not is_bson_id_valid(boulder_id):
        return jsonify(dict(rated=False, errors={'boulder_id': 'Boulder ID not valid'})), 400

      boulder = db_controller.get_boulder_by_id(gym_id, boulder_id, db)

      if not bool(boulder):  # boulder is empty -> it wasn't found
        return jsonify(dict(rated=False, errors={'boulder_id': 'Boulder not found'})), 404

      # rate boulder, update stats
      boulder['rating'] = (boulder['rating'] * boulder['raters'] +
                           int(data.get('rating'))) / (boulder['raters'] + 1)
      boulder['raters'] += 1

      db_controller.update_boulder_by_id(
          gym=gym_id,
          boulder_id=boulder_id,
          data=boulder,
          database=db
      )

      return jsonify(dict(rated=True, _id=boulder_id)), 200
    return jsonify(dict(rated=False, errors={'method': 'Invalid HTTP method. This endpoint only accepts POST requests'})), 400

def process_new_user_request(request, db):
    # Some of this code can be extracted into a utility function
    data, _ = load_data(request)
    username = data.get('username', None)
    password = data.get('password', None)
    email = data.get('email', None)
    errors = {
        'username': 'Username is required',
        'password': 'Password is required',
        'email': 'Email is required'
    }
    if username is None or password is None or email is None:
        return jsonify(dict(errors=[errors[key] for key in errors.keys() if data.get(key, None) is None])), 400
    if User.get_user_by_username(username, db) is not None:
        return jsonify(dict(errors=['Username already exists'])), 400
    if User.get_user_by_email(email, db) is not None:
        return jsonify(dict(errors=['Email already exists'])), 400
    # Create and save user
    user = User(name=username, email=email)
    user.set_password(password)
    user.save(db)
    return jsonify({'username': user.name}), 201

def process_get_auth_token_request(request, db, current_app):
    user_data, _ = load_data(request)
    username = user_data.get('username', '')
    email = user_data.get('email', '')
    password = user_data.get('password')
    user = None
    if username:
      user = User.get_user_by_username(username, db)
    elif email:
      user = User.get_user_by_email(email, db)
    if user is not None and user.check_password(password):
        token = user.generate_auth_token(current_app)
        return jsonify(dict(token=token.decode('ascii'))), 200
    return jsonify(dict(error='Invalid credentials')), 401

def process_mark_boulder_as_done_request(request, db, user):
    if request.method == 'POST':
      data, _ = load_data(request)

      valid, errors = is_gym_valid(data.get('gym', ''), db)
      if not valid:
        return jsonify(errors=errors), 404


      if data.get('boulder_id', '') and data.get('gym', ''):

        db_boulder = db_controller.get_boulder_by_id(data.get('gym'), data.get('boulder_id'), db)

        if not db_boulder:
          return jsonify(
            dict(
                errors=dict(
                    boulder_id=f'Boulder {data.get("boulder_id")} for gym {data.get("gym")} not found'
                ), 
                marked_as_done=False)), 404
   
        db_boulder['iden'] = db_boulder.pop('_id')
        db_boulder['is_done'] = True

        # adds the boulder, it doesn't check if it exists
        updated_ticklist = db_controller.put_boulder_in_ticklist(
            db_boulder,
            user.id,
            db,
            mark_as_done_clicked=True
        )
        
        updated_boulder = [b for b in updated_ticklist if b['iden'] == db_boulder['iden']]

        if updated_boulder and updated_boulder[0]['is_done']:
          return jsonify(dict(boulder_id=db_boulder.get('iden'), marked_as_done=True)), 200
        else:
          return jsonify(dict(errors=dict(boulder_id='Boulder not found'), marked_as_done=False)), 404

      # detect missing fields and add as errors
      errors = dict()
      if not data.get('boulder_id', ''):
        errors['boulder_id'] = 'Boulder id is required'
      if not data.get('gym', ''):
        errors['gym'] = 'Gym is required'
      return jsonify(dict(dict(errors=errors), marked_as_done=False)), 400

def process_get_user_ticklist_request(db, user):
    # user has been retrieved by the authentication callback
    # and stored in the g object, which is accessible and global
    # while processing the request
    ticklist_boulders, _ = ticklist_handler.load_user_ticklist(
        user, db)
    return jsonify(dict(boulders=ticklist_boulders)), 200

def process_test_auth_request(user):
    return jsonify(dict(data=f'Hello {user.name}')), 200
