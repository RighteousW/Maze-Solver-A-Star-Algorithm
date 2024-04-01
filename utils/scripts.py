import json
import os

from pygame import Vector2

from src.node import Node
from utils.constants import NODES_FILE


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


def load_from_json():
    node_dict: dict = dict()
    start_node = None
    end_node = None

    with open(NODES_FILE, "r") as f:
        try:
            data = json.loads(f.read())
        except json.JSONDecodeError:
            return False
        except FileExistsError:
            f = open(NODES_FILE, 'a')
            f.close()

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
