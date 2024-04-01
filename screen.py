import pygame

from src.board import Board
from utils.constants import *


class Screen:
    def __init__(self, rows: int = 10, columns: int = 10):
        pygame.init()
        pygame.display.set_caption("Maze")

        self.rows = rows + 2
        self.columns = columns + 2
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.board = Board(screen=self.screen, rows=self.rows, columns=self.columns)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # on pressing exit on window
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:  # new nodes
                self.board.new_nodes()
                self.board = Board(screen=self.screen, rows=self.rows, columns=self.columns)
            if keys[pygame.K_w]:  # next state of solution
                self.board.next_state()
            if keys[pygame.K_s]:  # completely solve board if possible
                self.board.solve()
            if keys[pygame.K_e]:  # refresh state of maze to unsolved
                self.board = Board(screen=self.screen, rows=self.rows, columns=self.columns)

            # cover all changes with black, to only look at current state
            self.screen.fill(COLOR_WHITE)

            # renders
            self.board.draw_nodes()
            self.board.draw_lines()

            # update window and sleep program to match frame rate
            pygame.display.update()
            self.clock.tick(FRAME_RATE)


Screen(30, 30).run()
