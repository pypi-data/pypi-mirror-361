# snake-game.py
import pygame, sys
from pygame.math import Vector2
from random import randint
import os
import pathlib

# Get the directory where this script is located
GAME_DIR = pathlib.Path(__file__).parent

# Helper function to get asset paths
def get_asset_path(filename):
    return str(GAME_DIR / "assets" / filename)

def get_font_path(filename):
    return str(GAME_DIR / "retro-font" / filename)

# State
state = "title"

grid_top  = 100
cell_size = 32
max_cols = 800 // cell_size
max_rows = (600 - grid_top) // cell_size + 1

# Save path and file
save_path = pathlib.Path.home() / ".local" / "share" / "retro-snake-game"
save_file = save_path / "highscore.txt"

def load_highscore() -> int:
    try:
        return int(save_file.read_text())
    except (FileNotFoundError, ValueError):
        return 0

def save_highscore(value: int) -> None:
    save_path.mkdir(parents=True, exist_ok=True)
    save_file.write_text(str(value))

# Class for apple
class Apple:
    def __init__(self, occupied):
        self.reposition(occupied)

    def reposition(self, occupied):
        self.pos = Vector2(randint(0, max_cols -1),
                           randint(0, max_rows -1))

        # Avoid overlap
        while self.pos in occupied:
            self.pos.update(randint(0, max_cols - 1),
                            randint(0, max_rows - 1))
            print("Avoided overlap successfully")

    def draw_apple(self):
        offset = (cell_size - apple_size) // 2
        px = self.pos.x * cell_size + offset
        py = grid_top + self.pos.y * cell_size + offset
        idx = (pygame.time.get_ticks() // 120) % 2
        screen.blit(apple_frames[idx], (px, py))

# Class for snake
class Snake:
    def __init__(self):
        self.body = [Vector2(6, 11), Vector2(5, 11), Vector2(4, 11), Vector2(3, 11)]
        self.direction = Vector2(1, 0)
        self.grow = False

    def draw_snake(self):
        for i, block in enumerate(self.body):
            px = block.x * cell_size
            py = grid_top + block.y * cell_size

            if i == 0:
                img = HEAD[tuple(self.direction)]

            elif i == len(self.body)-1:
                tail_dir = self.body[-2] - self.body[-1]
                img = TAIL[tuple(tail_dir)]

            else:
                prev_vec = self.body[i-1] - block
                next_vec = self.body[i+1] - block

                if prev_vec.x == next_vec.x:
                    img = body_v
                elif prev_vec.y == next_vec.y:
                    img = body_h
                else:
                    img = CORNERS[(tuple(prev_vec), tuple(next_vec))]

            screen.blit(img, (px, py))

    def move_snake(self):
        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)

        if self.grow:
            self.grow = False
        else:
            self.body.pop()

# Class for game logic
class Logic:
    def __init__(self):
        self.snake = Snake()
        self.apple = Apple(self.snake.body)
        self.score = 0

    def apple_pickup(self):
        if self.snake.body[0] == self.apple.pos:
            self.snake.grow = True
            self.score += 1
            coin_sound.play()
            self.apple.reposition(self.snake.body)

    def check_collisions(self):
        head = self.snake.body[0]
        if head.x < 0 or head.x >= max_cols or head.y < 0 or head.y >= max_rows:
            return True

        if head in self.snake.body[1:]:
            return True

        return False

pygame.init()
pygame.mixer.init()

high_score = load_highscore()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Retro Snake Game")

# Tile startup sound
title_sound = pygame.mixer.Sound(get_asset_path("title_sound.wav"))

# Load sounds
startup_sound = pygame.mixer.Sound(get_asset_path("game_start.wav"))
bg_sound = pygame.mixer.Sound(get_asset_path("sound.wav"))

# Coin sound effect
coin_sound = pygame.mixer.Sound(get_asset_path("coin.wav"))

# Game over sound effect
game_over_sfx = pygame.mixer.Sound(get_asset_path("game_over.wav"))

# Apple imgages
apple_size = int(cell_size * 3.3)
small_scale = 0.75

# big apple
apple_big = pygame.image.load(get_asset_path("apple.png")).convert_alpha()
apple_big = pygame.transform.scale(apple_big, (apple_size, apple_size))

# small apple
apple_small_raw = pygame.image.load(get_asset_path("small_apple.png")).convert_alpha()
w  = int(apple_size * small_scale)
h  = int(apple_size * small_scale)
apple_small_raw = pygame.transform.scale(apple_small_raw, (w, h))

apple_small = pygame.Surface((apple_size, apple_size), pygame.SRCALPHA)
apple_small.blit(apple_small_raw, ((apple_size - w)//2, (apple_size - h)//2))

apple_frames = [apple_big, apple_small]

# Snake sheet
sheet = pygame.image.load(get_asset_path("snake_sheet.png")).convert_alpha()
tile = sheet.get_width() // 3
tiles = [[None]*3 for _ in range(3)]

# Background
bg_play = pygame.image.load(get_asset_path("background.png")).convert()
bg_play = pygame.transform.scale(bg_play, (800, 600 - grid_top))

for r in range(3):
    for c in range(3):
        rect = pygame.Rect(c*tile, r*tile, tile, tile)
        tiles[r][c] = sheet.subsurface(rect)

tiles = [[pygame.transform.scale(tile, (cell_size, cell_size))
          for tile in row]
         for row in tiles]

head_up = tiles[0][0]
corner_tl = tiles[0][1]
corner_tr = tiles[0][2]
corner_bl = tiles[1][1]
corner_br = tiles[1][2]
tail_up = tiles[2][1]
body_straight = tiles[2][2]

# Lookup tables
HEAD = {
    (0, -1): head_up,
    (1, 0): pygame.transform.rotate(head_up, -90), # right
    (0, 1): pygame.transform.flip(head_up, False, True), # down
    (-1, 0): pygame.transform.rotate(head_up, 90) # left
}

TAIL = {
    (0, -1): tail_up,
    (1, 0): pygame.transform.rotate(tail_up, -90), # right
    (0, 1): pygame.transform.flip(tail_up, False, True), # down
    (-1, 0): pygame.transform.rotate(tail_up, 90) # left
}

CORNERS = {
    ((-1,0), (0,-1)): corner_br, ((0,-1), (-1,0)): corner_br,
    (( 1,0), (0,-1)): corner_bl, ((0,-1), ( 1,0)): corner_bl,
    ((-1,0), (0, 1)): corner_tr, ((0, 1), (-1,0)): corner_tr,
    (( 1,0), (0, 1)): corner_tl, ((0, 1), ( 1,0)): corner_tl
}

body_v = body_straight
body_h = pygame.transform.rotate(body_straight, 90)

# Move
MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, 150)

# Scan set up
scan = pygame.Surface((800, 600), flags=pygame.SRCALPHA)
for y in range(0, 600, 2):
    pygame.draw.line(scan, (0, 0, 0, 100), (0, y), (800, y))

# Fonts
title_font = pygame.font.Font(get_font_path("PressStart2P-Regular.ttf"), 45)
enter_coin_font = pygame.font.Font(get_font_path("PressStart2P-Regular.ttf"), 23)
volume_font = pygame.font.Font(get_font_path("PressStart2P-Regular.ttf"), 20)
scores = pygame.font.Font(get_font_path("PressStart2P-Regular.ttf"), 40)
title_color = pygame.Color("goldenrod")
border_color = (80, 250, 80)

# Animate text set up
message = "Retro Snake Game"
count = 0
speed = 3
done = False

# Flicker set up
flicker_duration = 20
flicker_interval = 1
show_text = True
frame_count = 0
flicker_done = False

# Play startup sound
intro_chan = startup_sound.play()
title_chan = None
bg_started = False

# Class
logic = Logic()
game_over = False

clock = pygame.time.Clock()
# Game loop
running = True
while running:
    clock.tick(60)
    frame_count += 1
    collision = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == "title":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN,
                                                              pygame.K_KP_ENTER):
                # Start game
                title_chan = title_sound.play()
                state = "playing"
                continue

        elif state == "playing":
            if event.type == MOVE_EVENT:
                if not game_over:
                    # Stop snake from moving
                    snake = logic.snake
                    next_head = snake.body[0] + snake.direction

                    hit_wall = (next_head.x < 0 or next_head.x >= max_cols or
                                next_head.y < 0 or next_head.y >= max_rows)
                    hit_self = next_head in snake.body

                    if hit_wall or hit_self:
                        game_over = True
                        bg_sound.stop()
                        game_over_sfx.play()
                        state = "game_over"

                        if logic.score > high_score:
                            high_score = logic.score
                            save_highscore(high_score)
                    else:
                        snake.move_snake()
                        logic.apple_pickup()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if logic.snake.direction.y != 1:
                        logic.snake.direction = Vector2(0, -1)

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if logic.snake.direction.y != -1:
                        logic.snake.direction = Vector2(0, 1)

                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if logic.snake.direction.x != 1:
                        logic.snake.direction = Vector2(-1, 0)

                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if logic.snake.direction.x != -1:
                        logic.snake.direction = Vector2(1, 0)

        elif state == "game_over":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN,
                                                              pygame.K_KP_ENTER):
                # Restart game
                title_sound.play()
                logic = Logic()
                game_over = False
                bg_started = False
                state = "playing"

    # States
    if state == "playing" and not game_over and not bg_started:
        intro_done = not intro_chan.get_busy()
        title_done = not (title_chan and title_chan.get_busy())
        if intro_done and title_done:
            bg_sound.play(loops=-1)
            bg_started = True

    screen.fill((15, 56, 15))

    if state == "title":
        screen.fill((15, 56, 15))
        title = title_font.render("Retro Snake Game", True, title_color)
        prompt = enter_coin_font.render("Enter coin (press ENTER) to start", True, (57, 255, 20))
        volume = volume_font.render("Turn volume up for maximun experience", True, (57, 225, 20))
        screen.blit(title, title.get_rect(center=(400, 150)))
        screen.blit(prompt, prompt.get_rect(center=(400, 280)))
        screen.blit(volume, volume.get_rect(center=(400, 410)))

        # Title border
        border_rect = screen.get_rect()
        pygame.draw.rect(screen, border_color, border_rect, 2)

    elif state == "playing":
        if collision:
            continue

        # Color background
        play_rect = pygame.Rect(0, grid_top, 800, 600 - grid_top)
        screen.blit(bg_play, play_rect.topleft)

        # Border
        pygame.draw.rect(screen, border_color, play_rect, width=2)

        # Flicker
        if not flicker_done:
            if frame_count % flicker_interval == 0:
                show_text = not show_text
            if frame_count >= flicker_duration:
                flicker_done = True
                show_text = True

                if show_text:
                    # Show label
                    title_text = title_font.render("Retro Snake Game", True, title_color)
                    title_rect = title_text.get_rect(center=(800 // 2, 50))
                    screen.blit(title_text, title_rect)

        else:
            # Animate typing effect
            if not done:
                if count < speed * len(message):
                    count += 1
                else:
                    done = True

            snip = title_font.render(message[0:count // speed], True, title_color)
            snip_rect = snip.get_rect(center=(800 // 2, 50))
            screen.blit(snip, snip_rect)

        logic.apple.draw_apple()
        logic.snake.draw_snake()

    if state == "game_over":
        screen.fill((15, 56, 15))

        # Game Over
        over = title_font.render("GAME OVER", True, title_color)
        screen.blit(over, over.get_rect(center=(400, 140)))

        # Score
        score = scores.render(f"Score: {logic.score}", True, (57, 255, 20))
        screen.blit(score, score.get_rect(center=(400, 235)))

        # Highscore
        highscore = scores.render(f"High Score: {high_score}", True, (57, 255, 20))
        screen.blit(highscore, highscore.get_rect(center=(400, 300)))

        # Restart
        restart = volume_font.render("Insert coin (press ENTER) to restart", True, (57, 255, 20))
        screen.blit(restart, restart.get_rect(center=(400, 415)))

        # Title border
        border_rect = screen.get_rect()
        pygame.draw.rect(screen, border_color, border_rect, 2)

    screen.blit(scan, (0, 0))
    pygame.display.update()

pygame.quit()
sys.exit()
