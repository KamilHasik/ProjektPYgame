import pygame
import os
import random
import math

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))
fade_alpha = 255
fade_in = True
show_run_text = True
run_text_timer = 0

camera_y = 0

wall_thickness = WIDTH // 4
right_wall_x = WIDTH - wall_thickness

player_size = int(HEIGHT * 0.15)
platform_width = int(WIDTH * 0.15)
platform_height = int(HEIGHT * 0.025)

jump_power = -14
gravity = 0.45
move_speed = int(WIDTH * 0.01)

x = WIDTH // 2
y = HEIGHT - int(HEIGHT * 0.15)
y_velocity = 0

danger_y = HEIGHT + int(HEIGHT * 0.3)
danger_speed = 2

left_wall = pygame.Rect(0, 0, wall_thickness, 100000)
right_wall = pygame.Rect(right_wall_x, 0, wall_thickness, 100000)

tile_width = wall_thickness // 2
tile_height = tile_width

STATE_MENU = "menu"
STATE_PLAYING = "playing"
game_state = STATE_MENU

font_huge = pygame.font.Font(None, int(HEIGHT * 0.14))
font_big = pygame.font.Font(None, int(HEIGHT * 0.10))
font_small = pygame.font.Font(None, int(HEIGHT * 0.05))
font_tiny = pygame.font.Font(None, int(HEIGHT * 0.04))

class Button:
    def __init__(self, x, y, w, h, text, color, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(255, c + 40) for c in color)
        self.text_color = text_color
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        col = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=12)
        txt = font_small.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))

bw = int(WIDTH * 0.28)
bh = int(HEIGHT * 0.09)
bx = WIDTH // 2 - bw // 2
btn_play = Button(bx, int(HEIGHT * 0.55), bw, bh, "▶  GRAJ", (120, 220, 255), (20, 10, 50))
btn_quit = Button(bx, int(HEIGHT * 0.68), bw, bh, "✕  WYJŚCIE", (200, 80, 80), (255, 255, 255))

menu_bg_t = 0
menu_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
               random.uniform(0.5, 2.5), random.uniform(0, math.pi * 2)) for _ in range(180)]

def draw_menu(surface, mouse_pos):
    global menu_bg_t
    menu_bg_t += 1

    for y_pos in range(0, HEIGHT, 4):
        ratio = y_pos / HEIGHT
        r = int(10 + 20 * ratio)
        g = int(5 + 10 * ratio)
        b = int(30 + 40 * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y_pos), (WIDTH, y_pos))
        pygame.draw.line(surface, (r, g, b), (0, y_pos + 1), (WIDTH, y_pos + 1))
        pygame.draw.line(surface, (r, g, b), (0, y_pos + 2), (WIDTH, y_pos + 2))
        pygame.draw.line(surface, (r, g, b), (0, y_pos + 3), (WIDTH, y_pos + 3))

    for sx, sy, brightness, phase in menu_stars:
        twinkle = 0.5 + 0.5 * math.sin(menu_bg_t * 0.04 + phase)
        alpha = int(80 + 175 * twinkle * brightness / 2.5)
        size = max(1, int(brightness))
        col = (min(255, alpha), min(255, alpha), min(255, int(alpha * 1.2)))
        pygame.draw.circle(surface, col, (sx, sy), size)

    for i in range(3):
        t = menu_bg_t * 0.015 + i * 2.1
        cx = int(WIDTH // 2 + math.cos(t) * WIDTH * 0.3)
        cy = int(HEIGHT // 2 + math.sin(t * 0.7) * HEIGHT * 0.25)
        r_val = int(60 + 30 * math.sin(t))
        ring_surf = pygame.Surface((r_val * 2 + 4, r_val * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (120, 220, 255, 15), (r_val + 2, r_val + 2), r_val, 2)
        surface.blit(ring_surf, (cx - r_val - 2, cy - r_val - 2))

    title_text = "CASTLE CLIMBERS"
    t = menu_bg_t * 0.05
    total_width = 0
    char_widths = []
    for ch in title_text:
        if ch == " ":
            w = int(HEIGHT * 0.08)
        else:
            w = font_huge.size(ch)[0]
        char_widths.append(w)
        total_width += w
    
    start_x = WIDTH // 2 - total_width // 2
    current_x = start_x
    
    for i, ch in enumerate(title_text):
        if ch == " ":
            current_x += int(HEIGHT * 0.08)
            continue
        wave = int(8 * math.sin(t + i * 0.5))
        col_r = int(200 + 55 * math.sin(t + i * 0.7))
        col_g = int(180 + 75 * math.sin(t + i * 0.9 + 1))
        col_b = 255
        ltr = font_huge.render(ch, True, (col_r, col_g, col_b))
        ly = int(HEIGHT * 0.14) + wave
        shadow = font_huge.render(ch, True, (0, 0, 0))
        surface.blit(shadow, (current_x + 4, ly + 4))
        surface.blit(ltr, (current_x, ly))
        current_x += char_widths[i]

    sub = font_tiny.render("Wspinaj się. Przeżyj. Zdobądź szczyt.", True, (160, 180, 220))
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, int(HEIGHT * 0.34)))

    controls = [("A / D", "Ruch lewo / prawo"), ("W / SPACE", "Skok"), ("ESC", "Wyjście")]
    cx_col = WIDTH // 2
    for i, (key, desc) in enumerate(controls):
        y_c = int(HEIGHT * 0.75) + i * int(HEIGHT * 0.06)
        k_surf = font_tiny.render(key, True, (255, 215, 0))
        d_surf = font_tiny.render(f"— {desc}", True, (160, 180, 220))
        total_w = k_surf.get_width() + 12 + d_surf.get_width()
        x_start = cx_col - total_w // 2
        surface.blit(k_surf, (x_start, y_c))
        surface.blit(d_surf, (x_start + k_surf.get_width() + 12, y_c))

    btn_play.update(mouse_pos)
    btn_quit.update(mouse_pos)
    btn_play.draw(surface)
    btn_quit.draw(surface)

background_image = None
background_path = os.path.join("Graphic", "Player", "Background.jpg")
try:
    background_image = pygame.image.load(background_path)
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except:
    pass

tiles = []
tile_names = ["tile 1.jpg", "tile 2.jpg", "tile 3.jpg", "tile 4.jpg", "tile 5.jpg",
              "tile 6.jpg", "tile 7.jpg", "tile 8.jpg", "tile 9.jpg"]

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

class Monster:
    def __init__(self, x_pos, y_pos):
        self.size = int(player_size * 0.7)
        self.speed = move_speed * 0.35
        self.x = x_pos
        self.y = y_pos
        self.direction = 1
        self.color = (255, 50, 100)
        
    def update(self):
        self.x += self.speed * self.direction
        if self.x <= wall_thickness:
            self.x = wall_thickness
            self.direction = 1
        elif self.x >= right_wall_x - self.size:
            self.x = right_wall_x - self.size
            self.direction = -1
            
    def draw(self, surface):
        screen_x = self.x
        screen_y = self.y - camera_y
        if -50 < screen_y < HEIGHT + 50:
            pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.size, self.size))
            pygame.draw.rect(surface, (200, 0, 100), (screen_x, screen_y, self.size, self.size), 3)
            pygame.draw.circle(surface, (255, 255, 255), (screen_x + self.size//3, screen_y + self.size//3), 3)
            pygame.draw.circle(surface, (255, 255, 255), (screen_x + 2*self.size//3, screen_y + self.size//3), 3)
    
    def get_rect(self):
        margin = 4
        return pygame.Rect(self.x + margin, self.y + margin, self.size - margin * 2, self.size - margin * 2)

monsters = []

class Platform:
    def __init__(self, y_pos, side, is_fake=False):
        self.side = side
        self.is_fake = is_fake
        self.platform_width = int(WIDTH * 0.15)
        self.platform_height = int(HEIGHT * 0.025)
        
        if side == "left":
            x_pos = wall_thickness + 20
        elif side == "center":
            x_pos = WIDTH // 2 - self.platform_width // 2
        else:
            x_pos = right_wall_x - self.platform_width - 20
        
        self.rect = pygame.Rect(x_pos, y_pos, self.platform_width, self.platform_height)
        self.color = (139, 69, 19) if not is_fake else (180, 60, 60)
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
            if self.is_fake:
                pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, screen_y, self.rect.width, self.rect.height), 3)
                pygame.draw.line(surface, (255, 0, 0), (self.rect.x, screen_y + self.rect.height//2), (self.rect.x + self.rect.width, screen_y + self.rect.height//2), 3)
            else:
                pygame.draw.rect(surface, (100, 50, 0), (self.rect.x, screen_y, self.rect.width, self.rect.height), 3)

def generate_platforms():
    platforms_list = []
    y_pos = HEIGHT - int(HEIGHT * 0.15)
    platforms_list.append(Platform(y_pos, "center", False))
    
    for i in range(199):
        last_side = platforms_list[-1].side
        options = ["left", "center", "right"]
        if last_side in options:
            options.remove(last_side)
        side = random.choice(options)
        jump_range = random.randint(int(HEIGHT * 0.18), int(HEIGHT * 0.22))
        y_pos -= jump_range
        
        is_fake = (random.randint(1, 5) == 1)
        platforms_list.append(Platform(y_pos, side, is_fake))
        
        if random.randint(1, 3) == 1 and i < 198:
            remaining = [opt for opt in options if opt != side]
            if remaining:
                second_side = random.choice(remaining)
                is_fake2 = (random.randint(1, 3) == 1)
                platforms_list.append(Platform(y_pos, second_side, is_fake2))
    
    platforms_list.sort(key=lambda p: p.rect.y, reverse=True)
    
    i = 0
    while i < len(platforms_list):
        current_y = platforms_list[i].rect.y
        same_level = []
        j = i
        while j < len(platforms_list) and platforms_list[j].rect.y == current_y:
            same_level.append(platforms_list[j])
            j += 1
        
        real_count = sum(1 for p in same_level if not p.is_fake)
        if real_count == 0:
            same_level[0].is_fake = False
            same_level[0].color = (139, 69, 19)
        elif real_count > 1:
            for p in same_level:
                if not p.is_fake and p != same_level[0]:
                    p.is_fake = True
                    p.color = (180, 60, 60)
        
        i = j
    
    return platforms_list

platforms = generate_platforms()

valid_platforms = [p for p in platforms[5:90] if p.visible and not p.is_fake and p != platforms[0]]
if valid_platforms:
    monster_count = random.randint(2, 5)
    selected = random.sample(valid_platforms, min(monster_count, len(valid_platforms)))
    for platform in selected:
        monster_x = platform.rect.x + (platform.platform_width // 2) - int(player_size * 0.35)
        monster_y = platform.rect.y - int(player_size * 0.7)
        monsters.append(Monster(monster_x, monster_y))

clock = pygame.time.Clock()
run = True
on_ground = True
jump_timer = 0
score = 0
font = pygame.font.Font(None, int(HEIGHT * 0.1))
small_font = pygame.font.Font(None, int(HEIGHT * 0.05))

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

def reset_game():
    global x, y, y_velocity, camera_y, score, danger_y, danger_speed, on_ground, jump_timer, fade_alpha, fade_in, show_run_text, run_text_timer, platforms, monsters, current_frame, animation_timer
    x = WIDTH // 2
    y = HEIGHT - int(HEIGHT * 0.15)
    y_velocity = 0
    camera_y = 0
    score = 0
    danger_y = HEIGHT + int(HEIGHT * 0.3)
    danger_speed = 2
    on_ground = True
    jump_timer = 0
    fade_alpha = 255
    fade_in = True
    show_run_text = True
    run_text_timer = 0
    current_frame = 0
    animation_timer = 0
    
    platforms = generate_platforms()
    monsters.clear()
    valid_platforms = [p for p in platforms[5:90] if p.visible and not p.is_fake and p != platforms[0]]
    if valid_platforms:
        monster_count = random.randint(2, 5)
        selected = random.sample(valid_platforms, min(monster_count, len(valid_platforms)))
        for platform in selected:
            monster_x = platform.rect.x + (platform.platform_width // 2) - int(player_size * 0.35)
            monster_y = platform.rect.y - int(player_size * 0.7)
            monsters.append(Monster(monster_x, monster_y))

while run:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == STATE_MENU:
                    run = False
                else:
                    game_state = STATE_MENU

        if game_state == STATE_MENU:
            if btn_play.is_clicked(event):
                reset_game()
                game_state = STATE_PLAYING
            if btn_quit.is_clicked(event):
                run = False

    if game_state == STATE_MENU:
        draw_menu(window, mouse_pos)

    elif game_state == STATE_PLAYING:
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
            
            player_hitbox = pygame.Rect(x + 10, y + 15, player_size - 20, player_size - 25)
            
            if (y_velocity >= 0 and
                player_hitbox.bottom <= platform.rect.y + 8 and
                player_hitbox.bottom + y_velocity >= platform.rect.y and
                player_hitbox.right > platform.rect.x + 5 and
                player_hitbox.left < platform.rect.right - 5):
                
                if platform.is_fake:
                    reset_game()
                    break
                else:
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

        player_hitbox = pygame.Rect(x + 10, y + 15, player_size - 20, player_size - 25)
        for monster in monsters[:]:
            monster.update()
            if monster.get_rect().colliderect(player_hitbox):
                reset_game()
                break

        animation_timer += 1
        if animation_timer >= 4:
            animation_timer = 0
            current_frame = (current_frame + 1) % 36

        camera_y = y - HEIGHT * 2 // 3
        danger_y -= danger_speed

        if y + player_size > danger_y:
            reset_game()

        for platform in platforms:
            if platform.breaking and platform.visible:
                if pygame.time.get_ticks() - platform.break_timer >= 1000:
                    platform.visible = False

        if background_image:
            window.blit(background_image, (0, 0))
        else:
            window.fill((52, 55, 235))
        
        draw_tiled_wall(window, left_wall, tiles)
        draw_tiled_wall(window, right_wall, tiles)

        danger_screen_y = danger_y - camera_y
        pygame.draw.rect(window, (255, 40, 40), (0, danger_screen_y, WIDTH, HEIGHT))

        for platform in platforms:
            platform.draw(window)

        for monster in monsters:
            monster.draw(window)

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

        score_text = small_font.render(f"Score: {score}", True, (255, 255, 255))
        window.blit(score_text, (20, 20))

        remaining = 200 - score
        if remaining < 0:
            remaining = 0
        remaining_text = small_font.render(f"Remaining: {remaining}", True, (255, 255, 255))
        window.blit(remaining_text, (20, 20 + int(HEIGHT * 0.06)))

        if score >= 200:
            win_text = font.render("YOU WIN! Press ESC", True, (255, 215, 0))
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(win_text, win_rect)

        if fade_in:
            fade_surface.set_alpha(fade_alpha)
            window.blit(fade_surface, (0, 0))
            fade_alpha -= 5
            if fade_alpha <= 0:
                fade_in = False
        
        if show_run_text and not fade_in:
            run_text = font.render("RUN!", True, (255, 255, 255))
            run_rect = run_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            window.blit(run_text, run_rect)
            run_text_timer += 1
            if run_text_timer > 30:
                show_run_text = False

    pygame.display.update()

pygame.quit()
