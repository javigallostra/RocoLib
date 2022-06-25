import os
import glob
import json
import ast
import datetime
from typing import NoReturn, Union

from flask import Flask, render_template, request, url_for, redirect, abort
from flask import session, send_from_directory, _app_ctx_stack, g
from flask_caching import Cache
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_swagger_ui import get_swaggerui_blueprint

from werkzeug.wrappers.response import Response
from werkzeug.urls import url_parse

from api.blueprint import api_blueprint
from models import User
from forms import LoginForm, SignupForm
from utils.typing import Data
from config import *
from utils.generate_open_api_spec import generate_api_docs
import utils.utils as utils
import db.mongodb_controller as db_controller
import ticklist_handler

# create the application object
app = Flask(__name__)

DEBUG = True
API_VERSION = 'v1'
SWAGGER_URL = f'/api/{API_VERSION}/docs'
API_URL = f'/api/{API_VERSION}/docs/swagger.json'
GENERATE_API_DOCS = True
RUN_SERVER = True
DEFAULT_LANG = 'en_US'

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
    """
    Open DDBB connection before request so that
    it can be accessed during the request processing
    """
    g.db = utils.get_db_connection()


@app.teardown_appcontext
def close_db_connection(exception) -> None:
    """
    Closes the database again at the end of the request.
    """
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


def choose_language(request) -> str:
    """
    Choose the first known user language else DEFAULT_LANG
    """
    user_lang = request.headers.get('Accept_Language').replace(
        '-', '_').split(';')[0].split(',')

    lang_matches = set(user_lang).intersection(LANG.keys())
    if lang_matches:
        return lang_matches.pop()
    return DEFAULT_LANG


@app.context_processor
def inject_langauge() -> dict:
    lang = choose_language(request)
    return {**LANG[DEFAULT_LANG], **LANG[lang]}


def get_gym() -> str:
    """
    Get the current session's selected gym.
    """
    if session.get('gym', ''):
        return session['gym']
    gyms = db_controller.get_gyms(g.db)
    return gyms[0]['id']


@app.route('/', methods=['GET', 'POST'])
def home() -> str:
    """
    Homepage handler.
    """
    gyms = db_controller.get_gyms(g.db)
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
    return render_template(
        'home.html',
        gyms=gyms,
        selected=get_gym(),
        current_gym=[gym['name'] for gym in gyms if gym['id'] == get_gym()][0],
        stats=utils.get_stats(g.db)
    )


@app.route('/create')
@cache.cached(timeout=60 * 60, key_prefix=make_cache_key_create)
def create() -> str:
    """
    Create page handler.
    """
    latest = request.args.get('latest', False)
    walls = db_controller.get_gym_walls(get_gym(), g.db, latest=latest)
    for wall in walls:
        wall['image_path'] = utils.get_wall_image(
            get_gym(), wall['image'], WALLS_PATH)
    return render_template(
        'create.html',
        walls=walls,
        options=request.args.get('options', '')
    )


@app.route('/create_boulder')
def create_boulder() -> str:
    """
    Create boulder page handler.
    """
    return render_template('create_boulder.html')


@app.route('/create_route')
def create_route() -> str:
    """
    Create route page handler.
    """
    return render_template('create_route.html')


@app.route('/explore')
def explore() -> str:
    """
    Explore page handler.
    """
    return render_template('explore.html', walls=db_controller.get_gym_walls(get_gym(), g.db))


@app.route('/explore_boulders', methods=['GET', 'POST'])
def explore_boulders() -> str:
    """
    Explore boulders page handler.
    """
    if request.method == 'POST':
        gym = get_gym()
        filters = {
            key: val for (
                key,
                val
            ) in json.loads(
                request.form.get('filters')
            ).items() if val not in ['all', '']
        }

    elif request.method == 'GET':
        gym = request.args.get('gym', get_gym())
        filters = None

    session['filters'] = filters

    boulders = utils.get_boulders_list(gym, filters, g.db, session)
    gym_walls = db_controller.get_gym_walls(gym, g.db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done]
        for boulder in boulders:
            boulder['is_done'] = 1 if boulder['_id'] in done_boulders else 0

    return render_template(
        'explore_boulders.html',
        gyms=db_controller.get_gyms(g.db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin='explore_boulders',
        is_authenticated=current_user.is_authenticated
    )

@app.route('/change_gym', methods=['POST'])
def change_gym_problem_list() -> str:
    """
    Load the list of problems for the selected gym
    """
    gym = request.form.get('gym', get_gym())
    session['gym'] = gym
    filters = session.get('filters', None)

    boulders = utils.get_boulders_list(gym, filters, g.db, session)
    gym_walls = db_controller.get_gym_walls(gym, g.db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done]
        for boulder in boulders:
            boulder['is_done'] = 1 if boulder['_id'] in done_boulders else 0

    return render_template(
        'explore_boulders.html',
        gyms=db_controller.get_gyms(g.db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin='explore_boulders',
        is_authenticated=current_user.is_authenticated
    )

@app.route('/rate_boulder', methods=['POST'])
def rate_boulder() -> Union[Response, NoReturn]:
    """
    Rate boulder handler.
    """
    if request.method == 'POST':
        boulder_name = request.form.get('boulder_name')
        boulder_rating = request.form.get('boulder_rating')
        gym = request.form.get('gym', get_gym())
        boulder = db_controller.get_boulder_by_name(
            gym=gym,
            name=boulder_name,
            database=g.db
        )
        # Update stats
        boulder['rating'] = (boulder['rating'] * boulder['raters'] +
                             int(boulder_rating)) / (boulder['raters'] + 1)
        boulder['raters'] += 1
        db_controller.update_boulder_by_id(
            gym=gym,
            boulder_id=boulder['_id'],
            data=boulder,
            database=g.db
        )
        return redirect(url_for('load_boulder', gym=gym, name=boulder_name))
    return abort(400)


@app.route('/load_boulder', methods=['POST', 'GET'])
# @cache.cached(timeout=60*60, key_prefix=make_cache_key_boulder)
def load_boulder() -> Union[str, NoReturn]:
    """
    Load a boulder in the required format to be rendered in the page.
    """
    try:
        boulder, wall_image = utils.get_boulder_from_request(
            request,
            g.db,
            session,
            get_gym()
        )
        # get hold data
        hold_data = utils.get_hold_data(
            get_gym(),
            boulder['section'],
            app.static_folder
        )

        return render_template(
            'load_boulder.html',
            boulder_name=boulder.get('name', ''),
            wall_image=wall_image,
            boulder_data=boulder,
            scroll=request.args.get('scroll', 0),
            origin=request.form.get('origin', 'explore_boulders'),
            hold_data=hold_data
        )
    except Exception:
        return abort(404)


@app.route('/load_next')
def load_next_problem():
    
    boulder, wall_image = utils.load_next_or_current(
        request.args.get('id'),
        request.args.get('gym'),
        g.db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        get_gym(),
        boulder['section'],
        app.static_folder
    )

    return render_template(
        'load_boulder.html',
        boulder_name=boulder.get('name', ''),
        wall_image=wall_image,
        boulder_data=boulder,
        scroll=request.args.get('scroll', 0),
        origin=request.form.get('origin', 'explore_boulders'),
        hold_data=hold_data
    )


@app.route('/load_previous')
def load_previous_problem():

    boulder, wall_image = utils.load_previous_or_current(
        request.args.get('id'),
        request.args.get('gym'),
        g.db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        get_gym(),
        boulder['section'],
        app.static_folder
    )

    return render_template(
        'load_boulder.html',
        boulder_name=boulder.get('name', ''),
        wall_image=wall_image,
        boulder_data=boulder,
        scroll=request.args.get('scroll', 0),
        origin=request.form.get('origin', 'explore_boulders'),
        hold_data=hold_data
    )

@app.route('/explore_routes')
def explore_routes() -> str:
    """
    Handler for explore_routes page.
    """
    return render_template('explore_routes.html')


@app.route('/random_problem')
def random_problem() -> str:
    """
    Show a random problem
    """
    # get random boulder from gym
    boulder = db_controller.get_random_boulder(get_gym(), g.db)
    if not boulder:
        return abort(404)

    boulder_data, wall_image = utils.load_full_boulder_data(
        boulder,
        get_gym(),
        g.db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        get_gym(),
        boulder['section'],
        app.static_folder
    )

    return render_template(
        'load_boulder.html',
        boulder_name=boulder_data['name'],
        wall_image=wall_image,
        boulder_data=boulder,
        origin=request.form.get('origin', ''),
        hold_data=hold_data
    )


@app.route('/about_us')
def render_about_us() -> str:
    """
    About us page handler.
    """
    return render_template('about_us.html')


@app.route('/walls/<string:wall_section>')
def wall_section(wall_section) -> str:
    """
    Load a wall section to create a boulder/route page handler.
    """
    template = 'create_boulder.html'
    if request.args.get('options', '') == 'route':
        template = 'create_route.html'

    if not session.get('walls_radius', ''):
        session['walls_radius'] = db_controller.get_walls_radius_all(g.db)

    # load hold data
    hold_data = utils.get_hold_data(get_gym(), wall_section, app.static_folder)

    return render_template(
        template,
        wall_image=utils.get_wall_image(get_gym(), wall_section, WALLS_PATH),
        wall_name=db_controller.get_gym_section_name(
            get_gym(), wall_section, g.db),
        section=wall_section,
        radius=utils.get_wall_radius(
            session, g.db, get_gym() + '/' + wall_section),
        hold_data=hold_data
    )


@app.route('/save', methods=['POST'])
def save() -> Response:
    """
    Save page handler
    """
    if request.method == 'POST':
        data: Data = {'rating': 0, 'raters': 0, 'repetitions': 0}
        for key, val in request.form.items():
            data[key.lower()] = val
            if key.lower() == 'holds':
                data[key.lower()] = ast.literal_eval(val)
        data['time'] = datetime.datetime.now().isoformat()
        db_controller.put_boulder(data, gym=get_gym(), database=g.db)
    return redirect('/')


@app.route('/save_boulder', methods=['POST'])
def save_boulder() -> Union[str, NoReturn]:
    """
    Save boulder page handler.
    """
    if request.method == 'POST':
        username = ''
        if current_user.is_authenticated:
            username = current_user.name
        return render_template(
            'save_boulder.html',
            username=username,
            holds=request.form.get('holds'),
            section=request.args.get('section')
        )
    else:
        return abort(400)


# route decorator should be the outermost decorator
@app.route('/add_gym', methods=['GET', 'POST'])
@login_required
def add_gym() -> str:
    """
    Add gym page handler.
    """
    return render_template('add_new_gym.html')


# Login handlers
@app.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    """
    Login page handler.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data, g.db)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('login_form.html', form=form)


@app.route('/signup/', methods=['GET', 'POST'])
def show_signup_form() -> Union[str, Response]:
    """
    Sign up form page handler.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User.get_user_by_email(email, g.db)
        if user is not None:
            error = f'The email {email} is already registered'
        else:
            # Create and save user
            user = User(name=name, email=email)
            user.set_password(password)
            user.save(g.db)
            # Keep user logged in
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('signup_form.html', form=form, error=error)


@app.route('/logout')
def logout() -> Response:
    """
    Logout page handler
    """
    logout_user()
    return redirect(url_for('home'))


# User related endpoints
@app.route('/tick_list', methods=['GET', 'POST'])
@login_required
def tick_list() -> Union[str, Response]:
    """
    Tick list page handler.
    """
    if request.method == 'POST':
        data, _ = utils.load_data(request)
        boulder = db_controller.get_boulder_by_name(
            data.get('gym'),
            data.get('name'),
            g.db
        )
        boulder_id = boulder.get('_id', '')
        if 'add_boulder_to_tick_list' in request.form:
            # Just add boulder to ticklist, it hasn't been climbed yet
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data,
                boulder_id,
                current_user,
                g.db
            )
        elif 'mark_boulder_as_done' in request.form:
            # Add boulder to ticklist if not present, mark as done or add new climbed date
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data,
                boulder_id,
                current_user,
                g.db,
                mark_as_done=True
            )
            # update number of repetitions
            boulder['repetitions'] += 1
            db_controller.update_boulder_by_id(
                gym=data.get('gym'),
                boulder_id=boulder_id,
                data=boulder,
                database=g.db
            )
        # if the request origin is the explore boulders page, go back to it
        if request.form.get('origin', '') and request.form.get('origin') == 'explore_boulders':
            return redirect(url_for('explore_boulders', gym=get_gym()))

    boulder_list, walls_list = ticklist_handler.load_user_ticklist(
        current_user, g.db)

    return render_template(
        'tick_list.html',
        boulder_list=boulder_list,
        walls_list=walls_list
    )


@app.route('/delete_ticklist_problem', methods=['POST'])
def delete_ticklist_problem() -> Union[Response, NoReturn]:
    """
    Delete tick list problem page handler.
    """
    if request.method == 'POST':
        current_user.ticklist = ticklist_handler.delete_problem_from_ticklist(
            request, current_user, g.db)
        return redirect(url_for('tick_list'))
    return abort(400)


@app.route('/get_nearest_gym', methods=['POST'])
def get_nearest_gym() -> Response:
    """
    Given a set of coordinates in the form of
    latitude, longitude, return the closest gym
    to the given position
    """
    closest_gym = utils.get_closest_gym(
        float(dict(request.form)['longitude']),
        float(dict(request.form)['latitude']),
        g.db
    )
    # Set closest gym as actual gym
    session['gym'] = closest_gym
    return redirect(url_for('home'))


@app.route('/contact', methods=['GET'])
def show_contact() -> Union[Response, NoReturn]:
    """
    Contact page
    """
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
