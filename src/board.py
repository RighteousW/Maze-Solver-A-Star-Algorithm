import random

import numpy as np

import pygame
from pygame import Rect

from utils.constants import *
from utils.scripts import *


# defines blocks on the screen
class Board:
    def __init__(self, screen, rows, columns):
        self.screen = screen

        self.rows = rows
        self.columns = columns

        self.start_node = None
        self.end_node = None

        self.node_dict = dict()
        self.node_list = list()
        try:
            self.node_dict, self.node_list, self.start_node, self.end_node = load_from_json()
        except FileExistsError:
            f = open(NODES_FILE, 'a')
            f.close()
            self.new_nodes()

        self.open_nodes = []  # nodes that neighbor a closed node
        self.closed_nodes = []  # nodes that have been visited

        self.open_nodes.append(self.start_node)

        self.y_change = SCREEN_HEIGHT / self.rows
        self.x_change = SCREEN_WIDTH / self.columns

    # draw lines that make node blocks look more separate
    def draw_lines(self):

        for x in range(1, self.columns):
            pygame.draw.line(self.screen, COLOR_BLACK, (x * self.x_change, self.y_change),
                             (x * self.x_change, SCREEN_HEIGHT - self.y_change))

        for y in range(1, self.rows):
            pygame.draw.line(self.screen, COLOR_BLACK, (self.x_change, y * self.y_change),
                             (SCREEN_WIDTH - self.x_change, y * self.y_change))

    # draw the nodes
    def draw_nodes(self):
        for x in range(1, self.columns - 1):
            for y in range(1, self.rows - 1):
                is_start = NODE_TYPE[self.node_dict[x, y].type][0] == 'start_node'
                is_end = NODE_TYPE[self.node_dict[x, y].type][0] == 'end'
                is_wall = NODE_TYPE[self.node_dict[x, y].type][0] == 'wall'

                if is_start or is_end or is_wall:  # always show walls, start_node and end node
                    pygame.draw.rect(self.screen, NODE_TYPE[self.node_dict[x, y].type][1],
                                     Rect(x * self.x_change, y * self.y_change, self.x_change, self.y_change))

                elif not is_wall:
                    pygame.draw.rect(self.screen, NODE_TYPE[self.node_dict[x, y].type][1],
                                     Rect(x * self.x_change, y * self.y_change, self.x_change, self.y_change))

    # generate new nodes
    def new_nodes(self):
        for x in range(self.columns):
            for y in range(self.rows):
                number = random.randint(0, 1000)
                if number < 500:
                    type_index = 2
                else:
                    type_index = 1
                self.node_dict[x, y] = Node(type_index, Vector2(x, y))
        self.place_start_end()
        self.reset_board()
        save_to_json(self.node_dict.values())

    # randomly place start and end nodes
    def place_start_end(self):
        start_x = random.randint(1, self.columns - 1)
        start_y = random.randint(1, self.rows - 1)

        self.start_node = Node(5, Vector2(start_x, start_y))
        self.start_node.distance_from_start = 0
        self.node_dict[start_x, start_y] = self.start_node

        while True:
            end_x = random.randint(1, self.columns - 1)
            end_y = random.randint(1, self.rows - 1)

            if start_x != end_x or start_y != end_y:
                self.end_node = Node(6, Vector2(end_x, end_y))
                self.node_dict[end_x, end_y] = self.end_node
                break

    def visit_node(self, node: Node):
        self.open_nodes.remove(node)
        self.closed_nodes.append(node)
        node.type = 4

        neighbors = node.get_neighbors(self.node_list)

        for neighbor in neighbors:
            if not self.is_border_node(neighbor):

                if neighbor.location.x == node.location.x or neighbor.location.y == node.location.y:
                    distance = node.distance_from_start + NODE_STRAIGHT_DISTANCE
                else:
                    distance = node.distance_from_start + NODE_DIAGONAL_DISTANCE

                neighbor.parent_node = node
                neighbor.distance_from_start = np.minimum(neighbor.distance_from_start, distance)
                neighbor.distance_to_end = np.minimum(neighbor.distance_to_end, self.get_distance_to_end(neighbor))
                neighbor.node_type = 3

                self.open_nodes.append(neighbor)
                neighbor.node_type = 3

    def is_border_node(self, neighbor) -> bool:
        if neighbor.location.x == 0 or neighbor.location.x == self.columns:
            return True
        elif neighbor.location.y == 0 or neighbor.location.y == self.rows:
            return True
        return False

    # use current state of board to calculate next state using A* algorithm
    def next_state(self):
        if self.end_node not in self.closed_nodes and len(self.open_nodes) > 0:
            possible_node = self.open_nodes[0]

            for node in self.open_nodes:
                if node not in self.closed_nodes:
                    if node.get_distance_total() < possible_node.get_distance_total():
                        possible_node = node
                    elif (node.get_distance_total() == possible_node.get_distance_total() and
                          node.distance_to_end < possible_node.distance_to_end):
                        possible_node = node

            self.visit_node(possible_node)
        else:
            self.show_path()

    # completely solve the board if possible
    def solve(self):
        while self.end_node not in self.closed_nodes:
            self.next_state()
        self.show_path()

    def get_distance_to_end(self, neighbor):
        x_delta = abs(self.end_node.location.x - neighbor.location.x)
        y_delta = abs(self.end_node.location.y - neighbor.location.y)

        distance = np.sqrt(x_delta ** 2 + y_delta ** 2)
        return distance * NODE_STRAIGHT_DISTANCE

    def reset_board(self):
        for node in self.open_nodes:
            node.node_type = 1
        self.open_nodes.clear()
        for node in self.closed_nodes:
            node.node_type = 1
        self.closed_nodes.clear()
        self.open_nodes.append(self.start_node)

    def show_path(self):
        pass
        # current_node = self.end_node
        # next_node = current_node.parent_node
        #
        # while next_node is not None:
        #     next_node.node_type = 7
