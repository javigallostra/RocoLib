import json
from flask import Blueprint, jsonify, _app_ctx_stack, send_from_directory, request
import os
import ast
import datetime
import pymongo
import db.mongodb_controller as db_controller
from marshmallow import ValidationError


api_blueprint = Blueprint(
    'api_blueprint',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/api'
)


def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'database'):
        client = pymongo.MongoClient(
            get_creds(),
            connectTimeoutMS=30000,
            socketTimeoutMS=None,
            # socketKeepAlive=True,
            connect=False,
            maxPoolsize=1)
        top.database = client["RocoLib"]
    return top.database


def get_creds():
    creds = None
    if os.path.isfile('creds.txt'):
        with open('creds.txt', 'r') as f:
            creds = f.readline()
    else:
        try:
            creds = os.environ['MONGO_DB']
        except:
            pass
    return creds


@api_blueprint.route('/docs/swagger.json')
def api_docs():
    """
    Raw swagger document endpoint
    """
    return send_from_directory('static', 'swagger/swagger.json')


@api_blueprint.route('/gym/list', methods=['GET'])
def get_gyms():
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
    return jsonify(dict(gyms=db_controller.get_gyms(get_db())))


@api_blueprint.route('/gym/<string:gym_id>/walls', methods=['GET'])
def get_gym_walls(gym_id):
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
    return jsonify(dict(walls=db_controller.get_gym_walls(gym_id, get_db())))


@api_blueprint.route('/gym/<string:gym_id>/name', methods=['GET'])
def get_gym_pretty_name(gym_id):
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
    return jsonify(dict(name=db_controller.get_gym_pretty_name(gym_id, get_db())))


@api_blueprint.route('/gym/<string:gym_id>/<string:wall_section>/name', methods=['GET'])
def get_gym_wall_name(gym_id, wall_section):
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
    return jsonify(dict(name=db_controller.get_wall_name(gym_id, wall_section, get_db())))


@api_blueprint.route('/boulders/<string:gym_id>/list', methods=['GET'])
def get_gym_boulders(gym_id):
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
    return jsonify(dict(boulders=db_controller.get_boulders(gym_id, get_db()).get('Items', [])))


@api_blueprint.route('/boulders/<string:gym_id>/<string:wall_section>/create', methods=['POST'])
def boulder_create(gym_id, wall_section):
    """Create a new boulder
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
        200:
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
    # TODO: Validate gym and section
    if request.method == 'POST':
        request.get_data()
        data = {'rating': 0, 'raters': 0, 'section': wall_section}
        if request.json is not None:
          for key, val in request.json.items():
              data[key.lower()] = val
        if request.form is not None:
          for key, val in request.form.items():
              data[key.lower()] = val
              if key.lower() == 'holds':
                  data[key.lower()] = ast.literal_eval(val)
        if request.data is not None:
          request_data = json.loads(request.data)
          for key, val in request_data.items():
              data[key.lower()] = val
        data['time'] = datetime.datetime.now().isoformat()
        # Validate Boulder Schema
        try:
          from api.schemas import CreateBoulderRequestValidator
          _ = CreateBoulderRequestValidator().load(data)
          resp = db_controller.put_boulder(data, gym=gym_id, database=get_db())
          if resp is not None:
            return jsonify(dict(created=True, _id=resp))
          return jsonify(dict(created=False))
        except ValidationError as err:
          return jsonify(dict(created=False, errors=err.messages)), 400
