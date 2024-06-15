import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Define shapes
SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T shape
    [[1, 1], [1, 1]],  # O shape
    [[1, 1, 0], [0, 1, 1]],  # S shape
    [[0, 1, 1], [1, 1, 0]],  # Z shape
    [[1, 0, 0], [1, 1, 1]],  # J shape
    [[0, 0, 1], [1, 1, 1]],  # L shape
    [[1, 1, 1, 1]]  # I shape
]

# Colors for shapes
SHAPE_COLORS = [CYAN, YELLOW, GREEN, RED, BLUE, ORANGE, MAGENTA]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")


class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.x = 3
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(10)] for _ in range(20)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
    return grid


def valid_space(shape, grid):
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                if (shape.x + x < 0 or shape.x + x >= 10 or shape.y + y >= 20 or grid[shape.y + y][
                    shape.x + x] != BLACK):
                    return False
    return True


def clear_rows(grid, locked):
    increment = 0
    for y in range(len(grid) - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            increment += 1
            for x in range(len(row)):
                del locked[(x, y)]
            for key in sorted(list(locked), key=lambda k: k[1])[::-1]:
                x, y2 = key
                if y2 < y:
                    new_key = (x, y2 + 1)
                    locked[new_key] = locked.pop(key)
    return increment


def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    draw_grid_lines(surface)


def draw_grid_lines(surface):
    for y in range(20):
        pygame.draw.line(surface, WHITE, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(10):
        pygame.draw.line(surface, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, WHITE)
    sx = SCREEN_WIDTH + 50
    sy = SCREEN_HEIGHT // 2 - 100
    for y, row in enumerate(shape.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, shape.color,
                                 (sx + x * BLOCK_SIZE, sy + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (sx + 10, sy - 30))


def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, WHITE)
    surface.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 30))

    font = pygame.font.SysFont('comicsans', 30)
    score_label = font.render('Score: ' + str(score), 1, WHITE)
    sx = SCREEN_WIDTH + 50
    sy = SCREEN_HEIGHT // 2 - 100
    surface.blit(score_label, (sx, sy + 160))
    pygame.display.update()


def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = Piece(random.choice(SHAPES))
    next_piece = Piece(random.choice(SHAPES))
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_speed = 0.27

        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()

        shape_pos = [(current_piece.x + x, current_piece.y + y) for y, row in enumerate(current_piece.shape) for x, cell
                     in enumerate(row) if cell]

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for x, y in shape_pos:
                locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(random.choice(SHAPES))
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(screen, grid, score)
        draw_next_shape(next_piece, screen)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
