from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


class GymSchema(Schema):
    _id = fields.Str()
    id = fields.Str()
    name = fields.Str()
    coordinates = fields.List(fields.Float(), validate=fields.Length(min=2, max=2))


class GymListSchema(Schema):
    gyms = fields.List(fields.Nested(GymSchema))


spec = APISpec(
    title="RocoLib API",
    version="1.0.0",
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
            description="Test server",
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

# spec.components.schema("Gyms", schema=GymListSchema)
