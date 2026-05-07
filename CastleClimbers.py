import pygame
import os
import random

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

camera_y = 0

x = WIDTH // 2
y = HEIGHT - 250
y_velocity = 0

gravity = 0.5
jump_power = -16
player_size = 80

danger_y = HEIGHT + 500
danger_speed = 1.2

wall_thickness = 400

left_wall = pygame.Rect(0, 0, wall_thickness, 100000)
right_wall = pygame.Rect(WIDTH - wall_thickness, 0, wall_thickness, 100000)

tile_width = wall_thickness // 2
tile_height = tile_width

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
for i in range(10):
    frame_path = os.path.join("Graphic", "Player", "Flying", f"Flying {i}.png")
    try:
        frame = pygame.image.load(frame_path)
        frame = pygame.transform.scale(frame, (player_size, player_size))
        flying_frames.append(frame)
        print(f"Zaladowano: Flying {i}.png")
    except Exception as e:
        print(f"Nie zaladowano Flying {i}.png: {e}")
        fallback = pygame.Surface((player_size, player_size))
        fallback.fill((255, 255, 0))
        flying_frames.append(fallback)

current_frame = 0
animation_timer = 0

class Platform:
    def __init__(self, y_pos, side):
        self.side = side
        platform_width = 220
        platform_height = 25
        
        if side == "left":
            x_pos = wall_thickness
        else:
            x_pos = WIDTH - wall_thickness - platform_width
        
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
y_pos = HEIGHT - 250
platforms.append(Platform(y_pos, "left"))

for i in range(199):
    side = random.choice(["left", "right"])
    jump_range = random.randint(170, 230)
    y_pos -= jump_range
    platforms.append(Platform(y_pos, side))

clock = pygame.time.Clock()
run = True
on_ground = True
jump_timer = 0
score = 0
font = pygame.font.Font(None, 48)

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

    if keys[pygame.K_a]:
        x -= 9
    if keys[pygame.K_d]:
        x += 9

    x = max(wall_thickness, min(x, WIDTH - wall_thickness - player_size))

    if jump_timer > 0:
        jump_timer -= 1

    on_ground = False

    for platform in platforms:
        if not platform.visible:
            continue
        if (y_velocity >= 0 and
            y + player_size <= platform.rect.y + 20 and
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

    if not on_ground:
        animation_timer += 1
        if animation_timer >= 3:
            animation_timer = 0
            current_frame = (current_frame + 1) % len(flying_frames)
    else:
        current_frame = 0
        animation_timer = 0

    camera_y = y - HEIGHT * 2 // 3

    danger_y -= danger_speed
    danger_speed += 0.0005

    if y + player_size > danger_y:
        y = HEIGHT - 250
        x = WIDTH // 2
        y_velocity = 0
        camera_y = 0
        score = 0
        danger_y = HEIGHT + 500
        danger_speed = 4
        for platform in platforms:
            platform.scored = False
            platform.visible = True
            platform.breaking = False

    window.fill((52, 55, 235))
    draw_tiled_wall(window, left_wall, tiles)
    draw_tiled_wall(window, right_wall, tiles)

    danger_screen_y = danger_y - camera_y
    pygame.draw.rect(window, (255, 40, 40), (0, danger_screen_y, WIDTH, HEIGHT))

    for platform in platforms:
        platform.draw(window)

    player_screen_y = y - camera_y
    if not on_ground and flying_frames:
        window.blit(flying_frames[current_frame], (x, player_screen_y))
    else:
        pygame.draw.rect(window, (20, 200, 20), (x, player_screen_y, player_size, player_size))

    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_text, (20, 20))

    remaining = 200 - score
    if remaining < 0:
        remaining = 0
    remaining_text = font.render(f"Remaining: {remaining}", True, (255, 255, 255))
    window.blit(remaining_text, (20, 70))

    if score >= 200:
        win_text = font.render("YOU WIN! Press ESC", True, (255, 215, 0))
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(win_text, win_rect)

    for platform in platforms:
        if platform.breaking and platform.visible:
            if pygame.time.get_ticks() - platform.break_timer >= 200:
                platform.visible = False

    pygame.display.update()

pygame.quit()
