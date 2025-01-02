import pygame
import sys
import random
import heapq

pygame.init()

# Game settings
SCREEN_WIDTH = 560
SCREEN_HEIGHT = 620
CELL_SIZE = 20
FPS = 4

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)

# Initialize screen and fonts
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man")
font = pygame.font.SysFont('Arial', 22)

# Game board setup
board = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "######.##### ## #####.######",
    "######.##          ##.######",
    "######.## ###--### ##.######",
    "######.## #      # ##.######",
    "#      ## #      # ##       #",
    "######.## #      # ##.######",
    "######.## ######## ##.######",
    "######.##          ##.######",
    "######.## ######## ##.######",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

# Game variables
pacman_x, pacman_y = 9, 13  # Initial pacman position
pacman_direction = 'LEFT'
score = 0
ghosts = [
    {'x': 8, 'y': 7}, {'x': 15, 'y': 7}, {'x': 10, 'y': 10}, {'x': 12, 'y': 15}, {'x': 8, 'y': 6}
]
ghost_paths = [{}, {}, {}, {}, {}]  # Precomputed paths for static ghosts

# Load Pac-Man and ghost images
pacman_image = pygame.image.load('pacman_PNG.webp')
pacman_image = pygame.transform.scale(pacman_image, (CELL_SIZE, CELL_SIZE))

ghost_images = [
    pygame.image.load('ghost_red.webp'),
    pygame.image.load('ghost_green.webp'),
    pygame.image.load('ghost_Cyan.jpg'),
    pygame.image.load('ghost_blue.jpg'),
    pygame.image.load('ghost_PInko.jpg')
]
ghost_images = [pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE)) for img in ghost_images]

# Heuristic for A* algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* algorithm for pathfinding
def a_star_search(start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next = (x + dx, y + dy)
            if board[next[1]][next[0]] != '#':
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

    return came_from

# Reconstruct the path from A* results
def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Draw the game board
def draw_board():
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell == '#':
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == '.':
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 3.75)
            elif cell == 'o':
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 7.5)

# Draw Pac-Man
def draw_pacman():
    screen.blit(pacman_image, (pacman_x * CELL_SIZE, pacman_y * CELL_SIZE))

# Draw ghosts
def draw_ghosts():
    for i, ghost in enumerate(ghosts):
        screen.blit(ghost_images[i], (ghost['x'] * CELL_SIZE, ghost['y'] * CELL_SIZE))

# Move Pac-Man
def move_pacman():
    global pacman_x, pacman_y, score
    if pacman_direction == 'LEFT' and board[pacman_y][pacman_x - 1] != '#':
        pacman_x -= 1
    elif pacman_direction == 'RIGHT' and board[pacman_y][pacman_x + 1] != '#':
        pacman_x += 1
    elif pacman_direction == 'UP' and board[pacman_y - 1][pacman_x] != '#':
        pacman_y -= 1
    elif pacman_direction == 'DOWN' and board[pacman_y + 1][pacman_x] != '#':
        pacman_y += 1

    if board[pacman_y][pacman_x] == '.':
        board[pacman_y] = board[pacman_y][:pacman_x] + ' ' + board[pacman_y][pacman_x + 1:]
        score += 10
    elif board[pacman_y][pacman_x] == 'o':
        board[pacman_y] = board[pacman_y][:pacman_x] + ' ' + board[pacman_y][pacman_x + 1:]
        score += 50

# Move ghosts
def move_ghosts():
    global ghost_paths
    for i, ghost in enumerate(ghosts):
        if i == 0 or i == 1:  # A* ghosts
            path = reconstruct_path(a_star_search((ghost['x'], ghost['y']), (pacman_x, pacman_y)), (ghost['x'], ghost['y']), (pacman_x, pacman_y))
            if path:
                ghost['x'], ghost['y'] = path[0]
        else:  # Static path ghosts
            if ghost_paths[i]:
                ghost['x'], ghost['y'] = ghost_paths[i].pop(0)
            else:
                while True:
                    target_x = ghost['x'] + random.randint(-3, 3)
                    target_y = ghost['y'] + random.randint(-3, 3)
                    if 0 <= target_x < len(board[0]) and 0 <= target_y < len(board) and board[target_y][target_x] != '#':
                        break
                ghost_paths[i] = reconstruct_path(a_star_search((ghost['x'], ghost['y']), (target_x, target_y)), (ghost['x'], ghost['y']), (target_x, target_y))

# Check for collisions
def check_collisions():
    for ghost in ghosts:
        if ghost['x'] == pacman_x and ghost['y'] == pacman_y:
            return True
    return False

# Check if all pellets are eaten
def check_all_pellets_eaten():
    for row in board:
        if '.' in row or 'o' in row:
            return False
    return True

# Reset game variables
def reset_game():
    global pacman_x, pacman_y, score, board
    pacman_x, pacman_y = 9, 13
    score = 0
    board[:] = [
        "############################",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#o####.#####.##.#####.####o#",
        "#.####.#####.##.#####.####.#",
        "#..........................#",
        "#.####.##.########.##.####.#",
        "#.####.##.########.##.####.#",
        "#......##....##....##......#",
        "######.##### ## #####.######",
        "######.##### ## #####.######",
        "######.##          ##.######",
        "######.## ###--### ##.######",
        "######.## #      # ##.######",
        "#      ## #      # ##       #",
        "######.## #      # ##.######",
        "######.## ######## ##.######",
        "######.##          ##.######",
        "######.## ######## ##.######",
        "######.## ######## ##.######",
        "#............##............#",
        "#.####.#####.##.#####.####.#",
        "#.####.#####.##.#####.####.#",
        "#o..##................##..o#",
        "###.##.##.########.##.##.###",
        "###.##.##.########.##.##.###",
        "#......##....##....##......#",
        "#.##########.##.##########.#",
        "#.##########.##.##########.#",
        "#..........................#",
        "############################"
    ]

# Game over screen
def game_over():
    while True:
        screen.fill(BLACK)
        message = font.render("Game Over! Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(message, (SCREEN_WIDTH // 8, SCREEN_HEIGHT // 3))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    reset_game()
                    return

# Main game loop
def game_loop():
    global pacman_direction
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    pacman_direction = 'LEFT'
                elif event.key == pygame.K_RIGHT:
                    pacman_direction = 'RIGHT'
                elif event.key == pygame.K_UP:
                    pacman_direction = 'UP'
                elif event.key == pygame.K_DOWN:
                    pacman_direction = 'DOWN'

        move_pacman()
        move_ghosts()

        if check_collisions():
            game_over()
            continue

        if check_all_pellets_eaten():
            print("You Win!")
            reset_game()

        screen.fill(BLACK)
        draw_board()
        draw_pacman()
        draw_ghosts()

        score_text = font.render(f"Score: {score}", True, GREEN)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

game_loop()
