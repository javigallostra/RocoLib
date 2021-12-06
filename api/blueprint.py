from typing import Tuple
from flask import Blueprint, jsonify, send_from_directory, request, g, current_app
from flask_httpauth import HTTPTokenAuth
from marshmallow import ValidationError
import json
import ast
import datetime
from werkzeug.wrappers.response import Response
import db.mongodb_controller as db_controller
from api.validation import validate_gym_and_section
from api.schemas import BoulderFields
from utils.utils import get_db
from models import User
import ticklist_handler
from utils.utils import load_data


auth = HTTPTokenAuth(scheme='Bearer')

api_blueprint = Blueprint(
    'api_blueprint',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/api'
)


@auth.verify_token
def verify_token(token: str) -> bool:
  """
  Validate the token and return a boolean balue indicating whether the token is valid

  :param token: token to validate
  :type token: str
  :return: Token validity. True if valid, False otherwise
  :rtype: bool
  """
  user = User.verify_auth_token(token, current_app, get_db())
  if user is None:
    return False
  g.user = user
  return True


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


@api_blueprint.route('/user/signup', methods=['POST'])
def new_user() -> Response:
    """Create a new user.
    ---
    post:
      tags:
        - User
      requestBody:
        description: User Sign Up request body
        required: true
        content:
          application/json:
            schema: SignUpRequestBody
          application/x-www-form-urlencoded:
            schema: SignUpRequestBody
          text/json:
            schema: SignUpRequestBody
          text/plain:
            schema: SignUpRequestBody
      responses:
        200:
          description:
            User creation successful
          content:
            text/plain:
              schema: SignUpResponseBody
            text/json:
              schema: SignUpResponseBody
            application/json:
              schema: SignUpResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: SignUpErrorResponse
            text/json:
              schema: SignUpErrorResponse
            application/json:
              schema: SignUpErrorResponse
        400:
          description:
            Invalid credentials
          content:
            text/plain:
              schema: SignUpErrorResponse
            text/json:
              schema: SignUpErrorResponse
            application/json:
              schema: SignUpErrorResponse
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
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
    if User.get_user_by_username(username, get_db()) is not None:
        return jsonify(dict(errors=['Username already exists'])), 400
    if User.get_user_by_email(email, get_db()) is not None:
        return jsonify(dict(errors=['Email already exists'])), 400
    # Create and save user
    user = User(name=username, email=email)
    user.set_password(password)
    user.save(get_db())
    return jsonify({'username': user.name}), 201


@api_blueprint.route('/user/auth', methods=['POST'])
def get_auth_token() -> Response:
    """
    Given a username/email and a password, get an auth token if the user exists
    and the credentials are valid.
    ---
    post:
      tags:
        - User
      requestBody:
        description: Authentication request body
        required: true
        content:
          application/json:
            schema: AuthenticationRequestBody
          application/x-www-form-urlencoded:
            schema: AuthenticationRequestBody
          text/json:
            schema: AuthenticationRequestBody
          text/plain:
            schema: AuthenticationRequestBody
      responses:
        200:
          description:
            Authentication successful
          content:
            text/plain:
              schema: AuthenticationResponseBody
            text/json:
              schema: AuthenticationResponseBody
            application/json:
              schema: AuthenticationResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: AuthenticationErrorResponse
            text/json:
              schema: AuthenticationErrorResponse
            application/json:
              schema: AuthenticationErrorResponse
        400:
          description:
            Invalid credentials
          content:
            text/plain:
              schema: AuthenticationErrorResponse
            text/json:
              schema: AuthenticationErrorResponse
            application/json:
              schema: AuthenticationErrorResponse
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    user_data, _ = load_data(request)
    username = user_data.get('username', '')
    email = user_data.get('email', '')
    password = user_data.get('password')
    user = None
    if username:
      user = User.get_user_by_username(username, get_db())
    elif email:
      user = User.get_user_by_email(email, get_db())
    if user is not None and user.check_password(password):
        token = user.generate_auth_token(current_app)
        return jsonify(dict(token=token.decode('ascii'))), 200
    return jsonify(dict(error='Invalid credentials')), 401


@api_blueprint.route('/user/ticklist', methods=['GET'])
@auth.login_required
def get_user_ticklist() -> Response:
    """
    Gat a user's ticklist
    ---
    get:
      tags:
        - User
      responses:
        200:
          description:
            Ticklist retrieval successful
          content:
            text/plain:
              schema: TicklistResponseBody
            text/json:
              schema: TicklistResponseBody
            application/json:
              schema: TicklistResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: TicklistErrorResponse
            text/json:
              schema: TicklistErrorResponse
            application/json:
              schema: TicklistErrorResponse
        400:
          description:
            Invalid credentials
          content:
            text/plain:
              schema: TicklistErrorResponse
            text/json:
              schema: TicklistErrorResponse
            application/json:
              schema: TicklistErrorResponse
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    # user has been retrieved by the authentication callback
    # and stored in the g object, which is accessible and global
    # while processing the request
    ticklist_boulders, _ = ticklist_handler.load_user_ticklist(
        g.user, get_db())
    return jsonify(dict(boulders=ticklist_boulders)), 200


@api_blueprint.route('/user/resource', methods=['GET'])
@auth.login_required
def get_resource() -> Response:
    """
    Test the validity of a token
    ---
    get:
      tags:
        - User
      responses:
        200:
          description:
            Authentication successful
          content:
            text/plain:
              schema: TestTokenResponseBody
            text/json:
              schema: TestTokenResponseBody
            application/json:
              schema: TestTokenResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: TestTokenErrorResponse
            text/json:
              schema: TestTokenErrorResponse
            application/json:
              schema: TestTokenErrorResponse
        400:
          description:
            Invalid credentials
          content:
            text/plain:
              schema: TestTokenErrorResponse
            text/json:
              schema: TestTokenErrorResponse
            application/json:
              schema: TestTokenErrorResponse
        404:
          description:
            Not found
        500:
          description:
            Server Error
    """
    return jsonify(dict(data=f'Hello {g.user.name}')), 200
