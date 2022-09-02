from sys import argv

CREDS = 'creds.txt'
CREDS_DEV = 'creds.dev.txt'
CREDS_LOCAL = 'creds.local.txt'

PORT = 5050

DB_NAME = 'RocoLib'
WALLS_PATH = 'images/walls/'
ITEMS = 'Items'

DOCKER_ENV = "False"
if len(argv) > 1 and str(argv[1]) == "docker":
    DOCKER_ENV = "True"

DEBUG = False
API_VERSION = 'v1'
SWAGGER_URL = f'/api/{API_VERSION}/docs'
API_URL = f'/api/{API_VERSION}/docs/swagger.json'
GENERATE_API_DOCS = True
RUN_SERVER = True
DEFAULT_LANG = 'en_US'

BOULDER_COLOR_MAP = {
    'green': '#2CC990',
    'blue': '#2C82C9',
    'yellow': '#EEE657',
    'red': '#FC6042'
}
BOULDER_DIFFICULTY_MAP = {
    0: 'green',
    1: 'blue',
    2: 'yellow',
    3: 'red'
}
FIELDS_TO_MAP = {
    'difficulty': BOULDER_DIFFICULTY_MAP
}

# For DB querying
EQUALS = ['section', 'difficulty']
RANGE = ['rating']
CONTAINS = ['creator']

# Mappings of DB feet field values to friendly text to render
FEET_MAPPINGS = {
    'free': 'Free feet',
    'follow': 'Feet follow hands',
    'no-feet': 'Campus',
}
