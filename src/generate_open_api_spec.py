import json
from api.blueprint import get_auth_token, get_boulder_by_id, get_boulder_by_name
from api.blueprint import get_gym_boulders, get_gym_pretty_name, get_gym_wall_name
from api.blueprint import get_gyms, get_gym_walls, boulder_create, test_auth, new_user
from api.blueprint import get_user_ticklist, rate_boulder, mark_boulder_as_done
from api.blueprint import get_user_preferences


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
    from api.schemas import BoulderSchema
    from api.schemas import BoulderIDParameter
    from api.schemas import BoulderNameParameter
    from api.schemas import GymIDParameter
    from api.schemas import CreateBoulderRequestBody
    from api.schemas import CreateBoulderResponseBody
    from api.schemas import AuthenticationRequestBody
    from api.schemas import AuthenticationResponseBody
    from api.schemas import SignUpRequestBody
    from api.schemas import SignUpResponseBody
    from api.schemas import TestTokenResponseBody
    from api.schemas import TicklistBoulderSchema
    from api.schemas import TicklistResponseBody
    from api.schemas import RateBoulderRequestBody
    from api.schemas import RateBoulderResponseBody
    from api.schemas import MarkDoneBoulderRequestBody
    from api.schemas import MarkDoneBoulderResponseBody
    from api.schemas import UserPreferencesResponseBody
    from api.schemas import ErrorResponse

    spec.components.schema("Gyms", schema=GymListSchema)
    spec.components.schema("Walls", schema=WallListSchema)
    spec.components.schema("Boulder", schema=BoulderSchema)
    spec.components.schema("Boulders", schema=GymBoulderListSchema)
    spec.components.schema("GymName", schema=GymNameSchema)
    spec.components.schema("WallName", schema=WallNameSchema)
    spec.components.schema(
        "CreateBoulder", schema=CreateBoulderRequestBody)
    spec.components.schema("CreateBoulderResponse",
                           schema=CreateBoulderResponseBody)
    spec.components.schema("GymIDParameter", schema=GymIDParameter)
    spec.components.schema("BoulderIDParameter", schema=BoulderIDParameter)
    spec.components.schema("BoulderNameParameter", schema=BoulderNameParameter)
    spec.components.schema("AuthenticationRequestBody",
                           schema=AuthenticationRequestBody)
    spec.components.schema("AuthenticationResponseBody",
                           schema=AuthenticationResponseBody)
    spec.components.schema("SignUpRequestBody", schema=SignUpRequestBody)
    spec.components.schema("SignUpResponseBody", schema=SignUpResponseBody)
    spec.components.schema("TestTokenResponseBody",
                           schema=TestTokenResponseBody)
    spec.components.schema("TicklistBoulder",
                           schema=TicklistBoulderSchema)
    spec.components.schema("TicklistResponseBody",
                           schema=TicklistResponseBody)
    spec.components.schema("RateBoulderRequestBody",
                           schema=RateBoulderRequestBody)
    spec.components.schema("RateBoulderResponseBody",
                           schema=RateBoulderResponseBody)
    spec.components.schema("MarkDoneBoulderRequestBody",
                           schema=MarkDoneBoulderRequestBody)
    spec.components.schema("MarkDoneBoulderResponseBody",
                           schema=MarkDoneBoulderResponseBody)
    spec.components.schema("UserPreferencesResponseBody",
                           schema=UserPreferencesResponseBody)
    spec.components.schema("ErrorResponse",
                           schema=ErrorResponse)

    with app.test_request_context():
        spec.path(view=get_gyms)
        spec.path(view=get_gym_walls)
        spec.path(view=get_gym_pretty_name)
        spec.path(view=get_gym_wall_name)
        spec.path(view=get_gym_boulders)
        spec.path(view=get_boulder_by_id)
        spec.path(view=get_boulder_by_name)
        spec.path(view=boulder_create)
        spec.path(view=new_user)
        spec.path(view=get_auth_token)
        spec.path(view=test_auth)
        spec.path(view=get_user_ticklist)
        spec.path(view=rate_boulder)
        spec.path(view=mark_boulder_as_done)
        spec.path(view=get_user_preferences)
    with open('./static/swagger/swagger.json', 'w') as f:
        json.dump(spec.to_dict(), f)
