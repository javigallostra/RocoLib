from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields


class GymSchema(Schema):
    _id = fields.Str()
    id = fields.Str()
    name = fields.Str()
    coordinates = fields.List(fields.Float())


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

# Extensions initialization
# =========================
# app = Flask(__name__)


# @app.route("/demo/<gist_id>", methods=["GET"])
# def my_route(gist_id):
#     """Gist detail view.
#     ---
#     get:
#       parameters:
#       - in: path
#         schema: DemoParameter
#       responses:
#         200:
#           content:
#             application/json:
#               schema: DemoSchema
#         201:
#           content:
#             application/json:
#               schema: DemoSchema
#     """
#     # (...)
#     return jsonify('foo')


# Since path inspects the view and its route,
# we need to be in a Flask request context
# with app.test_request_context():
#     spec.path(view=my_route)
# # We're good to go! Save this to a file for now.
# with open('swagger.json', 'w') as f:
#     json.dump(spec.to_dict(), f)

# pprint(spec.to_dict())
# print(spec.to_yaml())
