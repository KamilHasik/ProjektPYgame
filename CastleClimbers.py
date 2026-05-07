import pygame
import os
import random

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

camera_y = 0

# SKALOWANE WARTOŚCI - 1/3 na ściany, 1/3 na środek
wall_thickness = WIDTH // 3
right_wall_x = WIDTH - wall_thickness

player_size = int(HEIGHT * 0.1)
platform_width = int(WIDTH * 0.12)
platform_height = int(HEIGHT * 0.02)

jump_power = -10.5
gravity = 0.35
move_speed = int(WIDTH * 0.008)

x = WIDTH // 2
y = HEIGHT - int(HEIGHT * 0.15)
y_velocity = 0

danger_y = HEIGHT + int(HEIGHT * 0.3)
danger_speed = 2 # STAŁA PRĘDKOŚĆ (bez przyspieszania)

left_wall = pygame.Rect(0, 0, wall_thickness, 100000)
right_wall = pygame.Rect(right_wall_x, 0, wall_thickness, 100000)

tile_width = wall_thickness // 2
tile_height = tile_width

# Wczytanie tła
background_image = None
background_path = os.path.join("Graphic", "Player", "Background.jpg")
try:
    background_image = pygame.image.load(background_path)
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    print("Zaladowano tło")
except:
    print("Nie zaladowano tła")

tiles = []

tile_names = [
    "tile 1.jpg",
    "tile 2.jpg",
    "tile 3.jpg",
    "tile 4.jpg",
    "tile 5.jpg",
    "tile 6.jpg",
    "tile 7.jpg",
    "tile 8.jpg",
    "tile 9.jpg"
]

for tile_name in tile_names:
    tile_path = os.path.join("Graphic", "Tiles", tile_name)
    try:
        tile_image = pygame.image.load(tile_path)
        tile_image = pygame.transform.scale(tile_image, (tile_width, tile_height))
        tiles.append(tile_image)
    except:
        fallback = pygame.Surface((tile_width, tile_height))
        fallback.fill((150, 150, 150))
        tiles.append(fallback)

flying_frames = []
for i in range(36):
    frame_path = os.path.join("Graphic", "Player", "Flying", f"Flying {i}.png")
    try:
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (player_size, player_size))
        flying_frames.append(frame)
    except:
        fallback = pygame.Surface((player_size, player_size))
        fallback.fill((255, 255, 0))
        flying_frames.append(fallback)

walking_right_frames = []
for i in range(36):
    frame_path = os.path.join("Graphic", "Player", "WalkingRight", f"WalkRight {i}.png")
    try:
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (player_size, player_size))
        walking_right_frames.append(frame)
    except:
        fallback = pygame.Surface((player_size, player_size))
        fallback.fill((0, 255, 0))
        walking_right_frames.append(fallback)

walking_left_frames = []
for i in range(36):
    frame_path = os.path.join("Graphic", "Player", "WalkingLeft", f"WalkLeft {i}.png")
    try:
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (player_size, player_size))
        walking_left_frames.append(frame)
    except:
        fallback = pygame.Surface((player_size, player_size))
        fallback.fill((0, 255, 0))
        walking_left_frames.append(fallback)

idle_frames = []
for i in range(36):
    frame_path = os.path.join("Graphic", "Player", "Idle", f"Idle {i}.png")
    try:
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (player_size, player_size))
        idle_frames.append(frame)
    except:
        fallback = pygame.Surface((player_size, player_size))
        fallback.fill((0, 200, 0))
        idle_frames.append(fallback)

current_frame = 0
animation_timer = 0
facing_right = True
moving = False

class Platform:
    def __init__(self, y_pos, side):
        self.side = side
        platform_width = int(WIDTH * 0.12)
        platform_height = int(HEIGHT * 0.02)
        
        if side == "left":
            x_pos = wall_thickness
        else:
            x_pos = right_wall_x - platform_width
        
        self.rect = pygame.Rect(x_pos, y_pos, platform_width, platform_height)
        self.color = (139, 69, 19)
        self.scored = False
        self.breaking = False
        self.break_timer = 0
        self.visible = True

    def draw(self, surface):
        if not self.visible:
            return
        screen_y = self.rect.y - camera_y
        if -50 < screen_y < HEIGHT + 50:
            color = self.color
            if self.breaking:
                color = (220, 60, 60)
            pygame.draw.rect(surface, color, (self.rect.x, screen_y, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, (100, 50, 0), (self.rect.x, screen_y, self.rect.width, self.rect.height), 3)

platforms = []
y_pos = HEIGHT - int(HEIGHT * 0.15)
platforms.append(Platform(y_pos, "left"))

for i in range(199):
    last_side = platforms[-1].side
    if last_side == "left":
        side = random.choice(["left", "right"])
    else:
        side = random.choice(["left", "right"])
    
    jump_range = random.randint(int(HEIGHT * 0.1), int(HEIGHT * 0.14))
    y_pos -= jump_range
    platforms.append(Platform(y_pos, side))

clock = pygame.time.Clock()
run = True
on_ground = True
jump_timer = 0
score = 0
font = pygame.font.Font(None, int(HEIGHT * 0.05))

def draw_tiled_wall(surface, wall_rect, tile_images):
    tiles_in_width = 2
    total_height = 100000
    for row in range(0, total_height // tile_height + 2):
        for col in range(tiles_in_width):
            tile_index = (row * 3 + col) % len(tile_images)
            tile_image = tile_images[tile_index]
            tile_x = wall_rect.x + col * tile_width
            tile_y = wall_rect.y + row * tile_height - camera_y
            if tile_y + tile_height > -100 and tile_y < HEIGHT + 100:
                surface.blit(tile_image, (tile_x, tile_y))

while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    keys = pygame.key.get_pressed()

    moving = False
    if keys[pygame.K_a]:
        x -= move_speed
        facing_right = False
        moving = True
    if keys[pygame.K_d]:
        x += move_speed
        facing_right = True
        moving = True

    x = max(wall_thickness, min(x, right_wall_x - player_size))

    if jump_timer > 0:
        jump_timer -= 1

    on_ground = False

    for platform in platforms:
        if not platform.visible:
            continue
        if (y_velocity >= 0 and
            y + player_size <= platform.rect.y + platform_height + 5 and
            y + player_size + y_velocity >= platform.rect.y and
            x + player_size > platform.rect.x and
            x < platform.rect.x + platform.rect.width):
            
            y = platform.rect.y - player_size
            y_velocity = 0
            on_ground = True
            
            if not platform.scored:
                platform.scored = True
                score += 1
            
            if not platform.breaking:
                platform.breaking = True
                platform.break_timer = pygame.time.get_ticks()
            break

    if not on_ground and y + player_size >= HEIGHT:
        y = HEIGHT - player_size
        y_velocity = 0
        on_ground = True

    if on_ground and jump_timer == 0:
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            y_velocity = jump_power
            on_ground = False
            jump_timer = 12

    y_velocity += gravity
    y += y_velocity

    animation_timer += 1
    if animation_timer >= 4:
        animation_timer = 0
        current_frame = (current_frame + 1) % 36

    camera_y = y - HEIGHT * 2 // 3

    danger_y -= danger_speed  # stała prędkość, bez przyspieszania

    if y + player_size > danger_y:
        y = HEIGHT - int(HEIGHT * 0.15)
        x = WIDTH // 2
        y_velocity = 0
        camera_y = 0
        score = 0
        danger_y = HEIGHT + int(HEIGHT * 0.3)
        for platform in platforms:
            platform.scored = False
            platform.visible = True
            platform.breaking = False

    # Rysowanie tła
    if background_image:
        bg_y = camera_y * 0.3
        window.blit(background_image, (0, -bg_y % HEIGHT))
        window.blit(background_image, (0, -bg_y % HEIGHT - HEIGHT))
    else:
        window.fill((52, 55, 235))
    
    draw_tiled_wall(window, left_wall, tiles)
    draw_tiled_wall(window, right_wall, tiles)

    danger_screen_y = danger_y - camera_y
    pygame.draw.rect(window, (255, 40, 40), (0, danger_screen_y, WIDTH, HEIGHT))

    for platform in platforms:
        platform.draw(window)

    player_screen_y = y - camera_y
    
    if not on_ground:
        window.blit(flying_frames[current_frame], (x, player_screen_y))
    elif moving:
        if facing_right:
            window.blit(walking_right_frames[current_frame], (x, player_screen_y))
        else:
            window.blit(walking_left_frames[current_frame], (x, player_screen_y))
    else:
        window.blit(idle_frames[current_frame], (x, player_screen_y))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_text, (20, 20))

    remaining = 200 - score
    if remaining < 0:
        remaining = 0
    remaining_text = font.render(f"Remaining: {remaining}", True, (255, 255, 255))
    window.blit(remaining_text, (20, 20 + int(HEIGHT * 0.06)))

    if score >= 200:
        win_text = font.render("YOU WIN! Press ESC", True, (255, 215, 0))
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(win_text, win_rect)

    for platform in platforms:
        if platform.breaking and platform.visible:
            if pygame.time.get_ticks() - platform.break_timer >= 1000:
                platform.visible = False

    pygame.display.update()

pygame.quit()
