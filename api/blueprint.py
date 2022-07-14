from flask import Blueprint, send_from_directory, request, g, current_app
from flask_httpauth import HTTPTokenAuth
from werkzeug.wrappers.response import Response
from src.utils import get_db_connection
from src.models import User
from src.config import *

import api.api_request_processor as api_request_processor

API_VERSION = 'v1'

auth = HTTPTokenAuth(scheme='Bearer')

api_blueprint = Blueprint(
    'api_blueprint',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix=f'/api/{API_VERSION}'
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
  user = User.verify_auth_token(token, current_app, g.db)
  if user is None:
    return False
  g.user = user
  return True


@api_blueprint.before_request
def open_database_connection():
    """
    Open a new database connection before processing the request and store 
    it in the global request g object so that it can be accessed from within
    the request
    """
    g.db = get_db_connection()


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_gyms_request(g.db)


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
      - in: query
        name: latest
        schema:
          type: boolean
        description: if true, get only latest wall versions. Defaults to false
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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_gym_walls_request(request, g.db, gym_id)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_gym_pretty_name(g.db, gym_id)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_gym_wall_name(g.db, gym_id, wall_section)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_gym_boulders_request(g.db, gym_id)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_boulder_by_id_request(g.db, gym_id, boulder_id)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_boulder_by_name_request(g.db, gym_id, boulder_name)


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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_boulder_create_request(request, g.db, gym_id, wall_section)


@api_blueprint.route('/boulders/<string:gym_id>/<string:boulder_id>/rate', methods=['POST'])
def rate_boulder(gym_id: str, boulder_id: str) -> Response:
    """Rate a boulder problem
    ---
    post:
      tags:
        - Boulders
      parameters:
      - in: path
        schema: GymIDParameter
      - in: path
        schema: BoulderIDParameter
      requestBody:
        description: Boulder rating
        required: true
        content:
          application/json:
            schema: RateBoulderRequestBody
          application/x-www-form-urlencoded:
            schema: RateBoulderRequestBody
          text/json:
            schema: RateBoulderRequestBody
          text/plain:
            schema: RateBoulderRequestBody
      responses:
        201:
          description:
            Rating successful
          content:
            text/plain:
              schema: RateBoulderResponseBody
            text/json:
              schema: RateBoulderResponseBody
            application/json:
              schema: RateBoulderResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: RateBoulderErrorResponse
            text/json:
              schema: RateBoulderErrorResponse
            application/json:
              schema: RateBoulderErrorResponse
        404:
          description:
            Not found
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_rate_boulder_request(request, g.db, gym_id, boulder_id)


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
        401:
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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_new_user_request(request, g.db)


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
        401:
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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_auth_token_request(request, g.db, current_app)


@api_blueprint.route('/user/ticklist/boulder/done', methods=['POST'])
@auth.login_required
def mark_boulder_as_done() -> Response:
    """Mark a boulder problem as done
    ---
    post:
      security:
        - bearerAuth: []
      tags:
        - User
      requestBody:
        description: Boulder to mark as done
        required: true
        content:
          application/json:
            schema: MarkDoneBoulderRequestBody
          application/x-www-form-urlencoded:
            schema: MarkDoneBoulderRequestBody
          text/json:
            schema: MarkDoneBoulderRequestBody
          text/plain:
            schema: MarkDoneBoulderRequestBody
      responses:
        200:
          description:
            Mark boulder as done successful
          content:
            text/plain:
              schema: MarkDoneBoulderResponseBody
            text/json:
              schema: MarkDoneBoulderResponseBody
            application/json:
              schema: MarkDoneBoulderResponseBody
        400:
          description:
            Bad request
          content:
            text/plain:
              schema: MarkDoneBoulderErrorResponse
            text/json:
              schema: MarkDoneBoulderErrorResponse
            application/json:
              schema: MarkDoneBoulderErrorResponse
        404:
          description:
            Not found
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_mark_boulder_as_done_request(request, g.db, g.user)


@api_blueprint.route('/user/ticklist', methods=['GET'])
@auth.login_required
def get_user_ticklist() -> Response:
    """
    Get a user's ticklist
    ---
    get:
      security:
        - bearerAuth: []
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
              schema: TicklistError
            text/json:
              schema: TicklistError
            application/json:
              schema: TicklistError
        401:
          description:
            Invalid credentials
          content:
            text/plain:
              schema: TicklistError
            text/json:
              schema: TicklistError
            application/json:
              schema: TicklistError
        404:
          description:
            Not found
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_get_user_ticklist_request(g.db, g.user)


@api_blueprint.route('/user/test-auth', methods=['GET'])
@auth.login_required
def test_auth() -> Response:
    """
    Test the validity of a token
    ---
    get:
      security:
        - bearerAuth: []
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
        401:
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
          content:
            application/json:
              schema: NotFoundError
            text/plain:
              schema: NotFoundError
            text/json:
              schema: NotFoundError
        500:
          description:
            Server Error
    """
    return api_request_processor.process_test_auth_request(g.user)
