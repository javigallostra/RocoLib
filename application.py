import os
import json
import ast
from flask import Flask, render_template, request, url_for, redirect, abort, jsonify

import aws_controller

WALLS_PATH = 'images/walls/'

# create the application object
app = Flask(__name__)

BOULDERS_FILE = 'data/boulders.txt'
BOULDERS_FILE_JSON = 'data/boulders_mod.txt'

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('home.html')


# @app.route('/test')
# def test():
#     return aws_controller.get_items()


@app.route('/create')
def create():
    return render_template('create.html', options=request.args.get('options', ''))


@app.route('/create_boulder')
def create_boulder():
    return render_template('create_boulder.html')


@app.route('/create_route')
def create_route():
    return render_template('create_route.html')


@app.route('/explore')
def explore():
    return render_template('explore.html')


@app.route('/explore_boulders')
def explore_boulders():
    data = json.loads(aws_controller.get_items())
    return render_template('explore_boulders.html', boulder_list=data['Items'])


@app.route('/load_boulder', methods=['GET', 'POST'])
def load_boulder():
    if request.method == 'POST':
        try:
            # boulder = request.form.get("boulder_data")
            boulder = json.loads(request.form.get(
                "boulder_data").replace('\'', '"'))
            boulder_name = boulder['name']
            section = boulder['section']
            wall_image = url_for(
                'static',
                filename='{}{}.JPG'.format(WALLS_PATH, section)
            )
            return render_template(
                'load_boulder.html',
                boulder_name=boulder_name,
                wall_image=wall_image,
                boulder_data=boulder)
        except:
            return abort(404)


@app.route('/explore_routes')
def explore_routes():
    return render_template('explore_boulders.html')


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
            filename='{}{}.JPG'.format(WALLS_PATH, wall_section)
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
        aws_controller.put_item(data)
    return redirect('/')


@app.route('/save_boulder', methods=['GET', 'POST'])
def save_boulder():
    if request.method == 'POST':
        return render_template('save_boulder.html', holds=request.form.get('holds'), section=request.args.get('section'))


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


# start the server
if __name__ == '__main__':
    app.run(debug=True)
