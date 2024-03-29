from utils.constants import MAX_SIZE
from utils.scripts import *


# defines a block on the board
# can be a wall or any other state
class Node:
    def __init__(self, node_type: int, location: Vector2):
        self.type: int = node_type
        self.location: Vector2 = location

        self.distance_from_start = MAX_SIZE
        self.distance_to_end = MAX_SIZE

        self.parent_node = None

    def get_neighbors(self, node_list: []) -> []:
        result = []
        for node in node_list:
            if self.is_neighbor(node) and node.type != 2:
                result.append(node)
        return result

    def get_distance_total(self):
        return self.distance_from_start + self.distance_to_end

    def get_distance_to_end(self):
        return self.distance_to_end

    def is_neighbor(self, node2) -> bool:
        if self.location == Vector2(node2.location.x + 1, node2.location.y):
            return True
        elif self.location == Vector2(node2.location.x - 1, node2.location.y):
            return True
        elif self.location == Vector2(node2.location.x, node2.location.y + 1):
            return True
        elif self.location == Vector2(node2.location.x, node2.location.y - 1):
            return True

        elif self.location == Vector2(node2.location.x + 1, node2.location.y + 1):
            return True
        elif self.location == Vector2(node2.location.x + 1, node2.location.y - 1):
            return True
        elif self.location == Vector2(node2.location.x - 1, node2.location.y + 1):
            return True
        elif self.location == Vector2(node2.location.x - 1, node2.location.y - 1):
            return True

        else:
            return False
