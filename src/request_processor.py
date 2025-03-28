import ast
import datetime
import json
from csv import list_dialects
from typing import Tuple
from urllib.parse import urlparse

from flask import abort, redirect, render_template, url_for

import db.mongodb_controller as db_controller
import src.ticklist_handler as ticklist_handler
import src.utils as utils
from src.config import *
from src.forms import LoginForm, SignupForm
from src.models import User
from src.typing import Data


def handle_home_request(request, session, db):
    if request.method == "POST":
        session["gym"] = request.form.get("gym")
    elif session.get("user_default_gym", "") and session.get("first_load", False):
        session["gym"] = session.get("user_default_gym")
        session["first_load"] = False

    gyms = db_controller.get_gyms(db)
    return render_template(
        "home.html",
        gyms=gyms,
        selected=utils.get_current_gym(session, db),
        current_gym=[
            gym["name"]
            for gym in gyms
            if gym["id"] == utils.get_current_gym(session, db)
        ][0],
        stats=utils.get_stats(db),
    )


def handle_create_request(request, session, db, current_user):

    walls = db_controller.get_gym_walls(
        utils.get_current_gym(session, db),
        db,
        utils.get_show_only_latest_wall_sets(current_user),
    )
    for wall in walls:
        wall["image_path"] = utils.get_wall_image(
            utils.get_current_gym(session, db), wall["image"], WALLS_PATH
        )
    return render_template(
        "create.html", walls=walls, options=request.args.get("options", "")
    )


def handle_explore_boulders(request, session, db, current_user):
    if request.method == "POST":
        gym = utils.get_current_gym(session, db)
        filters = {
            key: val
            for (key, val) in json.loads(request.form.get("filters")).items()
            if val not in ["all", ""]
        }

    elif request.method == "GET":
        gym = request.args.get("gym", utils.get_current_gym(session, db))
        filters = None

    session["filters"] = filters

    boulders = utils.get_boulders_list(
        gym, filters, db, session, utils.get_show_only_latest_wall_sets(current_user)
    )
    gym_walls = db_controller.get_gym_walls(gym, db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done
        ]
        for boulder in boulders:
            boulder["is_done"] = 1 if boulder["_id"] in done_boulders else 0

    return render_template(
        "explore_boulders.html",
        gyms=db_controller.get_gyms(db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin="explore_boulders",
        is_authenticated=current_user.is_authenticated,
    )


def handle_explore_circuits(request, session, db, current_user):
    if request.method == "POST":
        gym = utils.get_current_gym(session, db)

    elif request.method == "GET":
        gym = request.args.get("gym", utils.get_current_gym(session, db))

    circuits = utils.get_circuits_list(
        gym, db, session, utils.get_show_only_latest_wall_sets(current_user)
    )

    gym_walls = db_controller.get_gym_walls(gym, db)

    return render_template(
        "explore_circuits.html",
        gyms=db_controller.get_gyms(db),
        selected=gym,
        circuit_list=circuits,
        walls_list=gym_walls,
        origin="explore_circuits",
        is_authenticated=current_user.is_authenticated,
    )


def handle_change_gym_problem_list_request(request, session, db, current_user):
    gym = request.form.get("gym", utils.get_current_gym(session, db))
    session["gym"] = gym
    filters = session.get("filters", None)

    boulders = utils.get_boulders_list(gym, filters, db, session)
    gym_walls = db_controller.get_gym_walls(gym, db)

    if current_user.is_authenticated:
        done_boulders = [
            boulder.iden for boulder in current_user.ticklist if boulder.is_done
        ]
        for boulder in boulders:
            boulder["is_done"] = 1 if boulder["_id"] in done_boulders else 0

    return render_template(
        "explore_boulders.html",
        gyms=db_controller.get_gyms(db),
        selected=gym,
        boulder_list=boulders,
        walls_list=gym_walls,
        origin="explore_boulders",
        is_authenticated=current_user.is_authenticated,
    )


def process_rate_boulder_request(request, session, db):
    if request.method == "POST":
        boulder_name = request.form.get("boulder_name")
        boulder_rating = request.form.get("boulder_rating")
        gym = request.form.get("gym", utils.get_current_gym(session, db))
        boulder = db_controller.get_boulder_by_name(
            gym=gym, name=boulder_name, database=db
        )
        # Update stats
        boulder["rating"] = (
            boulder["rating"] * boulder["raters"] + int(boulder_rating)
        ) / (boulder["raters"] + 1)
        boulder["raters"] += 1
        db_controller.update_boulder_by_id(
            gym=gym, boulder_id=boulder["_id"], boulder_data=boulder, database=db
        )
        return redirect(url_for("load_boulder", gym=gym, name=boulder_name))
    return abort(400)


def process_load_circuit_request(request, session, db, current_user, static_folder):
    try:
        # get additional request params: list_id, is_user_list, sort_order, is_ascending, to_show
        request_data = utils.load_data(request)

        if isinstance(request_data, Tuple):
            request_data = request_data[0]

        circuit, wall_image = utils.get_circuit_from_request(
            request, db, session, utils.get_current_gym(session, db)
        )

        if not bool(circuit):
            abort(404)

        # get hold data
        hold_data = utils.get_hold_data(
            utils.get_current_gym(session, db), circuit["section"], static_folder
        )

        # map fields to appropriate values
        sort_by = utils.get_field_value("sort_order", request_data)
        is_ascending = utils.get_field_value("is_ascending", request_data)
        to_show = utils.get_field_value("to_show", request_data)

        return render_template(
            "load_circuit.html",
            circuit_name=circuit.get("name", ""),
            wall_image=wall_image,
            circuit_data=circuit,
            scroll=request.args.get("scroll", 0),
            origin=request.form.get("origin", "explore_circuit"),
            hold_data=hold_data,
            hold_detection=utils.get_hold_detection_active(current_user),
            list_id=request_data.get("list_id"),
            is_user_list=request_data.get("is_user_list"),
            sort_by=sort_by,
            is_ascending=is_ascending,
            to_show=to_show,
        )
    except Exception:
        return abort(500)  # internal server error


def process_load_boulder_request(request, session, db, current_user, static_folder):
    try:
        # get additional request params: list_id, is_user_list, sort_order, is_ascending, to_show
        request_data = utils.load_data(request)

        if isinstance(request_data, Tuple):
            request_data = request_data[0]

        boulder, wall_image = utils.get_boulder_from_request(
            request, db, session, utils.get_current_gym(session, db)
        )

        if not bool(boulder):
            abort(404)

        # get hold data
        hold_data = utils.get_hold_data(
            utils.get_current_gym(session, db), boulder["section"], static_folder
        )

        # map fields to appropriate values
        sort_by = utils.get_field_value("sort_order", request_data)
        is_ascending = utils.get_field_value("is_ascending", request_data)
        to_show = utils.get_field_value("to_show", request_data)

        return render_template(
            "load_boulder.html",
            boulder_name=boulder.get("name", ""),
            wall_image=wall_image,
            boulder_data=boulder,
            scroll=request.args.get("scroll", 0),
            origin=request.form.get("origin", "explore_boulders"),
            hold_data=hold_data,
            hold_detection=utils.get_hold_detection_active(current_user),
            list_id=request_data.get("list_id"),
            is_user_list=request_data.get("is_user_list"),
            sort_by=sort_by,
            is_ascending=is_ascending,
            to_show=to_show,
        )
    except Exception:
        return abort(500)  # internal server error


def process_load_next_problem_request(
    request, session, db, current_user, static_folder
):
    user_id = None
    is_user_list = False
    if request.args.get("is_user_list", "").lower() == "true":
        is_user_list = True
    if current_user.is_authenticated:
        user_id = current_user.id

    boulder, wall_image = utils.load_next_or_current(
        request.args.get("id"),  # problem_id
        request.args.get("list_id"),  # list from which to get next problem
        user_id,  # pass user id in case we need to retrieve the list for a user
        is_user_list,
        utils.get_show_only_latest_wall_sets(current_user),
        request.args.get("sort_by"),
        True if request.args.get("is_ascending") == "True" else False,
        request.args.get("to_show"),
        db,
        session,
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db), boulder["section"], static_folder
    )

    # TODO: pass back sorting/visualization parameters
    return render_template(
        "load_boulder.html",
        boulder_name=boulder.get("name", ""),
        wall_image=wall_image,
        boulder_data=boulder,
        scroll=request.args.get("scroll", 0),
        # TODO: map somehow lists to origin urls?
        origin=request.form.get(
            "origin", "explore_boulders" if not is_user_list else "tick_list"
        ),
        hold_data=hold_data,
        hold_detection=utils.get_hold_detection_active(current_user),
        list_id=request.args.get("list_id"),  # default values atm
        is_user_list=is_user_list,
        sort_by=request.args.get("sort_by"),
        is_ascending=request.args.get("is_ascending"),
        to_show=request.args.get("to_show"),
    )


def process_load_previous_problem_request(
    request, session, db, current_user, static_folder
):
    user_id = None
    is_user_list = False
    if request.args.get("is_user_list", "").lower() == "true":
        is_user_list = True
    if current_user.is_authenticated:
        user_id = current_user.id

    boulder, wall_image = utils.load_previous_or_current(
        request.args.get("id"),  # problem_id
        request.args.get("list_id"),  # list from which to get next problem
        user_id,  # pass user id in case we need to retrieve the list for a user
        is_user_list,
        utils.get_show_only_latest_wall_sets(current_user),
        request.args.get("sort_by"),
        True if request.args.get("is_ascending") == "True" else False,
        request.args.get("to_show"),
        db,
        session,
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db), boulder["section"], static_folder
    )

    # TODO: pass back sorting/visualization parameters
    return render_template(
        "load_boulder.html",
        boulder_name=boulder.get("name", ""),
        wall_image=wall_image,
        boulder_data=boulder,
        scroll=request.args.get("scroll", 0),
        origin=request.form.get(
            "origin", "explore_boulders" if not is_user_list else "tick_list"
        ),
        hold_data=hold_data,
        hold_detection=utils.get_hold_detection_active(current_user),
        list_id=request.args.get("list_id"),  # default values atm
        is_user_list=is_user_list,
        sort_by=request.args.get("sort_by"),
        is_ascending=request.args.get("is_ascending"),
        to_show=request.args.get("to_show"),
    )


def process_random_problem_request(request, session, db, current_user, static_folder):
    # get random boulder from gym
    boulder = db_controller.get_random_boulder(utils.get_current_gym(session, db), db)
    if not boulder:
        return abort(404)

    boulder_data, wall_image = utils.load_full_boulder_data(
        boulder, utils.get_current_gym(session, db), db, session
    )

    # get hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db), boulder["section"], static_folder
    )

    return render_template(
        "load_boulder.html",
        boulder_name=boulder_data["name"],
        wall_image=wall_image,
        boulder_data=boulder,
        scroll=0,
        origin=request.form.get("origin", ""),
        hold_data=hold_data,
        hold_detection=utils.get_hold_detection_active(current_user),
        list_id=boulder["gym"],
        is_user_list=False,
    )


def process_wall_section_request(
    request, session, db, current_user, static_folder, wall_section
):
    template = "create_boulder.html"
    # Not implemented atm
    if request.args.get("options", "") == "route":
        template = "create_route.html"

    elif request.args.get("options", "") == "circuit":
        template = "create_circuit.html"

    if not session.get("walls_radius", ""):
        session["walls_radius"] = db_controller.get_walls_radius_all(db)

    # load hold data
    hold_data = utils.get_hold_data(
        utils.get_current_gym(session, db), wall_section, static_folder
    )

    hold_detection = True
    if current_user.is_authenticated:
        hold_detection = not current_user.preferences.hold_detection_disabled

    return render_template(
        template,
        wall_image=utils.get_wall_image(
            utils.get_current_gym(session, db), wall_section, WALLS_PATH
        ),
        wall_name=db_controller.get_gym_section_name(
            utils.get_current_gym(session, db), wall_section, db
        ),
        section=wall_section,
        radius=utils.get_wall_radius(
            session, db, utils.get_current_gym(session, db) + "/" + wall_section
        ),
        hold_data=hold_data,
        hold_detection=hold_detection,
    )


def process_save_request(request, session, db, is_circuit=False):
    if request.method == "POST":
        data: Data = {"rating": 0, "raters": 0, "repetitions": 0}
        for key, val in request.form.items():
            data[key.lower()] = val
            if key.lower() == "holds":
                data[key.lower()] = ast.literal_eval(val)
        data["time"] = datetime.datetime.now().isoformat()
        if is_circuit:
            db_controller.put_circuit(data, utils.get_current_gym(session, db), db)
        else:
            db_controller.put_boulder(data, utils.get_current_gym(session, db), db)
    return redirect("/")


def process_save_boulder_request(request, current_user):
    if request.method == "POST":
        username = ""
        if current_user.is_authenticated:
            username = current_user.name
        return render_template(
            "save_boulder.html",
            username=username,
            holds=request.form.get("holds"),
            section=request.args.get("section"),
        )
    else:
        return abort(400)


def process_save_circuit_request(request, current_user):
    if request.method == "POST":
        username = ""
        if current_user.is_authenticated:
            username = current_user.name
        return render_template(
            "save_circuit.html",
            username=username,
            holds=request.form.get("holds"),
            section=request.args.get("section"),
        )
    else:
        return abort(400)


def process_ticklist_request(request, session, db, current_user):
    # TODO: split into several requests? Too much going on here
    if request.method == "POST":
        data, _ = utils.load_data(request)
        boulder = db_controller.get_boulder_by_name(
            data.get("gym"), data.get("name"), db
        )
        boulder_id = boulder.get("_id", "")
        if "add_boulder_to_tick_list" in request.form:
            # Just add boulder to ticklist, it hasn't been climbed yet
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data, boulder_id, current_user, db
            )
        elif "mark_boulder_as_done" in request.form:
            # Add boulder to ticklist if not present, mark as done or add new climbed date
            current_user.ticklist = ticklist_handler.add_boulder_to_ticklist(
                data, boulder_id, current_user, db, mark_as_done=True
            )
            # update number of repetitions
            boulder["repetitions"] += 1
            db_controller.update_boulder_by_id(
                gym=data.get("gym"),
                boulder_id=boulder_id,
                boulder_data=boulder,
                database=db,
            )
        # if the request origin is the explore boulders page, go back to it
        if (
            request.form.get("origin", "")
            and request.form.get("origin") == "explore_boulders"
        ):
            return redirect(
                url_for("explore_boulders", gym=utils.get_current_gym(session, db))
            )

    boulder_list, walls_list = ticklist_handler.load_user_ticklist(current_user, db)

    return render_template(
        "tick_list.html", boulder_list=boulder_list, walls_list=walls_list
    )


def process_delete_ticklist_problem_request(request, db, current_user):
    if request.method == "POST":
        current_user.ticklist = ticklist_handler.delete_problem_from_ticklist(
            request, current_user, db
        )
        return redirect(url_for("tick_list"))
    return abort(400)


def process_login_request(request, session, db, current_user, login_user):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_user_by_email(form.email.data, db)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("home")
            # set user prefs
            session["user_default_gym"] = user.preferences.default_gym
            session["first_load"] = True
            return redirect(next_page)
    return render_template("login_form.html", form=form)


def process_logout_request(logout_user):
    logout_user()
    return redirect(url_for("home"))


def process_signup_request(request, db, current_user, login_user):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = User.get_user_by_email(email, db)
        if user is not None:
            error = f"The email {email} is already registered"
        else:
            # Create and save user
            user = User(name=name, email=email)
            user.set_password(password)
            user.save(db)
            # Keep user logged in
            login_user(user, remember=True)
            next_page = request.args.get("next", None)
            if not next_page or urlparse(next_page).netloc != "":
                next_page = url_for("home")
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)


def process_get_nearest_gym_request(request, session, db):
    """
    Given a set of coordinates in the form of
    latitude, longitude, return the closest gym
    to the given position
    """
    closest_gym = utils.get_closest_gym(
        float(dict(request.form)["longitude"]),
        float(dict(request.form)["latitude"]),
        db,
    )
    # Set closest gym as actual gym
    session["gym"] = closest_gym
    return redirect(url_for("home"))


def process_profile_request(request, db, session, current_user):
    # switches come as "on" or nothing
    if request.method == "POST":
        should_save, current_user = utils.update_user_prefs(request, current_user)
        if should_save:
            current_user.save(db)
            # update default gym
            session["gym"] = current_user.preferences.default_gym
            session["user_default_gym"] = current_user.preferences.default_gym

    gyms = db_controller.get_gyms(db)

    return render_template(
        "profile.html",
        gyms=gyms,
        user_prefs=current_user.preferences,
        selected=current_user.preferences.default_gym,
        current_gym=[
            gym["name"]
            for gym in gyms
            if gym["id"] == current_user.preferences.default_gym
        ][0],
    )
