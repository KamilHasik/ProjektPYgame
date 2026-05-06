import pygame
from random import randint

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

x = WIDTH // 2
y = HEIGHT - 100

y_velocity = 0
gravity = 0.6
jump_power = -18

player_size = 50

wall_thickness = 300

left_wall = pygame.Rect(0, 0, wall_thickness, HEIGHT)
right_wall = pygame.Rect(WIDTH - wall_thickness, 0, wall_thickness, HEIGHT)

platforms = []

def generate_platform():
    side = randint(0, 1)
    py = randint(100, HEIGHT - 200)

    if side == 0:
        px = 0
    else:
        px = WIDTH - wall_thickness

    return pygame.Rect(px, py, wall_thickness, 20)

for _ in range(6):
    platforms.append(generate_platform())

clock = pygame.time.Clock()
run = True

while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    speed = 6

    if keys[pygame.K_a]:
        x -= speed
    if keys[pygame.K_d]:
        x += speed

    if x < wall_thickness:
        x = wall_thickness
    if x > WIDTH - wall_thickness - player_size:
        x = WIDTH - wall_thickness - player_size

    old_y = y

    if keys[pygame.K_w]:
        y_velocity = jump_power

    y_velocity += gravity
    y += y_velocity

    player = pygame.Rect(x, y, player_size, player_size)

    on_ground = False

    if y > HEIGHT - player_size:
        y = HEIGHT - player_size
        y_velocity = 0
        on_ground = True

    for p in platforms:
        if player.colliderect(p) and y_velocity > 0:
            y = p.y - player_size
            y_velocity = 0
            on_ground = True

    window.fill((52, 55, 235))

    pygame.draw.rect(window, (200, 0, 0), left_wall)
    pygame.draw.rect(window, (200, 0, 0), right_wall)

    for p in platforms:
        pygame.draw.rect(window, (150, 75, 0), p)

    pygame.draw.rect(window, (20, 200, 20), player)

    pygame.display.update()

pygame.quit()
