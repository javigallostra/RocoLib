import os
import json
import ast
import datetime
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, session, send_from_directory
from flask_caching import Cache
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import User
from forms import LoginForm, SignupForm
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse


import db.firebase_controller as firebase_controller

WALLS_PATH = 'images/walls/'

# For DB querying
EQUALS = ['section', 'difficulty']
RANGE = ['rating']
CONTAINS = ['creator']

# Mappings of DB feet field values to friendly text to render
FEET_MAPPINGS = {
    'free': 'Free feet',
    'follow': 'Feet follow hands',
    'no-feet': 'Campus',
}

# create the application object
app = Flask(__name__)
# app.config.from_pyfile('config.py')
app.secret_key = b'\xf7\x81Q\x89}\x02\xff\x98<et^'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

def make_cache_key_boulder(*args, **kwargs):
    path = request.path
    form = str(hash(frozenset(request.form.items())))
    return (path + form).encode('utf-8')

def make_cache_key_create():
    return (request.path + get_gym()).encode('utf-8')

# user loading callback
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Load favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static/images/favicon'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

def get_gym_path():
    if session.get('gym', ''):
        return '/' + session['gym']
    else:
        return '/sancu'

def get_gym():
    if session.get('gym', ''):
        return session['gym']
    else:
        return 'sancu'    

def get_gym_from_gym_path(gym_path):
    return gym_path[1:]

def get_wall_radius(wall_path=None):
    """
    wall path is expected to be: 'gym/wall'
    """
    if session.get('walls_radius', ''):
        return session['walls_radius'][wall_path]
    else:
        return firebase_controller.get_walls_radius_all()[wall_path]

def get_stats():
    gyms = firebase_controller.get_gyms()
    total_gyms = len(gyms)
    total_boulders = 0
    total_routes = 0
    for gym in gyms:
        try:
            total_boulders += len(firebase_controller.get_boulders(gym['value'])['Items'])
        except:
            pass
        try:
            total_routes += len(firebase_controller.get_routes(gym['value'])['Items'])
        except:
            pass
    
    return {
        'Boulders': total_boulders,
        'Routes': total_routes,
        'Gyms': total_gyms
    }


@app.route('/', methods=['GET', 'POST'])
def home():
    gyms = firebase_controller.get_gyms()
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
    return render_template(
        'home.html',
        gyms=gyms,
        selected=get_gym(),
        current_gym=[gym['name'] for gym in gyms if gym['value']==get_gym()][0],
        stats=get_stats())


@app.route('/create')
@cache.cached(timeout=60*60, key_prefix=make_cache_key_create)
def create():
    walls = firebase_controller.get_gym_walls(get_gym())
    for wall in walls:
        wall['image_path'] = url_for(
            'static',
            filename='{}{}/{}.JPG'.format(WALLS_PATH, get_gym(), wall['image'])
        )
    return render_template(
        'create.html',
        walls=walls,
        options=request.args.get('options', '')
    )


@app.route('/create_boulder')
def create_boulder():
    return render_template('create_boulder.html')


@app.route('/create_route')
def create_route():
    return render_template('create_route.html')


@app.route('/explore')
def explore():
    return render_template('explore.html', walls=firebase_controller.get_gym_walls(get_gym()))


@app.route('/explore_boulders', methods=['GET', 'POST'])
def explore_boulders():
    if request.method == 'POST':
        gym_path = get_gym_path()
        filters = {key: val for (key, val) in json.loads(
            request.form.get('filters')).items() if val not in ['all', '']}
        data = firebase_controller.get_boulders_filtered(
                gym=gym_path,
                conditions=filters,
                equals=EQUALS,
                ranged=RANGE,
                contains=CONTAINS
            )
        for boulder in data['Items']:
            boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
            boulder['safe_name'] = secure_filename(boulder['name'])
            boulder['radius'] = get_wall_radius(get_gym_from_gym_path(gym_path) + '/' + boulder['section'])
        session['boulder_filters'] = filters
        session['boulders_list'] = sorted(
            data['Items'],
            key=lambda x: datetime.datetime.strptime(
                x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
            reverse=True
        )
        gym_walls = firebase_controller.get_gym_walls(gym_path)
        return render_template(
            'explore_boulders.html',
            boulder_list=session['boulders_list'],
            walls_list=gym_walls
        )
    if request.method == 'GET':
        gym_path = get_gym_path()
        boulder_list = session.get('boulders_list', [])
        if not boulder_list:
            data = firebase_controller.get_boulders_filtered(
                    gym=gym_path,
                    conditions=None,
                    equals=EQUALS,
                    contains=CONTAINS
                )
            for boulder in data['Items']:
                boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
                boulder['safe_name'] = secure_filename(boulder['name'])
                boulder['radius'] = get_wall_radius(get_gym_from_gym_path(gym_path) + '/' + boulder['section'])
                boulder_list.append(boulder)
        boulder_list = sorted(
            boulder_list,
            key=lambda x: datetime.datetime.strptime(
                x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
            reverse=True
        )
        gym_walls = firebase_controller.get_gym_walls(gym_path)
        return render_template(
            'explore_boulders.html',
            boulder_list=boulder_list,
            walls_list=gym_walls
        )

@app.route('/rate_boulder', methods=['POST'])
def rate_boulder():
    if request.method == 'POST':
        boulder_name = request.form.get('boulder_name')
        boulder_rating = request.form.get('boulder_rating')
        boulder = firebase_controller.get_boulder_by_name(
            gym=get_gym_path(),
            name=boulder_name
        )
        for key, val in boulder.items():
            # Update stats
            val['rating'] = (val['rating'] * val['raters'] + int(boulder_rating)) / (val['raters'] + 1)
            val['raters'] += 1
            firebase_controller.update_boulder_by_id(
                gym=get_gym_path(),
                boulder_id=key,
                data=val)
    
    return redirect('/explore')


@app.route('/load_boulder', methods=['GET', 'POST'])
@cache.cached(timeout=60*60, key_prefix=make_cache_key_boulder)
def load_boulder():
    if request.method == 'POST':
        try:
            boulder = json.loads(request.form.get(
                "boulder_data").replace('\'', '"'))
            boulder_name = boulder['name']
            section = boulder['section']
            wall_image = url_for(
                'static',
                filename='{}{}/{}.JPG'.format(WALLS_PATH, get_gym(), section)
            )
            return render_template(
                'load_boulder.html',
                boulder_name=boulder_name,
                wall_image=wall_image,
                boulder_data=boulder)
        except:
            return abort(404)
    return abort(400)


@app.route('/explore_routes')
def explore_routes():
    return render_template('explore_routes.html')


@app.route('/about_us')
def render_about_us():
    return render_template('about_us.html')


@app.route('/walls/<string:wall_section>')
def wall_section(wall_section):
    template = 'create_boulder.html'
    if not session.get('walls_radius', ''):
        session['walls_radius'] = firebase_controller.get_walls_radius_all()
    if request.args.get('options', '') == 'route':
        template = 'create_route.html'

    return render_template(
        template,
        wall_image=url_for(
            'static',
            filename='{}{}/{}.JPG'.format(WALLS_PATH, get_gym(), wall_section)
        ),
        wall_name=firebase_controller.get_gym_section_name(get_gym(), wall_section),
        section=wall_section,
        radius=get_wall_radius(get_gym()+'/'+wall_section)
    )


@app.route('/save', methods=['GET', 'POST'])
def save():
    if request.method == 'POST':
        data = {'rating': 0, 'raters': 0}
        for key, val in request.form.items():
            data[key] = val
            if key == "holds":
                data[key] = ast.literal_eval(val)
        data['time'] = datetime.datetime.now().isoformat()
        firebase_controller.put_boulder(data, gym=get_gym_path())
    return redirect('/')


@app.route('/save_boulder', methods=['GET', 'POST'])
def save_boulder():
    if request.method == 'POST':
        return render_template('save_boulder.html', holds=request.form.get('holds'), section=request.args.get('section'))
    else:
        return abort(400)

# route decorator should be the outermost decorator
@app.route('/add_gym', methods=['GET', 'POST'])
@login_required
def add_gym():
    return render_template('add_new_gym.html')

# Login handlers
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('login_form.html', form=form)

@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User.get_user_by_email(email)
        if user is not None:
            error = f'The email {email} is already registered'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# User related
@app.route('/tick_list')
def tick_list():
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


@app.errorhandler(400)
def bad_request(error):
    app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/400.html'), 400


# start the server
if __name__ == '__main__':
    app.run(debug=False)
