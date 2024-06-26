import json
import os

from pygame import Vector2

from src.node import Node
from utils.constants import NODES_FILE

# saves nodes in a board in json file
def save_to_json(node_dict):
    data = {}
    for node in node_dict:
        data[f'{node.location.x};{node.location.y};{node.type}'] = 0
    try:
        with open(NODES_FILE, "x") as write_file:
            json.dump(data, write_file)
    except FileExistsError:
        os.remove(NODES_FILE)
        with open(NODES_FILE, "x") as write_file:
            json.dump(data, write_file)

# loads nodes from json file, returns start, end and dictionary with all nodes
def load_from_json():
    node_dict: dict = dict()
    start_node = None
    end_node = None

    try:
        data = json.loads(open(NODES_FILE, "r").read())
    except json.JSONDecodeError:  # if file exists but is empty or not in JSON format
        return False
    except FileNotFoundError:  # if file doesn't exist
        f = open(NODES_FILE, 'x')
        f.close()
        return False

    for node_entry in data:
        x, y, node_type = node_entry.split(';')
        x = float(x)
        y = float(y)

        node = Node(node_type, Vector2(x=x, y=y))

        if node_type == 'start':
            start_node = node
        if node_type == 'end':
            end_node = node

        node_dict[x, y] = node

    return node_dict, start_node, end_node
