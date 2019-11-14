import os
from flask import Flask, render_template, request, url_for

WALLS_PATH = 'images/walls/'

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('home.html')


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
        user_image=url_for(
            'static',
            filename='{}{}.JPG'.format(WALLS_PATH, wall_section)
        ),
        wall_name=wall_section 
    )


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


# start the server
if __name__ == '__main__':
    app.run(debug=True)
