import os

from config import PORT

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


host = 'http://localhost:'
localhost_port = PORT
if os.environ['DOCKER_ENV'] == "True":
    localhost_port = 9090


class GymSchema(Schema):
    """
    Data schema of a gym
    """
    _id = fields.Str()
    id = fields.Str()
    name = fields.Str()
    coordinates = fields.List(
        fields.Float(), validate=fields.Length(min=2, max=2))


class WallSchema(Schema):
    """
    Data schema of a Gym Wall
    """
    _id = fields.Str()
    image = fields.Str()
    name = fields.Str()
    radius = fields.Float()


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
    pass


class CreateBoulderRequestValidator(BaseBoulderSchema):
    raters = fields.Int(required=True)
    rating = fields.Float(required=True)
    section = fields.Str(required=True)

    # @post_load
    # def make_boulder(self, data, **kwargs):
    #     return CreateBoulderRequestValidator(**data)


class CreateBoulderResponseBody(Schema):
    created = fields.Bool()
    _id = fields.Str()


class CreateBoulderErrorResponse(Schema):
    created = fields.Bool()
    errors = fields.Dict()


class AuthenticationRequestBody(Schema):
    username = fields.Str()
    email = fields.Str()
    password = fields.Str()


class AuthenticationResponseBody(Schema):
    token = fields.Str()


class AuthenticationErrorResponse(Schema):
    errors = fields.Str()


class TestTokenResponseBody(Schema):
    data = fields.Str()


class TestTokenErrorResponse(Schema):
    errors = fields.Str()


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
