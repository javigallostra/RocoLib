from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


class GymSchema(Schema):
    """
    Data schema of a gym
    """
    _id = fields.Str()
    id = fields.Str()
    name = fields.Str()
    coordinates = fields.List(fields.Float(), validate=fields.Length(min=2, max=2))

class WallSchema(Schema):
    """
    Data schema of a Gym Wall
    """
    _id = fields.Str()
    image = fields.Str()
    name = fields.Str()
    radius = fields.Float()

class GymIDParameter(Schema):
    gym_id = fields.Str()

class GymListSchema(Schema):
    gyms = fields.List(fields.Nested(GymSchema))

class WallListSchema(Schema):
    walls = fields.List(fields.Nested(WallSchema))


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
            url="http://localhost:5000"
        )
    ],
    tags=[
        dict(
            name="Gyms",
            description="Endpoints related to Gyms"
        )
    ],
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)
