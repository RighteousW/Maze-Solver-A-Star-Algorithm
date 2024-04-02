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
        self.screen: pygame.surface = screen

        self.rows = rows
        self.columns = columns

        self.node_dict: dict[(int, int): Node] = {}  # each node's location is index to the node in dict
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

        # draw vertical lines (||||)
        for x in range(self.columns):
            pygame.draw.line(self.screen, COLOR_BLACK, (x * self.x_change, 0),
                             (x * self.x_change, SCREEN_HEIGHT))

        # draw horizontal lines (----)
        for y in range(self.rows):
            pygame.draw.line(self.screen, COLOR_BLACK, (0, y * self.y_change),
                             (SCREEN_WIDTH, y * self.y_change))

    # draw the nodes
    def draw_nodes(self):
        for node in self.node_dict.values():
            pygame.draw.rect(self.screen, NODE_TYPE[node.type],
                             Rect(node.location.x * self.x_change,
                                  node.location.y * self.y_change, self.x_change, self.y_change))

    # generate new nodes for board and save to json file
    def new_nodes(self):
        for x in range(0, self.columns):
            for y in range(0, self.rows):
                number = random.randint(0, 1000)
                if number < 450:
                    node_type = 'wall'
                else:
                    node_type = 'empty'
                self.node_dict[x, y] = Node(node_type, Vector2(x, y))
        self.place_start_end()
        self.reset_board()
        save_to_json(self.node_dict.values())

    # randomly add start and end nodes to node dictionary
    # also defines start and end node of the board
    def place_start_end(self):
        start_x = random.randint(1, self.columns - 1)
        start_y = random.randint(1, self.rows - 1)

        self.start_node = Node('start', Vector2(start_x, start_y))
        self.start_node.distance_from_start = 0
        self.node_dict[start_x, start_y] = self.start_node

        # making sure end node coordinates not equal to start node
        while True:
            end_x = random.randint(1, self.columns - 1)
            end_y = random.randint(1, self.rows - 1)

            if start_x != end_x or start_y != end_y:
                self.end_node = Node('end', Vector2(end_x, end_y))
                self.node_dict[end_x, end_y] = self.end_node
                break

    # visit a node and add neighbors of the node to open nodes list
    def visit_node(self, node: Node):
        # remove from list of open nodes and
        # add to list of visited nodes to prevent visiting the node again
        self.open_nodes.remove(node)
        self.closed_nodes.append(node)

        if node.type != 'start' or node.type != 'end':
            node.type = 'closed'

        neighbors = node.get_neighbors(self.node_dict.values())

        # add neighbors of visited node to list of open nodes
        for neighbor in neighbors:
            if neighbor not in self.closed_nodes:
                # update neighbor node if a shorter way to it from start node is found
                if neighbor.location.x == node.location.x or neighbor.location.y == node.location.y:
                    distance = node.distance_from_start + NODE_STRAIGHT_DISTANCE
                else:
                    distance = node.distance_from_start + NODE_DIAGONAL_DISTANCE

                if neighbor.distance_from_start > distance:
                    neighbor.parent_node = node
                    neighbor.distance_from_start = distance

                # calculate neighbor node's distance to end if not yet calculated
                if neighbor.distance_to_end == MAX_SIZE:
                    neighbor.distance_to_end = self.get_distance_to_end(neighbor)
                if neighbor.type != 'start' or neighbor.type != 'end':
                    neighbor.type = 'open'

                self.open_nodes.append(neighbor)

    # use current state of board to calculate next state using A* algorithm
    def next_state(self):
        # end node reached or board already solved
        if self.solved or self.end_node in self.closed_nodes:
            self.show_path()
            self.solved = True
        # no possible next nodes
        elif len(self.open_nodes) == 0:
            pass
        # next state of board can be calculated
        else:
            # arbitrary selection of a possible node
            possible_node = self.open_nodes[0]

            for node in self.open_nodes:
                if node not in self.closed_nodes:
                    # if node's distance total is less than possible node's update possible node to the new node
                    if node.get_distance_total() < possible_node.get_distance_total():
                        possible_node = node
                    # if distance total is the same,
                    # update the possible node to the node with the smallest distance to end
                    elif (node.get_distance_total() == possible_node.get_distance_total() and
                          node.distance_to_end < possible_node.distance_to_end):
                        possible_node = node

            self.visit_node(possible_node)

    # completely solve the board if possible
    def solve(self):
        # loop until end node found or no open nodes available
        while self.end_node not in self.closed_nodes or len(self.open_nodes) == 0:
            self.next_state()
        # if end node has been reached show path from start to end
        if self.end_node in self.closed_nodes:
            self.show_path()

    # calculate a node's distance to end using pythagorean theorem
    def get_distance_to_end(self, neighbor: Node):
        x_delta = abs(self.end_node.location.x - neighbor.location.x)
        y_delta = abs(self.end_node.location.y - neighbor.location.y)

        distance = np.sqrt(x_delta ** 2 + y_delta ** 2)  # distance between nodes using pythagorean theorem
        return distance * NODE_STRAIGHT_DISTANCE

    # return board to initial state
    def reset_board(self):
        # make all possible nodes empty apart from start and end nodes
        for node in self.open_nodes:
            if node.type != 'start' or 'end':
                node.type = 'empty'
        self.open_nodes.clear()

        # make all visited nodes empty apart from start and end nodes
        for node in self.closed_nodes:
            if node.type != 'start' or 'end':
                node.type = 'empty'
        self.closed_nodes.clear()

        # make the boards state to not solved
        self.solved = False

        # make the only possible node the start node
        self.open_nodes.append(self.start_node)

    # show the  shortest path from start node to end node
    def show_path(self):
        current_node = self.end_node.parent_node

        while current_node is not self.start_node:
            current_node.type = 'path'
            current_node = current_node.parent_node
        self.end_node.type = 'end'
        self.start_node.type = 'start'
