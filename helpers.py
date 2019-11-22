def make_valid_json(filename, skip_lines=1):
    """
    From a file with comma separated JSON like dictionaries
    return a valid JSON object.
    """
    valid_json = filename[:-3] + "_mod.txt"
    with open(filename, 'r') as contents:
        save = contents.readlines()[skip_lines:]
    with open(valid_json, 'w') as contents:
        contents.write('{ "items": [')
    with open(valid_json, 'a') as contents:
        contents.write("".join(save) + "]}")
    return valid_json
