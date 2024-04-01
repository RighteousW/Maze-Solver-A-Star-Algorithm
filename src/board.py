import random

import numpy as np

import pygame
from pygame import Rect, Vector2

from src.node import Node

from utils.constants import *
from utils.scripts import save_to_json, load_from_json


# defines blocks on the screen
class Board:
    def __init__(self, screen, rows, columns):
        self.screen = screen

        self.rows = rows
        self.columns = columns

        self.node_dict: dict[(int, int): Node] = {}  # map each node to its location
        self.open_nodes: list[Node] = list()  # nodes that can be visited
        self.closed_nodes: list[Node] = list()  # nodes that have been visited

        self.start_node: Node
        self.end_node: Node

        self.x_change = SCREEN_WIDTH / self.columns  # distance between grid blocks on x-axis
        self.y_change = SCREEN_HEIGHT / self.rows  # distance between grid blocks on y-axis

        try_load_json = load_from_json()
        if not try_load_json:
            self.new_nodes()
            try_load_json = load_from_json()

        (self.node_dict,
         self.start_node,
         self.end_node) = try_load_json
        
        self.start_node.distance_from_start = 0

        self.open_nodes.append(self.start_node)

        self.solved = False

    # draw lines that make grid blocks look distinct
    def draw_lines(self):

        for x in range(-1, self.columns):
            pygame.draw.line(self.screen, COLOR_BLACK, (x * self.x_change, 0),
                             (x * self.x_change, SCREEN_HEIGHT))

        for y in range(self.rows):
            pygame.draw.line(self.screen, COLOR_BLACK, (0, y * self.y_change),
                             (SCREEN_WIDTH, y * self.y_change))

    # draw the nodes
    def draw_nodes(self):
        for node in self.node_dict.values():
            is_start = node.type == 'start_node'
            is_end = node.type == 'end'
            is_wall = node.type == 'wall'

            if is_start or is_end or is_wall:  # always show walls, start_node and end node
                pygame.draw.rect(self.screen, NODE_TYPE[node.type],
                                 Rect(node.location.x * self.x_change,
                                      node.location.y * self.y_change, self.x_change, self.y_change))

            elif not is_wall:
                pygame.draw.rect(self.screen, NODE_TYPE[node.type],
                                 Rect(node.location.x * self.x_change,
                                      node.location.y * self.y_change, self.x_change, self.y_change))

    # generate new nodes
    def new_nodes(self):
        for x in range(self.columns):
            for y in range(self.rows):
                number = random.randint(0, 1000)
                if number < 450:
                    type_index = 'wall'
                else:
                    type_index = 'empty'
                self.node_dict[x, y] = Node(type_index, Vector2(x, y))
        self.place_start_end()
        self.reset_board()
        save_to_json(self.node_dict.values())

    # randomly place start and end nodes
    def place_start_end(self):
        start_x = random.randint(1, self.columns - 1)
        start_y = random.randint(1, self.rows - 1)

        self.start_node = Node('start', Vector2(start_x, start_y))
        self.start_node.distance_from_start = 0
        self.node_dict[start_x, start_y] = self.start_node

        while True:
            end_x = random.randint(1, self.columns - 1)
            end_y = random.randint(1, self.rows - 1)

            if start_x != end_x or start_y != end_y:
                self.end_node = Node('end', Vector2(end_x, end_y))
                self.node_dict[end_x, end_y] = self.end_node
                break

    def visit_node(self, node: Node):
        self.open_nodes.remove(node)
        self.closed_nodes.append(node)
        if node.type != 'start' or node.type != 'end':
            node.type = 'closed'

        neighbors = node.get_neighbors(self.node_dict.values())

        # add neighbors of visited node to list of open nodes
        for neighbor in neighbors:
            if neighbor not in self.closed_nodes:
                if neighbor.location.x == node.location.x or neighbor.location.y == node.location.y:
                    distance = node.distance_from_start + NODE_STRAIGHT_DISTANCE
                else:
                    distance = node.distance_from_start + NODE_DIAGONAL_DISTANCE

                if neighbor.distance_from_start > distance:
                    neighbor.parent_node = node
                    neighbor.distance_from_start = distance

                neighbor.distance_to_end = self.get_distance_to_end(neighbor)
                if neighbor.type != 'start' or neighbor.type != 'end':
                    neighbor.type = 'open'

                self.open_nodes.append(neighbor)

    # use current state of board to calculate next state using A* algorithm
    def next_state(self):
        # end node reached
        if self.solved or self.end_node in self.closed_nodes:
            self.show_path()
            self.solved = True
        # no possible next nodes
        elif len(self.open_nodes) == 0:
            pass
        else:
            possible_node = self.open_nodes[0]

            for node in self.open_nodes:
                if node not in self.closed_nodes:
                    if node.get_distance_total() < possible_node.get_distance_total():
                        possible_node = node
                    elif (node.get_distance_total() == possible_node.get_distance_total() and
                          node.distance_to_end < possible_node.distance_to_end):
                        possible_node = node

            self.visit_node(possible_node)

    # completely solve the board if possible
    def solve(self):
        # loop until end node found or no open nodes available
        while self.end_node not in self.closed_nodes and len(self.open_nodes) > 0:
            self.next_state()
        if self.end_node in self.closed_nodes:  # if end node has been reached show path from start to end
            self.show_path()

    def get_distance_to_end(self, neighbor):
        x_delta = abs(self.end_node.location.x - neighbor.location.x)
        y_delta = abs(self.end_node.location.y - neighbor.location.y)

        distance = np.sqrt(x_delta ** 2 + y_delta ** 2)  # distance between nodes using pythagorean theorem
        return distance * NODE_STRAIGHT_DISTANCE

    # return to start node and change all nodes calculated on to empty
    def reset_board(self):
        for node in self.open_nodes:
            node.type = 'empty'
        self.open_nodes.clear()
        for node in self.closed_nodes:
            node.node_type = 'empty'
        self.closed_nodes.clear()
        self.open_nodes.append(self.start_node)

    # show the  shortest path from start node to end node
    def show_path(self):
        current_node = self.end_node.parent_node

        while current_node is not self.start_node:
            current_node.type = 'path'
            current_node = current_node.parent_node
        self.end_node.type = 'end'
        self.start_node.type = 'start'
