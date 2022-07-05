import os
import glob
import json
from typing import NoReturn, Union

from flask import Flask, render_template, request
from flask import session, send_from_directory, _app_ctx_stack, g
from flask_caching import Cache
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_swagger_ui import get_swaggerui_blueprint

from werkzeug.wrappers.response import Response

from api.blueprint import api_blueprint
from src.models import User
from src.config import *
from src.generate_open_api_spec import generate_api_docs
import src.utils as utils
import db.mongodb_controller as db_controller

import src.request_processor as request_processor

# create the application object
app = Flask(__name__)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "RocoLib API"
    }
)

app.register_blueprint(swaggerui_blueprint)
app.register_blueprint(api_blueprint)

# app.config.from_pyfile('config.py')
# Might have to change how this is computed
app.secret_key = b'\xf7\x81Q\x89}\x02\xff\x98<et^'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager(app)
login_manager.login_view = 'login'


def make_cache_key_create() -> str:
    return (request.path + get_gym()).encode('utf-8')


@app.before_request
def open_database_connection() -> None:
    """Open DDBB connection before request so that
    it can be accessed during the request processing"""
    g.db = utils.get_db_connection()


@app.teardown_appcontext
def close_db_connection(exception) -> None:
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'database'):
        top.database.client.close()


# user loading callback
@login_manager.user_loader
def load_user(user_id: str) -> Union[User, None]:
    return User.get_by_id(user_id, utils.get_db_connection())


# Load favicon
@app.route('/favicon.ico')
def favicon() -> Response:
    """Load page favicon

    :return: the favicon file
    :rtype: Response
    """
    return send_from_directory(
        os.path.join(app.root_path, 'static/images/favicon'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


# load languages files
LANG = {}
language_list = glob.glob("language/*.json")
for lang in language_list:
    lang_code = lang.split(os.path.sep)[1].split('.')[0]
    with open(lang, 'r', encoding='utf8') as file:
        LANG[lang_code] = json.loads(file.read())


@app.context_processor
def inject_langauge() -> dict:
    lang = utils.choose_language(request, LANG)
    return {**LANG[DEFAULT_LANG], **LANG[lang]}


def get_gym() -> str:
    """Get the current session's selected gym."""
    return request_processor.get_current_gym(session, g.db)


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    return request_processor.handle_home_request(request, session, g.db)


@app.route('/create')
@cache.cached(timeout=60 * 60, key_prefix=make_cache_key_create)
def create() -> str:
    return request_processor.handle_create_request(request, session, g.db)


@app.route('/create_boulder')
def create_boulder() -> str:
    return render_template('create_boulder.html')


@app.route('/create_route')
def create_route() -> str:
    return render_template('create_route.html')


@app.route('/explore')
def explore() -> str:
    return render_template('explore.html', walls=db_controller.get_gym_walls(get_gym(), g.db))


@app.route('/explore_boulders', methods=['GET', 'POST'])
def explore_boulders() -> str:
    return request_processor.handle_explore_boulders(request, session, g.db, current_user)


@app.route('/change_gym', methods=['POST'])
def change_gym_problem_list() -> str:
    return request_processor.handle_change_gym_problem_list_request(request, session, g.db, current_user)


@app.route('/rate_boulder', methods=['POST'])
def rate_boulder() -> Union[Response, NoReturn]:
    return request_processor.process_rate_boulder_request(request, session, g.db)


@app.route('/load_boulder', methods=['POST', 'GET'])
# @cache.cached(timeout=60*60, key_prefix=make_cache_key_boulder)
def load_boulder() -> Union[str, NoReturn]:
    return request_processor.process_load_boulder_request(request, session, g.db, app.static_folder)


@app.route('/load_next')
def load_next_problem():
    return request_processor.process_load_next_problem_request(request, session, g.db, app.static_folder)


@app.route('/load_previous')
def load_previous_problem():
    return request_processor.process_load_previous_problem_request(request, session, g.db, app.static_folder)


@app.route('/explore_routes')
def explore_routes() -> str:
    return render_template('explore_routes.html')


@app.route('/random_problem')
def random_problem() -> str:
    return request_processor.process_random_problem_request(request, session, g.db, app.static_folder)


@app.route('/about_us')
def render_about_us() -> str:
    return render_template('about_us.html')


@app.route('/walls/<string:wall_section>')
def wall_section(wall_section) -> str:
    return request_processor.process_wall_section_request(request, session, g.db, app.static_folder, wall_section)


@app.route('/save', methods=['POST'])
def save() -> Response:
    return request_processor.process_save_request(request, session, g.db)


@app.route('/save_boulder', methods=['POST'])
def save_boulder() -> Union[str, NoReturn]:
    return request_processor.process_save_boulder_request(request, current_user)


@app.route('/add_gym', methods=['GET', 'POST'])
@login_required
def add_gym() -> str:
    return render_template('add_new_gym.html')


# Login handlers
@app.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    return request_processor.process_login_request(request, g.db, current_user, login_user)


@app.route('/signup/', methods=['GET', 'POST'])
def show_signup_form() -> Union[str, Response]:
    return request_processor.process_signup_request(request, g.db, current_user, login_user)


@app.route('/logout')
def logout() -> Response:
    return request_processor.process_logout_request(logout_user)

# User related endpoints


@app.route('/tick_list', methods=['GET', 'POST'])
@login_required
def tick_list() -> Union[str, Response]:
    return request_processor.process_ticklist_request(request, session, g.db, current_user)


@app.route('/delete_ticklist_problem', methods=['POST'])
@login_required
def delete_ticklist_problem() -> Union[Response, NoReturn]:
    return request_processor.process_delete_ticklist_problem_request(request, g.db, current_user)


@app.route('/get_nearest_gym', methods=['POST'])
def get_nearest_gym() -> Response:
    return request_processor.process_get_nearest_gym_request(request, session, g.db)


@app.route('/contact', methods=['GET'])
def show_contact() -> Union[Response, NoReturn]:
    return render_template('contact.html')


@app.errorhandler(404)
def page_not_found(error) -> tuple[str, int]:
    # pylint: disable=no-member
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


@app.errorhandler(400)
def bad_request(error) -> tuple[str, int]:
    # pylint: disable=no-member
    app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/400.html'), 400


# start the server
if __name__ == '__main__':
    if GENERATE_API_DOCS:
        generate_api_docs(app)
    if RUN_SERVER:
        if DOCKER_ENV == "True":
            utils.set_creds_file(CREDS_DEV)
            app.run(debug=DEBUG, host='0.0.0.0', port=80)
        else:
            utils.set_creds_file(CREDS)
            app.run(debug=DEBUG, port=PORT)
