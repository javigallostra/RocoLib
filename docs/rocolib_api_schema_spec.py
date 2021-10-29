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
    color = fields.Str()
    x = fields.Float()
    y = fields.Float()


class BaseBoulderSchema(Schema):
    """
    Base Boulder Schema
    """
    creator = fields.Str()
    difficulty = fields.Str()
    feet = fields.Str()
    name = fields.Str()
    section = fields.Str()
    time = fields.Str()
    notes = fields.Str()
    holds = fields.List(fields.Nested(HoldSchema))


class BoulderSchema(BaseBoulderSchema):
    """
    Data Schema of a Boulder Problem
    """
    _id = fields.Str()
    raters = fields.Int()
    rating = fields.Float()


class CreateBoulderRequestBody(BaseBoulderSchema):
    pass

class CreateBoulderResponseBody(Schema):
    created = fields.Bool()
    _id = fields.Str()

class GymIDParameter(Schema):
    """
    Data Schema of a Gym ID parameter
    """
    gym_id = fields.Str()


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
        )
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
