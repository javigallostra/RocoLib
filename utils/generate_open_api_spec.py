import json
from api.blueprint import get_gym_boulders, get_gym_pretty_name, get_gym_wall_name, get_gyms, get_gym_walls, boulder_create

def generate_api_docs(app) -> None:
    """
    Generate the OpenAPI spec doc
    """
    # Generate API documentation
    from api.schemas import spec
    from api.schemas import GymListSchema
    from api.schemas import WallListSchema
    from api.schemas import GymNameSchema
    from api.schemas import WallNameSchema
    from api.schemas import GymBoulderListSchema
    from api.schemas import CreateBoulderRequestBody
    from api.schemas import CreateBoulderResponseBody
    from api.schemas import CreateBoulderErrorResponse
    spec.components.schema("Gyms", schema=GymListSchema)
    spec.components.schema("Walls", schema=WallListSchema)
    spec.components.schema("Boulders", schema=GymBoulderListSchema)
    spec.components.schema("GymName", schema=GymNameSchema)
    spec.components.schema("WallName", schema=WallNameSchema)
    spec.components.schema(
        "CreateBoulder", schema=CreateBoulderRequestBody)
    spec.components.schema("CreateBoulderResponse",
                           schema=CreateBoulderResponseBody)
    spec.components.schema("CreateBoulderErrorResponse",
                           schema=CreateBoulderErrorResponse)
    with app.test_request_context():
        spec.path(view=get_gyms)
        spec.path(view=get_gym_walls)
        spec.path(view=get_gym_pretty_name)
        spec.path(view=get_gym_wall_name)
        spec.path(view=get_gym_boulders)
        spec.path(view=boulder_create)
    with open('./static/swagger/swagger.json', 'w') as f:
        json.dump(spec.to_dict(), f)
