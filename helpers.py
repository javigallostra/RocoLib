def make_valid_json(filename, json_filename, skip_lines=1):
    """
    From a file with comma separated JSON like dictionaries
    return a valid JSON object.
    """
    with open(filename, 'r') as contents:
        save = contents.readlines()[skip_lines:]
    with open(json_filename, 'w') as contents:
        contents.write('{ "items": [')
    with open(json_filename, 'a') as contents:
        contents.write("".join(save) + "]}")
    return 1
