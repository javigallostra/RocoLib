import json
import db.mongodb_controller as db_controller
import utils.utils as utils
from flask import render_template
from config import *


def handle_home_request(request, session, db):
    if request.method == 'POST':
        session['gym'] = request.form.get('gym')
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