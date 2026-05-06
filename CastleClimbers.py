import pygame
import os
import random

pygame.init()
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

camera_y = 0
x = WIDTH // 2
y = HEIGHT - 100
y_velocity = 0
gravity = 0.6
jump_power = -18
player_size = 50
wall_thickness = 400

left_wall = pygame.Rect(0, 0, wall_thickness, HEIGHT)
right_wall = pygame.Rect(WIDTH - wall_thickness, 0, wall_thickness, HEIGHT)

tile_width = wall_thickness // 2
tile_height = tile_width  

tiles = []
tile_names = ["tile 1.jpg", "tile 2.jpg", "tile 3.jpg", 
              "tile 4.jpg", "tile 5.jpg", "tile 6.jpg",
              "tile 7.jpg", "tile 8.jpg", "tile 9.jpg"]

for tile_name in tile_names:
    tile_path = os.path.join("tiles", tile_name)
    try:
        tile_image = pygame.image.load(tile_path)
        tile_image = pygame.transform.scale(tile_image, (tile_width, tile_height))
        tiles.append(tile_image)
    except:
        fallback = pygame.Surface((tile_width, tile_height))
        fallback.fill((150, 150, 150))
        tiles.append(fallback)

class Platform:
    def __init__(self, y_pos, side):
        self.side = side
        platform_width = random.randint(80, 150)
        platform_height = 20
        
        if side == 'left':
            x_pos = wall_thickness
        else:
            x_pos = WIDTH - wall_thickness - platform_width
        
        self.rect = pygame.Rect(x_pos, y_pos, platform_width, platform_height)
        self.color = (139, 69, 19)
    
    def draw(self, surface):
        screen_y = self.rect.y - camera_y
        if -50 < screen_y < HEIGHT + 50:
            pygame.draw.rect(surface, self.color, (self.rect.x, screen_y, self.rect.width, self.rect.height))
            pygame.draw.rect(surface, (100, 50, 0), (self.rect.x, screen_y, self.rect.width, self.rect.height), 2)

platforms = []
last_side = None
for i in range(30):
    if last_side == 'left':
        side = 'right'
    else:
        side = 'left'
    last_side = side
    y_pos = HEIGHT - 100 - i * 80
    platforms.append(Platform(y_pos, side))

clock = pygame.time.Clock()
run = True
on_ground = True

def draw_tiled_wall(surface, wall_rect, tile_images):
    tiles_in_width = 2
    tiles_in_height = (wall_rect.height + tile_height - 1) // tile_height
    
    for row in range(tiles_in_height):
        for col in range(tiles_in_width):
            tile_index = (col % 3) + (row % 3) * 3
            tile_image = tile_images[tile_index % len(tile_images)]
            tile_x = wall_rect.x + col * tile_width
            tile_y = wall_rect.y + row * tile_height - camera_y
            
            if 0 < tile_y + tile_height and tile_y < HEIGHT:
                if tile_y + tile_height > HEIGHT:
                    crop_height = HEIGHT - tile_y
                    if crop_height > 0:
                        surface.blit(tile_image.subsurface((0, 0, tile_width, crop_height)), (tile_x, tile_y))
                else:
                    surface.blit(tile_image, (tile_x, tile_y))

while run:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a]: x -= 6
    if keys[pygame.K_d]: x += 6
    
    x = max(wall_thickness, min(x, WIDTH - wall_thickness - player_size))
    
    on_ground = False
    
    for platform in platforms:
        if (y + player_size >= platform.rect.y and y + player_size <= platform.rect.y + 10 and
            x + player_size > platform.rect.x and x < platform.rect.x + platform.rect.width):
            y = platform.rect.y - player_size
            y_velocity = 0
            on_ground = True
            break
    
    if not on_ground and y + player_size >= HEIGHT:
        y = HEIGHT - player_size
        y_velocity = 0
        on_ground = True
    
    if (keys[pygame.K_w] or keys[pygame.K_UP]) and on_ground:
        y_velocity = jump_power
        on_ground = False
    
    y_velocity += gravity
    y += y_velocity
    
    camera_y = y - HEIGHT * 2 // 3
    if camera_y < 0: camera_y = 0
    
    window.fill((52, 55, 235))
    draw_tiled_wall(window, left_wall, tiles)
    draw_tiled_wall(window, right_wall, tiles)
    
    for platform in platforms:
        platform.draw(window)
    
    pygame.draw.rect(window, (20, 200, 20), (x, y - camera_y, player_size, player_size))
    pygame.display.update()

pygame.quit()
