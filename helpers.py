def make_valid_json(filename):
    valid_json = filename[:-3] + "_mod.txt"
    with open(filename, 'r') as contents:
        save = contents.readlines()[1:]
    with open(valid_json, 'w') as contents:
        contents.write('{ "items": [')
    with open(valid_json, 'a') as contents:
        contents.write("".join(save) + "]}")
    return valid_json
