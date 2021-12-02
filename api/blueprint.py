from typing import Tuple
from flask import Blueprint, jsonify, send_from_directory, request, g, current_app
import json
import ast
import datetime
from flask.wrappers import Request
# from flask_login.utils import login_user, current_user
from werkzeug.wrappers.response import Response
import db.mongodb_controller as db_controller
from marshmallow import ValidationError
from api.validation import validate_gym_and_section
from api.schemas import BoulderFields
from utils.utils import get_db
from models import User
from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()

api_blueprint = Blueprint(
    'api_blueprint',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/api'
)


def load_data(request: Request) -> Tuple[dict, bool]:
  """
  Load data from the request body into a dict and return it
  """
  # Handle the different content types
  request.get_data()  # required?
  if request.data is not None:
    return json.loads(request.data), False
  elif request.form is not None:
    return request.form, True
  elif request.json is not None:
    return request.json, False
  else:
    return dict(), False


@api_blueprint.route('/docs/swagger.json')
def api_docs() -> Response:
    """
    Raw swagger document endpoint
    """
    return send_from_directory('static', 'swagger/swagger.json')


@api_blueprint.route('/gym/list', methods=['GET'])
def get_gyms() -> Response:
    """Gym list.
    ---
    get:
      tags:
        - Gyms
      responses:
        200:
          description:
            List of gyms
          content:
            application/json:
              schema: GymListSchema
            text/plain:
              schema: GymListSchema
            text/json:
              schema: GymListSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(gyms=db_controller.get_gyms(get_db()))), 200


@api_blueprint.route('/gym/<string:gym_id>/walls', methods=['GET'])
def get_gym_walls(gym_id: str) -> Response:
    """Walls associated to the given gym.
    ---
    get:
      tags:
        - Gyms
      parameters:
      - in: path
        schema: GymIDParameter
      responses:
        200:
          description:
            List of walls associated to the specified gym
          content:
            application/json:
              schema: WallListSchema
            text/plain:
              schema: WallListSchema
            text/json:
              schema: WallListSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(walls=db_controller.get_gym_walls(gym_id, get_db()))), 200


@api_blueprint.route('/gym/<string:gym_id>/name', methods=['GET'])
def get_gym_pretty_name(gym_id: str) -> Response:
    """Given a gym id get its display name
    ---
    get:
      tags:
        - Gyms
      parameters:
      - in: path
        schema: GymIDParameter
      responses:
        200:
          description:
            Gym name
          content:
            application/json:
              schema: GymNameSchema
            text/plain:
              schema: GymNameSchema
            text/json:
              schema: GymNameSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(name=db_controller.get_gym_pretty_name(gym_id, get_db()))), 200


@api_blueprint.route('/gym/<string:gym_id>/<string:wall_section>/name', methods=['GET'])
def get_gym_wall_name(gym_id: str, wall_section: str) -> Response:
    """Get a wall name given the gym and the section
    ---
    get:
      tags:
        - Gyms
      parameters:
      - in: path
        schema: GymIDParameter
      - in: path
        schema: WallSectionParameter
      responses:
        200:
          description:
            Wall name
          content:
            application/json:
              schema: WallNameSchema
            text/plain:
              schema: WallNameSchema
            text/json:
              schema: WallNameSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(name=db_controller.get_wall_name(gym_id, wall_section, get_db()))), 200


@api_blueprint.route('/boulders/<string:gym_id>/list', methods=['GET'])
def get_gym_boulders(gym_id: str) -> Response:
    """Boulders associated to the given gym.
    ---
    get:
      tags:
        - Boulders
      parameters:
      - in: path
        schema: GymIDParameter
      responses:
        200:
          description:
            List of gym boulders
          content:
            application/json:
              schema: GymBoulderListSchema
            text/plain:
              schema: GymBoulderListSchema
            text/json:
              schema: GymBoulderListSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(boulders=db_controller.get_boulders(gym_id, get_db()).get('Items', []))), 200


@api_blueprint.route('/boulders/<string:gym_id>/<string:boulder_id>', methods=['GET'])
def get_boulder_by_id(gym_id: str, boulder_id: str) -> Response:
    """Get boulder by id.
    ---
    get:
      tags:
        - Boulders
      parameters:
      - in: path
        schema: GymIDParameter
      - in: path
        schema: BoulderIDParameter
      responses:
        200:
          description:
            Boulder data for the specified problem
          content:
            application/json:
              schema: BoulderSchema
            text/plain:
              schema: BoulderSchema
            text/json:
              schema: BoulderSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(boulder=db_controller.get_boulder_by_id(gym_id, boulder_id, get_db()))), 200


@api_blueprint.route('/boulders/<string:gym_id>/name/<string:boulder_name>', methods=['GET'])
def get_boulder_by_name(gym_id: str, boulder_name: str) -> Response:
    """Get boulder by name.
    ---
    get:
      tags:
        - Boulders
      parameters:
      - in: path
        schema: GymIDParameter
      - in: path
        schema: BoulderNameParameter
      responses:
        200:
          description:
            Boulder data for the specified problem
          content:
            application/json:
              schema: BoulderSchema
            text/plain:
              schema: BoulderSchema
            text/json:
              schema: BoulderSchema
        400:
          description:
            Bad request
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(boulder=db_controller.get_boulder_by_name(gym_id, boulder_name, get_db()))), 200


@api_blueprint.route('/boulders/<string:gym_id>/<string:wall_section>/create', methods=['POST'])
def boulder_create(gym_id: str, wall_section: str) -> Response:
    """Create a new boulder linked to the given gym and wall section
    ---
    post:
      tags:
        - Boulders
      parameters:
      - in: path
        schema: GymIDParameter
      - in: path
        schema: WallSectionParameter
      requestBody:
        description: Create boulder request body
        required: true
        content:
          application/json:
            schema: CreateBoulderRequestBody
          application/x-www-form-urlencoded:
            schema: CreateBoulderRequestBody
          text/json:
            schema: CreateBoulderRequestBody
          text/plain:
            schema: CreateBoulderRequestBody
      responses:
        201:
          description:
            Creation successful
          content:
            text/plain:
              schema: CreateBoulderResponseBody
            text/json:
              schema: CreateBoulderResponseBody
            application/json:
              schema: CreateBoulderResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: CreateBoulderErrorResponse
            text/json:
              schema: CreateBoulderErrorResponse
            application/json:
              schema: CreateBoulderErrorResponse
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    if request.method == 'POST':
        # Validate gym and wall section
        db = get_db()
        boulder_fields = BoulderFields()
        valid, errors = validate_gym_and_section(gym_id, wall_section, db)
        if not valid:
          return jsonify(dict(created=False, errors=errors)), 404
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

# User related endpoints
@api_blueprint.route('/user/signup', methods=['POST'])
def new_user() -> Response:
    """
    Create a new user.
    """
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    if username is None or password is None or email is None:
        pass  # return 400
    if User.query.filter_by(username=username).first() is not None:
        pass  # return 400 "existing user"
    user = User.get_user_by_email(email, get_db())
    if user is not None:
        # return 400 "existing email"
        error = f'The email {email} is already registered'
    else:
      # Create and save user
      user = User(name=username, email=email)
      user.set_password(password)
      user.save(get_db())
      # Keep user logged in
      # login_user(user, remember=True)
      return jsonify({'username': user.name}), 201


@api_blueprint.route('/token')
@auth.login_required
def get_auth_token() -> Response:
    token = g.user.generate_auth_token(current_app)
    return jsonify({ 'token': token.decode('ascii') }), 200

@api_blueprint.route('/resource')
@auth.login_required
def get_resource() -> Response:
    return jsonify({'data': f'Hello {g.user.name}'}), 200


@auth.verify_password
def verify_password(username_or_token: str, password: str) -> bool:
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token, current_app, get_db())
    if not user:
      user = User.get_user_by_username(username_or_token, get_db())
      if not user or not user.check_password(password):
          return False
    g.user = user
    return True
