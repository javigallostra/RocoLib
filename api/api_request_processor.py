import ast
import datetime
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


def process_get_gym_circuits_request(db, gym_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(circuits=db_controller.get_circuits(gym_id, db).get(ITEMS, []))), 200

def process_get_circuit_by_id_request(db, gym_id, circuit_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404

    circuit = db_controller.get_circuit_by_id(gym_id, circuit_id, db)
    if not bool(circuit):
        return jsonify(errors=dict(circuit_id=f'Circuit with id {circuit_id} not found on gym {gym_id}')), 404

    return jsonify(dict(circuit=circuit)), 200


def process_get_circuit_by_name_request(db, gym_id, circuit_name):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404

    circuit = db_controller.get_circuit_by_name(gym_id, circuit_name, db)
    if not bool(circuit):
        return jsonify(errors=dict(circuit_id=f'circuit with name {circuit_name} not found on gym {gym_id}')), 404

    return jsonify(dict(circuit=circuit)), 200


def process_circuit_create_request(request, db, gym_id, wall_section):
    valid, errors = are_gym_and_section_valid(gym_id, wall_section, db)
    if not valid:
        return jsonify(dict(errors=errors)), 404

    if request.method == 'POST':
        circuit_fields = BoulderFields()
        # Get circuit data from request
        base_data = {
            circuit_fields.rating: 0,
            circuit_fields.raters: 0,
            circuit_fields.section: wall_section,
            circuit_fields.time: datetime.datetime.now().isoformat()}

        request_data, from_form = load_data(request)
        for key, val in request_data.items():
          base_data[key.lower()] = val
          if from_form and key.lower() == circuit_fields.holds:
            base_data[key.lower()] = ast.literal_eval(val)

        # Validate Circuit Schema
        try:
          from api.schemas import CreateCircuitRequestValidator
          # Will raise ValidationError if not valid
          _ = CreateCircuitRequestValidator().load(base_data)
          resp = db_controller.put_circuit(base_data, gym=gym_id, database=db)
          if resp is None:
              return jsonify(dict(errors=dict(message='Something went wrong creating the circuit'))), 500
          return jsonify(dict(created=True, _id=resp)), 201
        except ValidationError as err:
          return jsonify(dict(errors=err.normalized_messages())), 400

def process_get_gym_boulders_request(db, gym_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404
    return jsonify(dict(boulders=db_controller.get_boulders(gym_id, db).get(ITEMS, []))), 200


def process_get_boulder_by_id_request(db, gym_id, boulder_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404

    boulder = db_controller.get_boulder_by_id(gym_id, boulder_id, db)
    if not bool(boulder):
        return jsonify(errors=dict(boulder_id=f'Boulder with id {boulder_id} not found on gym {gym_id}')), 404

    return jsonify(dict(boulder=boulder)), 200


def process_get_boulder_by_name_request(db, gym_id, boulder_name):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404

    boulder = db_controller.get_boulder_by_name(gym_id, boulder_name, db)
    if not bool(boulder):
        return jsonify(errors=dict(boulder_id=f'Boulder with name {boulder_name} not found on gym {gym_id}')), 404

    return jsonify(dict(boulder=boulder)), 200


def process_boulder_create_request(request, db, gym_id, wall_section):
    valid, errors = are_gym_and_section_valid(gym_id, wall_section, db)
    if not valid:
        return jsonify(dict(errors=errors)), 404

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
              return jsonify(dict(errors=dict(message='Something went wrong creating the boulder'))), 500
          return jsonify(dict(created=True, _id=resp)), 201
        except ValidationError as err:
          return jsonify(dict(errors=err.normalized_messages())), 400


def process_rate_boulder_request(request, db, gym_id, boulder_id):
    valid, errors = is_gym_valid(gym_id, db)
    if not valid:
        return jsonify(errors=errors), 404

    if request.method == 'POST':
        data, _ = load_data(request)
        # validate gym
        valid, errors = is_gym_valid(gym_id, db)
        if not valid:
            return jsonify(dict(errors=errors)), 404
        # validate rating
        valid, errors = is_rating_valid(data.get('rating', ''))
        if not valid:
            return jsonify(dict(errors=errors)), 400
        # validate id
        valid, errors = is_bson_id_valid(boulder_id)
        if not valid:
            return jsonify(dict(errors=errors)), 400

        boulder = db_controller.get_boulder_by_id(gym_id, boulder_id, db)

        if not bool(boulder):  # boulder is empty -> it wasn't found
            return jsonify(dict(errors={'boulder_id': f'Boulder with id {boulder_id} not found'})), 404

        # rate boulder, update stats
        boulder['rating'] = (boulder['rating'] * boulder['raters'] +
                             int(data.get('rating'))) / (boulder['raters'] + 1)
        boulder['raters'] += 1

        db_controller.update_boulder_by_id(
            gym=gym_id,
            boulder_id=boulder_id,
            boulder_data=boulder,
            database=db
        )

        return jsonify(dict(rated=True, _id=boulder_id)), 200
    return jsonify(dict(errors={'method': 'Invalid HTTP method. This endpoint only accepts POST requests'})), 400


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
        return jsonify(dict(errors={key: errors[key] for key in errors.keys() if data.get(key, None) is None})), 400
    if User.get_user_by_username(username, db) is not None:
        return jsonify(dict(errors={'username': f'Username {username} already exists'})), 400
    if User.get_user_by_email(email, db) is not None:
        return jsonify(dict(errors={'email': f'Email {email} already exists'})), 400
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
    return jsonify(dict(errors={'message': 'Authentication error. Invalid credentials'})), 400


def process_mark_boulder_as_done_request(request, db, user):
    if request.method == 'POST':
      data, _ = load_data(request)

      # detect missing fields and add as errors
      errors = dict()
      if not data.get('boulder_id', ''):
        errors['boulder_id'] = 'Boulder id is required'
      if not data.get('gym', ''):
        errors['gym'] = 'Gym is required'
      if bool(errors):
          return jsonify(dict(errors=errors)), 400

      valid, errors = is_gym_valid(data.get('gym', ''), db)
      if not valid:
        return jsonify(errors=errors), 404

      db_boulder = db_controller.get_boulder_by_id(
          data.get('gym'), data.get('boulder_id'), db)

      if not bool(db_boulder):
          return jsonify(
              dict(
                  errors=dict(
                      boulder_id=f'Boulder {data.get("boulder_id")} for gym {data.get("gym")} not found'
                  ))), 404

      db_boulder['iden'] = db_boulder.pop('_id')
      db_boulder['is_done'] = True

      # adds the boulder, it doesn't check if it exists
      updated_ticklist = db_controller.put_boulder_in_ticklist(
          db_boulder,
          user.id,
          db,
          mark_as_done_clicked=True
      )

      updated_boulder = [
          b for b in updated_ticklist if b['iden'] == db_boulder['iden']]

      if updated_boulder and updated_boulder[0]['is_done']:
          return jsonify(dict(boulder_id=db_boulder.get('iden'), marked_as_done=True)), 200
      else:
          return jsonify(dict(errors=dict(boulder_id=f'Could not update boulder with id {data.get("boulder_id")}'))), 500


def process_get_user_ticklist_request(db, user):
    # user has been retrieved by the authentication callback
    # and stored in the g object, which is accessible and global
    # while processing the request
    ticklist_boulders, _ = ticklist_handler.load_user_ticklist(
        user, db)
    return jsonify(dict(boulders=ticklist_boulders)), 200


def process_test_auth_request(user):
    return jsonify(dict(data=f'Hello {user.name}')), 200


def process_get_user_preferences_request(user):
    return jsonify(user.preferences.serialize(ignore_keys=('_id', 'user_id'))), 200
