import os
from flask import Flask, render_template, request


# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/about_us')
def render_about_us():
    return render_template('about_us.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    return render_template('errors/404.html'), 404


# start the server
if __name__ == '__main__':
    app.run(debug=True)
