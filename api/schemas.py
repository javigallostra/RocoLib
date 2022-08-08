from src.config import PORT, DOCKER_ENV

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


host = 'http://localhost:'
localhost_port = PORT
if DOCKER_ENV == "True":
    localhost_port = 9090


class GymSchema(Schema):
    """
    Data schema of a gym
    """
    _id = fields.Str()
    id = fields.Str()
    name = fields.Str()
    coordinates = fields.List(
        fields.Float(),
        validate=fields.Length(min=2, max=2)
    )


class WallSchema(Schema):
    """
    Data schema of a Gym Wall
    """
    _id = fields.Str()
    image = fields.Str()
    name = fields.Str()
    radius = fields.Float()
    latest = fields.Bool()


class GymNameSchema(Schema):
    """
    Data schema of a Gym Name
    """
    name = fields.Str()


class WallNameSchema(Schema):
    """
    Data schema of a Wall Name
    """
    name = fields.Str()


class HoldSchema(Schema):
    """
    Data Schema of a Hold in a Wall
    """
    color = fields.Str(required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)


class BaseBoulderSchema(Schema):
    """
    Base Boulder Schema
    """
    creator = fields.Str(required=True)
    difficulty = fields.Str(required=True)
    feet = fields.Str(required=True)
    name = fields.Str(required=True)
    time = fields.Str(required=True)
    notes = fields.Str(required=True)
    holds = fields.List(fields.Nested(HoldSchema), required=True)


class BoulderSchema(BaseBoulderSchema):
    """
    Data Schema of a Boulder Problem
    """
    _id = fields.Str()
    raters = fields.Int()
    rating = fields.Float()
    section = fields.Str()


class CreateBoulderRequestBody(BaseBoulderSchema):
    """
    Data Schema to create a boulder
    """
    pass


class CreateBoulderRequestValidator(BaseBoulderSchema):
    """
    Data Schema to validate a create boulder request
    """
    raters = fields.Int(required=True)
    rating = fields.Float(required=True)
    section = fields.Str(required=True)

    # @post_load
    # def make_boulder(self, data, **kwargs):
    #     return CreateBoulderRequestValidator(**data)


class CreateBoulderResponseBody(Schema):
    """
    Data schema of the response to a successful create boulder request
    """
    created = fields.Bool()
    _id = fields.Str()


class RateBoulderRequestBody(Schema):
    """
    Data Schema to rate a boulder
    """
    rating = fields.Int(required=True)


class RateBoulderResponseBody(Schema):
    """
    Data schema of the response to a successful boulder rating request
    """
    _id = fields.Str()
    rated = fields.Bool()


class MarkDoneBoulderRequestBody(Schema):
    """
    Data Schema to rate a boulder
    """
    boulder_id = fields.Str(required=True)
    gym = fields.Str(required=True)


class MarkDoneBoulderResponseBody(Schema):
    """
    Data schema of the response to a successful boulder rating request
    """
    boulder_id = fields.Str()
    marked_as_done = fields.Bool()


class AuthenticationRequestBody(Schema):
    """
    Data Schema of the request to authenticate a user
    """
    username = fields.Str()
    email = fields.Str()
    password = fields.Str()


class AuthenticationResponseBody(Schema):
    """
    Data Schema of the response to a successful authentication request
    """
    token = fields.Str()


class SignUpRequestBody(Schema):
    """
    Data Schema of the request to sign up a new user
    """
    username = fields.Str()
    email = fields.Str()
    password = fields.Str()


class SignUpResponseBody(Schema):
    """
    Data Schema of the response to a successful sign up request
    """
    username = fields.Str()


class UserPreferencesResponseBody(Schema):
    """
    """
    user_id = fields.Str()  # not sure this should be returned
    default_gym = fields.Str()
    show_latest_walls_only = fields.Bool()
    hold_detection_disabled = fields.Bool()


class TestTokenResponseBody(Schema):
    """
    Data schema of the response to a successful test token request
    """
    data = fields.Str()


class GymIDParameter(Schema):
    """
    Data Schema of a Gym ID parameter
    """
    gym_id = fields.Str()


class BoulderIDParameter(Schema):
    """
    Data Schema of a Boulder ID parameter
    """
    boulder_id = fields.Str()


class BoulderNameParameter(Schema):
    """
    Data Schema of a Boulder ID parameter
    """
    boulder_name = fields.Str()


class WallSectionParameter(Schema):
    """
    Data Schema of a Wall section parameter
    """
    wall_section = fields.Str()


class GymListSchema(Schema):
    """
    Gym List Data Schema
    """
    gyms = fields.List(fields.Nested(GymSchema))


class WallListSchema(Schema):
    """
    Wall List Data Schema
    """
    walls = fields.List(fields.Nested(WallSchema))


class GymBoulderListSchema(Schema):
    """
    Boulder List Data Schema
    """
    boulders = fields.List(fields.Nested(BoulderSchema))


class TicklistBoulderSchema(BoulderSchema):
    """
    Ticklist Boulder Data Schema
    """
    is_done = fields.Bool()
    date_climbed = fields.List(fields.Str())


class TicklistResponseBody(Schema):
    """
    Ticklist response data schema
    """
    boulders = fields.List(fields.Nested(TicklistBoulderSchema))


class ErrorResponse(Schema):
    """
    Base error response data schema
    """
    errors = fields.Dict()


class BoulderFields:
    raters = 'raters'
    rating = 'rating'
    section = 'section'
    creator = 'creator'
    difficulty = 'difficulty'
    feet = 'feet'
    name = 'name'
    time = 'time'
    notes = 'notes'
    holds = 'holds'


spec = APISpec(
    title="RocoLib API",
    version="0.0.1",
    openapi_version="3.0.2",
    info=dict(
        description="RocoLib API",
        version="1.0.0-oas3",
        contact=dict(
            email="juangallostra@gmail.com"
        ),
        license=dict(
            name="Apache 2.0",
            url='http://www.apache.org/licenses/LICENSE-2.0.html'
        )
    ),
    servers=[
        dict(
            description="Production server",
            url="https://rocolib.herokuapp.com"
        ),
        dict(
            description="Local Test server",
            url=f"{host}{localhost_port}"
        )
    ],
    components=dict(
        securitySchemes=dict(
            bearerAuth=dict(
                type="http",
                scheme="bearer",
                bearerFormat="JWT"
            )
        )
    ),
    tags=[
        dict(
            name="Gyms",
            description="Endpoints related to Gyms"
        ),
        dict(
            name="Boulders",
            description="Endpoints related to Boulder Problems"
        ),
        dict(
            name="User",
            description="Endpoints related to Users"
        )
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
