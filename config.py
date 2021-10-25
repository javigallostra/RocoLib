PORT = 5000

WALLS_PATH = 'images/walls/'
ITEMS = 'Items'

BOULDER_COLOR_MAP = {
    'green': '#2CC990',
    'blue': '#2C82C9',
    'yellow': '#EEE657',
    'red': '#FC6042'
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
