import os
import json
import ast
import datetime

from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, session, send_from_directory, _app_ctx_stack
from flask_caching import Cache
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import User, TickListProblem
from forms import LoginForm, SignupForm
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse

import pymongo
import db.mongodb_controller as db_controller
from config import *
from utils.utils import *

import ticklist_handler

# create the application object
app = Flask(__name__)

# app.config.from_pyfile('config.py')
app.secret_key = b'\xf7\x81Q\x89}\x02\xff\x98<et^'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def make_cache_key_create():
    return (request.path + get_gym()).encode('utf-8')

def get_db():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'database'):
        client = pymongo.MongoClient(
            os.environ['MONGO_DB'],
            connectTimeoutMS=30000, socketTimeoutMS=None, socketKeepAlive=True, connect=False, maxPoolsize=1)
        top.database = client["RocoLib"]
    return top.database


@app.teardown_appcontext
def close_db_connection(exception):
    """
    Closes the database again at the end of the request.
    """
    top = _app_ctx_stack.top
    if hasattr(top, 'database'):
        top.database.client.close()

# user loading callback
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id, get_db())

# Load favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/images/favicon'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

def get_gym():
    """
    Get the current session's selected gym.
    """
    if session.get('gym', ''):
        return session['gym']
    else:
        return 'sancu'    

def get_wall_radius(wall_path=None):
    """
    Gets the radius of the circe used to mark holds for
    a specific wall.
    Wall path is expected to be: 'gym/wall'.
    """
    if session.get('walls_radius', '') and session['walls_radius'].get(wall_path, ''):
        return session['walls_radius'][wall_path]
    else:
        return db_controller.get_walls_radius_all(get_db())[wall_path]

def get_stats():
    """
    Gt current app stats from DDBB: Number of problems, routes and Gyms.
    """
    gyms = db_controller.get_gyms(get_db())
    total_gyms = len(gyms)
    total_boulders = 0
    total_routes = 0
    for gym in gyms:
        try:
            total_boulders += len(db_controller.get_boulders(gym['id'], get_db())[ITEMS])
        except:
            pass
        try:
            total_routes += len(db_controller.get_routes(gym['id'], get_db())[ITEMS])
        except:
            pass
    
    return {
        'Boulders': total_boulders,
        'Routes': total_routes,
        'Gyms': total_gyms
    }

def get_boulders_list(gym, filters, database):
    """
    Given a gym and a set of filters return the list of
    boulders that match the specified criteria.
    """
    data = db_controller.get_boulders_filtered(
            gym=gym,
            database=database,
            conditions=filters,
            equals=EQUALS,
            ranged=RANGE,
            contains=CONTAINS
        )
    # Map and complete boulder data
    for boulder in data[ITEMS]:
        boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
        boulder['safe_name'] = secure_filename(boulder['name'])
        boulder['radius'] = get_wall_radius(gym + '/' + boulder['section'])
        boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
    return sorted(
        data[ITEMS],
        key=lambda x: datetime.datetime.strptime(
            x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
        reverse=True
    )

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Homepage handler.
    """
    gyms = db_controller.get_gyms(get_db())
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
    return render_template(
        'home.html',
        gyms=gyms,
        selected=get_gym(),
        current_gym=[gym['name'] for gym in gyms if gym['id']==get_gym()][0],
        stats=get_stats())


@app.route('/create')
@cache.cached(timeout=60*60, key_prefix=make_cache_key_create)
def create():
    """
    Create page handler.
    """
    walls = db_controller.get_gym_walls(get_gym(), get_db())
    for wall in walls:
        wall['image_path'] = get_wall_image(get_gym(), wall['image'], WALLS_PATH)
    return render_template(
        'create.html',
        walls=walls,
        options=request.args.get('options', '')
    )


@app.route('/create_boulder')
def create_boulder():
    """
    Create boulder page handler.
    """
    return render_template('create_boulder.html')


@app.route('/create_route')
def create_route():
    """
    Create route page handler.
    """
    return render_template('create_route.html')


@app.route('/explore')
def explore():
    """
    Explore page handler.
    """
    return render_template('explore.html', walls=db_controller.get_gym_walls(get_gym(), get_db()))


@app.route('/explore_boulders', methods=['GET', 'POST'])
def explore_boulders():
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
        boulders = get_boulders_list(gym, filters, get_db())

    elif request.method == 'GET':
        gym = request.args.get('gym', '')
        if not gym:
            gym = get_gym()
        filters = None
        
    boulders = get_boulders_list(gym, filters, get_db())
    gym_walls = db_controller.get_gym_walls(gym, get_db())
    return render_template(
        'explore_boulders.html',
        boulder_list=boulders,
        walls_list=gym_walls,
        origin='explore_boulders'
    )

@app.route('/rate_boulder', methods=['POST'])
def rate_boulder():
    """
    Rate boulder handler.
    """
    if request.method == 'POST':
        boulder_name = request.form.get('boulder_name')
        boulder_rating = request.form.get('boulder_rating')
        gym = request.form.get('gym') if request.form.get('gym', '') else get_gym()
        boulder = db_controller.get_boulder_by_name(
            gym=gym,
            name=boulder_name,
            database=get_db()
        )        
        # Update stats
        boulder['rating'] = (boulder['rating'] * boulder['raters'] + int(boulder_rating)) / (boulder['raters'] + 1)
        boulder['raters'] += 1
        db_controller.update_boulder_by_id(
            gym=gym,
            boulder_id=boulder['_id'],
            data=boulder,
            database=get_db()
        )
        return redirect(url_for('load_boulder', gym=gym, name=boulder_name))
    return abort(400)


@app.route('/load_boulder', methods=['POST'])
# @cache.cached(timeout=60*60, key_prefix=make_cache_key_boulder)
def load_boulder():
    """
    Load a boulder in the required format to be rendered in the page.
    """
    try:
        if request.method == 'POST':
            boulder = load_boulder_from_request(request)
            boulder_name = boulder['name']
            section = boulder['section']
            if not boulder.get('gym', ''):
                boulder['gym'] = get_gym()
            wall_image = get_wall_image(boulder['gym'], section, WALLS_PATH)
        elif request.method == 'GET':
            boulder = db_controller.get_boulder_by_name(
                gym=request.args.get('gym'), 
                name=request.args.get('name'),
                database=get_db()
            )
            boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
            boulder['safe_name'] = secure_filename(boulder['name'])
            boulder['radius'] = get_wall_radius(request.args.get('gym') + '/' + boulder['section'])
            boulder['color'] = BOULDER_COLOR_MAP[boulder['difficulty']]
            boulder['gym'] = request.args.get('gym')
            boulder_name = boulder['name']
            section = boulder['section']
            wall_image = get_wall_image(request.args.get('gym'), section, WALLS_PATH)
        return render_template(
                'load_boulder.html',
                boulder_name=boulder_name,
                wall_image=wall_image,
                boulder_data=boulder,
                origin=request.form.get('origin')
            )
    except:
        return abort(404)


@app.route('/explore_routes')
def explore_routes():
    """
    Handler for explore_routes page.
    """
    return render_template('explore_routes.html')


@app.route('/about_us')
def render_about_us():
    """
    About us page handler.
    """
    return render_template('about_us.html')


@app.route('/walls/<string:wall_section>')
def wall_section(wall_section):
    """
    Load a wall section to create a boulder/route page handler.
    """
    template = 'create_boulder.html'
    if request.args.get('options', '') == 'route':
        template = 'create_route.html'

    if not session.get('walls_radius', ''):
        session['walls_radius'] = db_controller.get_walls_radius_all(get_db())

    return render_template(
        template,
        wall_image=get_wall_image(get_gym(), wall_section, WALLS_PATH),
        wall_name=db_controller.get_gym_section_name(get_gym(), wall_section, get_db()),
        section=wall_section,
        radius=get_wall_radius(get_gym()+'/'+wall_section)
    )


@app.route('/save', methods=['POST'])
def save():
    """
    Save page handler.
    """
    if request.method == 'POST':
        data = {'rating': 0, 'raters': 0}
        for key, val in request.form.items():
            data[key] = val
            if key == 'holds':
                data[key] = ast.literal_eval(val)
        data['time'] = datetime.datetime.now().isoformat()
        db_controller.put_boulder(data, gym=get_gym(), database=get_db())
    return redirect('/')


@app.route('/save_boulder', methods=['POST'])
def save_boulder():
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
def add_gym():
    """
    Add gym page handler.
    """
    return render_template('add_new_gym.html')


# Login handlers
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page handler.
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data, get_db())
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('login_form.html', form=form)


@app.route('/signup/', methods=['GET', 'POST'])
def show_signup_form():
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
        user = User.get_user_by_email(email, get_db())
        if user is not None:
            error = f'The email {email} is already registered'
        else:
            # Create and save user
            user = User(name=name, email=email)
            user.set_password(password)
            user.save(get_db())
            # Keep user logged in
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('signup_form.html', form=form, error=error)


@app.route('/logout')
def logout():
    """
    Logout page handler
    """
    logout_user()
    return redirect(url_for('home'))


# User related
@app.route('/tick_list', methods=['GET', 'POST'])
@login_required
def tick_list():
    """
    Tick list page handler.
    """
    if request.method == 'POST':
        current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(request, current_user, get_db())
        # if the request origin is the explore boulders page, go back to it
        if request.form.get('origin', '') and request.form.get('origin') == 'explore_boulders':
            return redirect(url_for('explore_boulders', gym=get_gym()))
    boulder_list, walls_list = ticklist_handler.load_user_ticklist(current_user, get_db())
    return render_template(
        'tick_list.html', 
        boulder_list=boulder_list,
        walls_list=walls_list
    )


@app.route('/delete_ticklist_problem', methods=['POST'])
def delete_ticklist_problem():
    """
    Delete tick list problem page handler.
    """
    if request.method == 'POST':
        current_user.ticklist = ticklist_handler.delete_problem_from_ticklist(request, current_user, get_db())
        return redirect(url_for('tick_list'))
    return abort(400)


@app.errorhandler(404)
def page_not_found(error):
    # pylint: disable=no-member
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


@app.errorhandler(400)
def bad_request(error):
    # pylint: disable=no-member
    app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/400.html'), 400


# start the server
if __name__ == '__main__':
    app.run(debug=False)
