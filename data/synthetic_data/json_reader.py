import json


def read_json(filename):
    with open('{0}.json'.format(filename)) as json_data:
        data = json.load(json_data)
        return data
