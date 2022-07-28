import ast
import datetime
import json
from src.models import User
import src.ticklist_handler as ticklist_handler
import db.mongodb_controller as db_controller
import src.utils as utils
from src.forms import LoginForm, SignupForm
from werkzeug.urls import url_parse
from src.typing import Data
from flask import render_template, redirect, url_for, abort
from src.config import *


def handle_home_request(request, session, db):
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
    elif session.get('user_default_gym', '') and session.get('first_load', False):
        session['gym'] = session.get('user_default_gym')
        session['first_load'] = False
    gyms = db_controller.get_gyms(db)
    return render_template(
        'home.html',
        gyms=gyms,
        selected=utils.get_current_gym(session, db),
        current_gym=[gym['name'] for gym in gyms if gym['id']
                     == utils.get_current_gym(session, db)][0],
        stats=utils.get_stats(db)
    )


def handle_create_request(request, session, db):
    latest = request.args.get('latest', False)
    walls = db_controller.get_gym_walls(
        utils.get_current_gym(session, db), db, latest=latest)
    for wall in walls:
        wall['image_path'] = utils.get_wall_image(
            utils.get_current_gym(session, db), wall['image'], WALLS_PATH)
    return render_template(
        'create.html',
        walls=walls,
        options=request.args.get('options', '')
    )


def handle_explore_boulders(request, session, db, current_user):
    if request.method == 'POST':
        gym = utils.get_current_gym(session, db)
        filters = {
            key: val for (
                key,
                val
            ) in json.loads(
                request.form.get('filters')
            ).items() if val not in ['all', '']
        }

    elif request.method == 'GET':
        gym = request.args.get('gym', utils.get_current_gym(session, db))
        filters = None

    session['filters'] = filters

    boulders = utils.get_boulders_list(gym, filters, db, session)
    gym_walls = db_controller.get_gym_walls(gym, db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done]
        for boulder in boulders:
            boulder['is_done'] = 1 if boulder['_id'] in done_boulders else 0

    return render_template(
        'explore_boulders.html',
        gyms=db_controller.get_gyms(db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin='explore_boulders',
        is_authenticated=current_user.is_authenticated
    )


def handle_change_gym_problem_list_request(request, session, db, current_user):
    gym = request.form.get('gym', utils.get_current_gym(session, db))
    session['gym'] = gym
    filters = session.get('filters', None)

    boulders = utils.get_boulders_list(gym, filters, db, session)
    gym_walls = db_controller.get_gym_walls(gym, db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done]
        for boulder in boulders:
            boulder['is_done'] = 1 if boulder['_id'] in done_boulders else 0

    return render_template(
        'explore_boulders.html',
        gyms=db_controller.get_gyms(db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin='explore_boulders',
        is_authenticated=current_user.is_authenticated
    )


def process_rate_boulder_request(request, session, db):
    if request.method == 'POST':
        boulder_name = request.form.get('boulder_name')
        boulder_rating = request.form.get('boulder_rating')
        gym = request.form.get('gym', utils.get_current_gym(session, db))
        boulder = db_controller.get_boulder_by_name(
            gym=gym,
            name=boulder_name,
            database=db
        )
        # Update stats
        boulder['rating'] = (boulder['rating'] * boulder['raters'] +
                             int(boulder_rating)) / (boulder['raters'] + 1)
        boulder['raters'] += 1
        db_controller.update_boulder_by_id(
            gym=gym,
            boulder_id=boulder['_id'],
            data=boulder,
            database=db
        )
        return redirect(url_for('load_boulder', gym=gym, name=boulder_name))
    return abort(400)


def process_load_boulder_request(request, session, db, static_folder):
    try:
        boulder, wall_image = utils.get_boulder_from_request(
            request,
            db,
            session,
            utils.get_current_gym(session, db)
        )
        # get hold data
        hold_data = utils.get_hold_data(
            utils.get_current_gym(session, db),
            boulder['section'],
            static_folder
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


def process_load_next_problem_request(request, session, db, static_folder):
    boulder, wall_image = utils.load_next_or_current(
        request.args.get('id'),
        request.args.get('gym'),
        db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db),
        boulder['section'],
        static_folder
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


def process_load_previous_problem_request(request, session, db, static_folder):
    boulder, wall_image = utils.load_previous_or_current(
        request.args.get('id'),
        request.args.get('gym'),
        db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db),
        boulder['section'],
        static_folder
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


def process_random_problem_request(request, session, db, static_folder):
    # get random boulder from gym
    boulder = db_controller.get_random_boulder(
        utils.get_current_gym(session, db), db)
    if not boulder:
        return abort(404)

    boulder_data, wall_image = utils.load_full_boulder_data(
        boulder,
        utils.get_current_gym(session, db),
        db,
        session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db),
        boulder['section'],
        static_folder
    )

    return render_template(
        'load_boulder.html',
        boulder_name=boulder_data['name'],
        wall_image=wall_image,
        boulder_data=boulder,
        origin=request.form.get('origin', ''),
        hold_data=hold_data
    )


def process_wall_section_request(request, session, db, static_folder, wall_section):
    template = 'create_boulder.html'
    if request.args.get('options', '') == 'route':
        template = 'create_route.html'

    if not session.get('walls_radius', ''):
        session['walls_radius'] = db_controller.get_walls_radius_all(db)

    # load hold data
    hold_data = utils.get_hold_data(utils.get_current_gym(
        session, db), wall_section, static_folder)

    return render_template(
        template,
        wall_image=utils.get_wall_image(utils.get_current_gym(
            session, db), wall_section, WALLS_PATH),
        wall_name=db_controller.get_gym_section_name(
            utils.get_current_gym(session, db), wall_section, db),
        section=wall_section,
        radius=utils.get_wall_radius(
            session, db, utils.get_current_gym(session, db) + '/' + wall_section),
        hold_data=hold_data
    )


def process_save_request(request, session, db):
    if request.method == 'POST':
        data: Data = {'rating': 0, 'raters': 0, 'repetitions': 0}
        for key, val in request.form.items():
            data[key.lower()] = val
            if key.lower() == 'holds':
                data[key.lower()] = ast.literal_eval(val)
        data['time'] = datetime.datetime.now().isoformat()
        db_controller.put_boulder(data, utils.get_current_gym(session, db), db)
    return redirect('/')


def process_save_boulder_request(request, current_user):
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


def process_ticklist_request(request, session, db, current_user):
    if request.method == 'POST':
        data, _ = utils.load_data(request)
        boulder = db_controller.get_boulder_by_name(
            data.get('gym'),
            data.get('name'),
            db
        )
        boulder_id = boulder.get('_id', '')
        if 'add_boulder_to_tick_list' in request.form:
            # Just add boulder to ticklist, it hasn't been climbed yet
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data,
                boulder_id,
                current_user,
                db
            )
        elif 'mark_boulder_as_done' in request.form:
            # Add boulder to ticklist if not present, mark as done or add new climbed date
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data,
                boulder_id,
                current_user,
                db,
                mark_as_done=True
            )
            # update number of repetitions
            boulder['repetitions'] += 1
            db_controller.update_boulder_by_id(
                gym=data.get('gym'),
                boulder_id=boulder_id,
                data=boulder,
                database=db
            )
        # if the request origin is the explore boulders page, go back to it
        if request.form.get('origin', '') and request.form.get('origin') == 'explore_boulders':
            return redirect(url_for('explore_boulders', gym=utils.get_current_gym(session, db)))

    boulder_list, walls_list = ticklist_handler.load_user_ticklist(
        current_user, db)

    return render_template(
        'tick_list.html',
        boulder_list=boulder_list,
        walls_list=walls_list
    )


def process_delete_ticklist_problem_request(request, db, current_user):
    if request.method == 'POST':
        current_user.ticklist = ticklist_handler.delete_problem_from_ticklist(
            request, current_user, db)
        return redirect(url_for('tick_list'))
    return abort(400)


def process_login_request(request, session, db, current_user, login_user):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data, db)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            # set user prefs
            session['user_default_gym'] = user.user_preferences.default_gym
            session['first_load'] = True
            return redirect(next_page)
    return render_template('login_form.html', form=form)


def process_logout_request(logout_user):
    logout_user()
    return redirect(url_for('home'))


def process_signup_request(request, db, current_user, login_user):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User.get_user_by_email(email, db)
        if user is not None:
            error = f'The email {email} is already registered'
        else:
            # Create and save user
            user = User(name=name, email=email)
            user.set_password(password)
            user.save(db)
            # Keep user logged in
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template('signup_form.html', form=form, error=error)


def process_get_nearest_gym_request(request, session, db):
    """
    Given a set of coordinates in the form of
    latitude, longitude, return the closest gym
    to the given position
    """
    closest_gym = utils.get_closest_gym(
        float(dict(request.form)['longitude']),
        float(dict(request.form)['latitude']),
        db
    )
    # Set closest gym as actual gym
    session['gym'] = closest_gym
    return redirect(url_for('home'))

def process_profile_request(request, db, session, current_user):
    if request.method == 'POST':
        default_gym = request.form.get('gym')
        if default_gym != current_user.user_preferences.default_gym:
            current_user.user_preferences.default_gym = default_gym
            current_user.save(db)
    gyms = db_controller.get_gyms(db)

    return render_template(
        'profile.html',
        gyms=gyms,
        user_prefs=current_user.user_preferences,
        selected=current_user.user_preferences.default_gym,
        current_gym=[gym['name'] for gym in gyms if gym['id']
                     == current_user.user_preferences.default_gym][0]
    )