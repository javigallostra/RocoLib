from flask import Blueprint, jsonify, _app_ctx_stack, send_from_directory
import os
import pymongo
import db.mongodb_controller as db_controller

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


@api_blueprint.route('/gyms/list', methods=['GET'])
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
    return jsonify(db_controller.get_gyms(get_db()))

@api_blueprint.route('/docs/swagger.json')
def api_docs():
    """
    Swagger document endpoint
    """
    return send_from_directory('static','openapi/swagger.json')
