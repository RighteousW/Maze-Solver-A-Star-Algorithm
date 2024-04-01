from utils.constants import MAX_SIZE
from pygame import Vector2


# defines a block on the board
# can be a wall or any other state
class Node:
    def __init__(self, node_type: str, location: Vector2):
        self.type: str = node_type
        self.location: Vector2 = location

        self.distance_from_start = MAX_SIZE
        self.distance_to_end = MAX_SIZE

        self.parent_node: Node

    # returns list containing all neighboring nodes of self node, neighbors can be
    # top-left, top, top-right, middle-left, middle, middle-right, bottom-left, bottom, bottom-right of self node
    def get_neighbors(self, node_list: list) -> list:
        result = []
        for node in node_list:
            if self.is_neighbor(node) and node.type != 'wall':
                result.append(node)
        return result

    def get_distance_total(self):
        return self.distance_from_start + self.distance_to_end

    # returns if a certain node is a neighbor of self node
    def is_neighbor(self, node) -> bool:
        # nodes directly up, down, left and right of self node
        if self.location == Vector2(node.location.x + 1, node.location.y):
            return True
        elif self.location == Vector2(node.location.x - 1, node.location.y):
            return True
        elif self.location == Vector2(node.location.x, node.location.y + 1):
            return True
        elif self.location == Vector2(node.location.x, node.location.y - 1):
            return True

        # nodes diagonal of self node
        elif self.location == Vector2(node.location.x + 1, node.location.y + 1):
            return True
        elif self.location == Vector2(node.location.x + 1, node.location.y - 1):
            return True
        elif self.location == Vector2(node.location.x - 1, node.location.y + 1):
            return True
        elif self.location == Vector2(node.location.x - 1, node.location.y - 1):
            return True

        else:
            return False
