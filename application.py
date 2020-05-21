import os
import json
import ast
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify, session, send_from_directory
import datetime

import firebase_controller

WALLS_PATH = 'images/walls/'

# For AWS DynamoDB querying
EQUALS = ['section', 'difficulty']
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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
    return render_template(
        'home.html',
        gyms=firebase_controller.get_gyms(),
        selected=get_gym())


@app.route('/create')
def create():
    return render_template(
        'create.html',
        walls=firebase_controller.get_gym_walls(get_gym()),
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
        filters = {key: val for (key, val) in json.loads(
            request.form.get('filters')).items() if val not in ['all', '']}
        data = firebase_controller.get_boulders_filtered(
                gym=get_gym_path(),
                conditions=filters,
                equals=EQUALS,
                contains=CONTAINS
            )
        for boulder in data['Items']:
            boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
        session['boulder_filters'] = filters
        session['boulders_list'] = sorted(
            data['Items'],
            key=lambda x: datetime.datetime.strptime(
                x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
            reverse=True
        )
        return render_template('explore_boulders.html', boulder_list=session['boulders_list'])
    if request.method == 'GET':
        boulder_list = session.get('boulders_list', [])
        if not boulder_list:
            data = firebase_controller.get_boulders_filtered(
                    gym=get_gym_path(),
                    conditions=None,
                    equals=EQUALS,
                    contains=CONTAINS
                )
            for boulder in data['Items']:
                boulder['feet'] = FEET_MAPPINGS[boulder['feet']]
                boulder_list.append(boulder)
        boulder_list = sorted(
            boulder_list,
            key=lambda x: datetime.datetime.strptime(
                x['time'], '%Y-%m-%dT%H:%M:%S.%f'),
            reverse=True
        )
        return render_template('explore_boulders.html', boulder_list=boulder_list)


@app.route('/load_boulder', methods=['GET', 'POST'])
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
    if request.args.get('options', '') == 'route':
        template = 'create_route.html'

    return render_template(
        template,
        wall_image=url_for(
            'static',
            filename='{}{}/{}.JPG'.format(WALLS_PATH, get_gym(), wall_section)
        ),
        wall_name=wall_section
    )


@app.route('/save', methods=['GET', 'POST'])
def save():
    if request.method == 'POST':
        data = {}
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


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


@app.errorhandler(400)
def page_not_found(error):
    app.logger.error('Bad request: %s', (request.path))
    return render_template('errors/400.html'), 400


# start the server
if __name__ == '__main__':
    app.run(debug=False)
