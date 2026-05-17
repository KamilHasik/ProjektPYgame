import pygame
import os
import random
import math

pygame.init()

window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = window.get_size()

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))

camera_y = 0

wall_thickness      = WIDTH // 4
right_wall_x        = WIDTH - wall_thickness
platform_width_val  = int(WIDTH * 0.15)
platform_height_val = int(HEIGHT * 0.025)
player_size         = int(HEIGHT * 0.15)
jump_power          = -14
gravity             = 0.45
move_speed          = int(WIDTH * 0.01)
tile_width          = wall_thickness // 2
tile_height         = tile_width

STATE_MENU    = "menu"
STATE_PLAYING = "playing"
game_state    = STATE_MENU

font_huge  = pygame.font.Font(None, int(HEIGHT * 0.14))
font_big   = pygame.font.Font(None, int(HEIGHT * 0.10))
font_small = pygame.font.Font(None, int(HEIGHT * 0.05))
font_tiny  = pygame.font.Font(None, int(HEIGHT * 0.04))
font_score = pygame.font.Font(None, int(HEIGHT * 0.05))


class Button:
    def __init__(self, x, y, w, h, text, base_color, text_color, border_color):
        self.rect         = pygame.Rect(x, y, w, h)
        self.text         = text
        self.color        = base_color
        self.hover_color  = tuple(min(255, c + 50) for c in base_color)
        self.text_color   = text_color
        self.border_color = border_color
        self.hovered      = False

    def update(self, mp):
        self.hovered = self.rect.collidepoint(mp)

    def draw(self, surface):
        col = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, 3, border_radius=8)
        txt = font_small.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2,
                           self.rect.centery - txt.get_height()//2))

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and self.rect.collidepoint(event.pos))


bw = int(WIDTH * 0.28)
bh = int(HEIGHT * 0.09)
bx = WIDTH // 2 - bw // 2
btn_play = Button(bx, int(HEIGHT * 0.55), bw, bh, "GRAJ",
                  (80, 50, 20), (255, 210, 80), (200, 160, 60))
btn_quit = Button(bx, int(HEIGHT * 0.68), bw, bh, "WYJSCIE",
                  (80, 20, 20), (255, 120, 80), (180, 60, 40))

menu_bg_t  = 0
menu_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
               random.uniform(0.5, 2.5), random.uniform(0, math.pi*2)) for _ in range(120)]


def draw_stone_banner(surface, cx, y_top, w, h):
    rect = pygame.Rect(cx - w//2, y_top, w, h)
    pygame.draw.rect(surface, (55, 45, 35), rect, border_radius=6)
    pygame.draw.rect(surface, (100, 80, 50), rect, 3, border_radius=6)
    for ry in range(y_top, y_top + h, 18):
        pygame.draw.line(surface, (40, 32, 24), (cx - w//2, ry), (cx + w//2, ry), 1)
    for rx in range(cx - w//2, cx + w//2, 30):
        pygame.draw.line(surface, (40, 32, 24), (rx, y_top), (rx, y_top + h), 1)


def draw_dragon_silhouette(surface, t):
    cx  = int(WIDTH * 0.82 + math.sin(t * 0.02) * 10)
    cy  = int(HEIGHT * 0.28 + math.cos(t * 0.015) * 8)
    col = (180, 40, 20)
    pygame.draw.ellipse(surface, col, (cx - 40, cy - 20, 80, 40))
    pygame.draw.line(surface, col, (cx - 10, cy - 18), (cx - 30, cy - 50), 14)
    pygame.draw.circle(surface, col, (cx - 35, cy - 55), 18)
    pygame.draw.circle(surface, (255, 220, 0), (cx - 28, cy - 58), 4)
    pygame.draw.circle(surface, (0, 0, 0), (cx - 27, cy - 58), 2)
    pygame.draw.line(surface, (140, 20, 0), (cx - 40, cy - 68), (cx - 50, cy - 85), 4)
    pygame.draw.line(surface, (140, 20, 0), (cx - 30, cy - 70), (cx - 34, cy - 88), 3)
    wf = int(12 * math.sin(t * 0.08))
    pygame.draw.polygon(surface, (150, 30, 15), [(cx, cy-10), (cx+50, cy-40-wf), (cx+20, cy)])
    pygame.draw.polygon(surface, (150, 30, 15), [(cx-5, cy-10), (cx-55, cy-35-wf), (cx-20, cy+5)])
    for i in range(5):
        pygame.draw.circle(surface, col,
                           (cx+40+i*14, int(cy+10+math.sin(t*0.05+i)*6)), max(1, 8-i))
    for fi in range(6):
        fx = cx - 55 + int(math.cos(t*0.1+fi*0.5)*8) - fi*12
        fy = cy - 55 + int(math.sin(t*0.07+fi)*5)
        pygame.draw.circle(surface, (255, max(0, 180-fi*30), 0), (fx, fy), max(2, 7-fi))


def draw_menu(surface, mouse_pos):
    global menu_bg_t
    menu_bg_t += 1
    t = menu_bg_t

    for ry in range(0, HEIGHT, 3):
        ratio = ry / HEIGHT
        pygame.draw.rect(surface, (int(28+18*ratio), int(22+12*ratio), int(15+10*ratio)),
                         (0, ry, WIDTH, 3))

    for gy in range(0, HEIGHT, 40):
        offset = (gy // 40 % 2) * 30
        for gx in range(-offset, WIDTH, 60):
            pygame.draw.rect(surface, (0, 0, 0), (gx, gy, 60, 40), 1)

    for tx, ty in [(int(WIDTH*0.1), int(HEIGHT*0.35)), (int(WIDTH*0.9), int(HEIGHT*0.35))]:
        flicker = int(4 * math.sin(t * 0.18))
        pygame.draw.rect(surface, (100, 70, 30), (tx-4, ty, 8, 22))
        for layer, (fc, r) in enumerate([((255,60,0), 10+flicker),
                                          ((255,160,0), 7+flicker//2),
                                          ((255,240,80), 4)]):
            pygame.draw.circle(surface, fc, (tx, ty - layer*5), r)

    draw_dragon_silhouette(surface, t)

    for sx, sy, brightness, phase in menu_stars:
        a = int(60 + 120 * (0.5 + 0.5*math.sin(t*0.05+phase)) * brightness / 2.5)
        pygame.draw.circle(surface, (min(255, a+40), min(255, a), 0), (sx, sy), 1)

    draw_stone_banner(surface, WIDTH//2, int(HEIGHT*0.08), int(WIDTH*0.72), int(HEIGHT*0.22))

    title   = "CASTLE CLIMBERS"
    total_w = sum((font_huge.size(ch)[0] if ch != " " else int(HEIGHT*0.07)) for ch in title)
    cx_t    = WIDTH//2 - total_w//2
    for i, ch in enumerate(title):
        if ch == " ":
            cx_t += int(HEIGHT * 0.07)
            continue
        wave = int(7 * math.sin(t*0.05 + i*0.45))
        ltr  = font_huge.render(ch, True, (int(220+35*math.sin(t*0.03+i*0.6)),
                                            int(160+55*math.sin(t*0.04+i*0.8+1)), 40))
        shd  = font_huge.render(ch, True, (20, 10, 0))
        ly   = int(HEIGHT * 0.10) + wave
        surface.blit(shd, (cx_t+4, ly+5))
        surface.blit(ltr, (cx_t, ly))
        cx_t += font_huge.size(ch)[0]

    sub = font_tiny.render("Wspinaj sie. Przezwyj. Zdobadz szczyt.", True, (200, 160, 80))
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, int(HEIGHT*0.295)))

    draw_stone_banner(surface, WIDTH//2, int(HEIGHT*0.72), int(WIDTH*0.5), int(HEIGHT*0.23))
    for i, (key, desc) in enumerate([("A / D", "Ruch lewo / prawo"),
                                      ("W / SPACJA", "Skok"),
                                      ("ESC", "Menu / Wyjscie")]):
        yc  = int(HEIGHT*0.745) + i*int(HEIGHT*0.062)
        k_s = font_tiny.render(key, True, (255, 210, 60))
        d_s = font_tiny.render("-- " + desc, True, (190, 165, 120))
        xs  = WIDTH//2 - (k_s.get_width()+14+d_s.get_width())//2
        surface.blit(k_s, (xs, yc))
        surface.blit(d_s, (xs + k_s.get_width() + 14, yc))

    btn_play.update(mouse_pos)
    btn_quit.update(mouse_pos)
    btn_play.draw(surface)
    btn_quit.draw(surface)


background_image = None
try:
    background_image = pygame.image.load(os.path.join("Graphic", "Player", "Background.jpg"))
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except Exception:
    pass

tiles = []
for tn in ["tile 1.jpg","tile 2.jpg","tile 3.jpg","tile 4.jpg","tile 5.jpg",
           "tile 6.jpg","tile 7.jpg","tile 8.jpg","tile 9.jpg"]:
    try:
        img = pygame.image.load(os.path.join("Graphic", "Tiles", tn))
        tiles.append(pygame.transform.scale(img, (tile_width, tile_height)))
    except Exception:
        fb = pygame.Surface((tile_width, tile_height))
        fb.fill((120, 100, 70))
        tiles.append(fb)


def load_frames(folder, prefix, count, size):
    frames = []
    for i in range(count):
        try:
            f = pygame.image.load(os.path.join("Graphic","Player",folder,prefix+" "+str(i)+".png"))
            frames.append(pygame.transform.scale(f, (size, size)))
        except Exception:
            fb = pygame.Surface((size, size))
            fb.fill((200, 200, 0))
            frames.append(fb)
    return frames


flying_frames        = load_frames("Flying",       "Flying",    36, player_size)
walking_right_frames = load_frames("WalkingRight", "WalkRight", 36, player_size)
walking_left_frames  = load_frames("WalkingLeft",  "WalkLeft",  36, player_size)
idle_frames          = load_frames("Idle",          "Idle",      36, player_size)

OPAT_QUOTES = [
    "Nie przychodzisz na lekcje\ndo opata tylko do Tobiasza...",
    "Wy nie jestescie wychowania ulicznego\ni nie wiecie jak zachowuja sie\nhardkorowi ludzie.",
    "Posluchaj moich piosenek, bracie.\nOpat ma flow, ktorego nie pojmiesz.",
    "Hardkor to stan umyslu.\nMoj umysl jest z granitu zamkowego.",
]

CAVE_W = int(player_size * 2.2)
CAVE_H = int(player_size * 2.5)


class Opat:
    def __init__(self, wall_side, y_world):
        self.wall_side     = wall_side
        self.y_world       = y_world
        self.size          = int(player_size * 0.85)
        self.talking       = False
        self.talk_timer    = 0
        self.q_index       = 0
        self.current_q     = ""
        self.player_inside = False
        self.active        = True

        if wall_side == "left":
            self.cave_x  = wall_thickness - CAVE_W
            self.opat_x  = self.cave_x + CAVE_W//2 - self.size//2
        else:
            self.cave_x  = right_wall_x
            self.opat_x  = self.cave_x + CAVE_W//2 - self.size//2

        self.opat_y  = y_world - self.size
        self.cave_rect_world = pygame.Rect(
            self.cave_x, y_world - CAVE_H, CAVE_W, CAVE_H
        )

    def check_player(self, px, py):
        if not self.active:
            return False
        pr         = pygame.Rect(px+10, py+10, player_size-20, player_size-20)
        inside_now = self.cave_rect_world.colliderect(pr)
        if inside_now and not self.player_inside and not self.talking:
            self.talking   = True
            self.talk_timer = 0
            self.current_q  = OPAT_QUOTES[self.q_index % len(OPAT_QUOTES)]
        self.player_inside = inside_now
        return inside_now

    def update(self):
        if self.talking:
            self.talk_timer += 1
            if self.talk_timer > 300:
                self.talking    = False
                self.talk_timer = 0
                self.q_index    = (self.q_index + 1) % len(OPAT_QUOTES)
                self.active     = False

    def draw(self, surface):
        if not self.active:
            return
        cave_sy = int(self.y_world - CAVE_H - camera_y)
        opat_sy = int(self.opat_y - camera_y)

        if not (-CAVE_H - 50 < cave_sy < HEIGHT + 50):
            return

        if self.wall_side == "left":
            arch_x = wall_thickness - CAVE_W
        else:
            arch_x = right_wall_x

        pygame.draw.rect(surface, (38, 28, 18),
                         (arch_x, cave_sy, CAVE_W, CAVE_H))

        arch_cx = arch_x + CAVE_W // 2
        arch_cy = cave_sy
        pygame.draw.ellipse(surface, (38, 28, 18),
                            (arch_cx - CAVE_W//2, arch_cy - CAVE_W//3,
                             CAVE_W, CAVE_W//3 * 2))

        for stone_y in range(cave_sy, cave_sy + CAVE_H, 18):
            pygame.draw.line(surface, (55, 42, 28),
                             (arch_x, stone_y), (arch_x + CAVE_W, stone_y), 1)
        for stone_x in range(arch_x, arch_x + CAVE_W, 22):
            pygame.draw.line(surface, (55, 42, 28),
                             (stone_x, cave_sy), (stone_x, cave_sy + CAVE_H), 1)

        if self.wall_side == "left":
            pygame.draw.line(surface, (80, 60, 30),
                             (arch_x + CAVE_W, cave_sy),
                             (arch_x + CAVE_W, cave_sy + CAVE_H), 3)
        else:
            pygame.draw.line(surface, (80, 60, 30),
                             (arch_x, cave_sy),
                             (arch_x, cave_sy + CAVE_H), 3)

        for ci in range(2):
            torch_x = arch_x + (CAVE_W//4 if ci == 0 else 3*CAVE_W//4)
            torch_y = cave_sy + CAVE_H//5
            pygame.draw.rect(surface, (80, 55, 20), (torch_x-2, torch_y, 4, 10))
            flick = int(3 * math.sin(pygame.time.get_ticks()*0.005 + ci*2))
            pygame.draw.circle(surface, (255, 100, 0), (torch_x, torch_y - 2 - flick), 5+flick)
            pygame.draw.circle(surface, (255, 210, 60), (torch_x, torch_y - 2 - flick), 3)

        pygame.draw.rect(surface, (60, 45, 30),
                         (self.opat_x + self.size//4, int(opat_sy + self.size*0.35),
                          self.size//2, int(self.size*0.65)), border_radius=4)
        pygame.draw.circle(surface, (215, 175, 135),
                           (self.opat_x + self.size//2, int(opat_sy + self.size*0.28)),
                           self.size//6)
        pygame.draw.circle(surface, (185, 145, 110),
                           (self.opat_x + self.size//2, int(opat_sy + self.size*0.22)),
                           self.size//9)
        ccx = self.opat_x + self.size//2
        ccy = int(opat_sy + self.size*0.55)
        pygame.draw.line(surface, (200, 170, 80), (ccx, ccy-14), (ccx, ccy+14), 3)
        pygame.draw.line(surface, (200, 170, 80), (ccx-8, ccy-4), (ccx+8, ccy-4), 3)

        lbl = font_tiny.render("OPAT", True, (255, 210, 60))
        surface.blit(lbl, (self.opat_x + self.size//2 - lbl.get_width()//2, opat_sy - 28))

        if self.talking:
            self._draw_bubble(surface, opat_sy)

    def _draw_bubble(self, surface, sy):
        lines  = self.current_q.split('\n')
        line_h = int(HEIGHT * 0.038)
        pad    = 14
        max_w  = max(font_tiny.size(l)[0] for l in lines)
        bw2    = max_w + pad * 2
        bh2    = len(lines) * line_h + pad * 2

        if self.wall_side == "left":
            bx2 = wall_thickness + 10
        else:
            bx2 = right_wall_x - bw2 - 10

        by2 = int(sy - bh2 - 10)
        pygame.draw.rect(surface, (240, 230, 190), (bx2, by2, bw2, bh2), border_radius=10)
        pygame.draw.rect(surface, (150, 110, 50), (bx2, by2, bw2, bh2), 2, border_radius=10)
        tip = self.opat_x + self.size//2
        pygame.draw.polygon(surface, (240, 230, 190),
                            [(tip-8, by2+bh2), (tip+8, by2+bh2), (tip, by2+bh2+14)])
        for li, line in enumerate(lines):
            ts = font_tiny.render(line, True, (60, 40, 10))
            surface.blit(ts, (bx2+pad, by2+pad+li*line_h))


class Monster:
    def __init__(self, x_pos, y_pos):
        self.size  = int(player_size * 0.7)
        self.speed = move_speed * 0.4
        self.x     = float(x_pos)
        self.y     = y_pos
        self.dir   = random.choice([-1, 1])
        self.anim  = 0

    def update(self):
        self.x    += self.speed * self.dir
        self.anim += 1
        if self.x <= wall_thickness:
            self.x   = float(wall_thickness)
            self.dir = 1
        elif self.x >= right_wall_x - self.size:
            self.x   = float(right_wall_x - self.size)
            self.dir = -1

    def draw(self, surface):
        sy = self.y - camera_y
        if not (-50 < sy < HEIGHT + 50):
            return
        ix   = int(self.x)
        bob  = int(3 * math.sin(self.anim * 0.15))
        body = pygame.Rect(ix, sy+bob, self.size, self.size)
        pygame.draw.rect(surface, (160, 30, 60), body, border_radius=6)
        pygame.draw.rect(surface, (220, 50, 80), body, 2, border_radius=6)
        eye_y = int(sy + bob + self.size*0.28)
        for ex in [ix+self.size//3, ix+2*self.size//3]:
            pygame.draw.circle(surface, (255, 240, 0), (ex, eye_y), 5)
            pygame.draw.circle(surface, (0, 0, 0), (ex, eye_y), 2)
        hx = ix + self.size//2
        hy = int(sy + bob)
        pygame.draw.polygon(surface, (120,10,30), [(hx-12,hy),(hx-6,hy-16),(hx,hy)])
        pygame.draw.polygon(surface, (120,10,30), [(hx,hy),(hx+6,hy-16),(hx+12,hy)])
        for ti in range(3):
            tx2 = ix + self.size//4 + ti*(self.size//4)
            pygame.draw.polygon(surface, (255,255,255), [
                (tx2, int(sy+bob+self.size*0.7)),
                (tx2+4, int(sy+bob+self.size*0.7)),
                (tx2+2, int(sy+bob+self.size*0.82))
            ])

    def get_rect(self):
        m = 5
        return pygame.Rect(int(self.x)+m, self.y+m, self.size-m*2, self.size-m*2)


class Platform:
    def __init__(self, y_pos, side, is_fake=False):
        self.side            = side
        self.is_fake         = is_fake
        self.platform_width  = platform_width_val
        self.platform_height = platform_height_val
        if side == "left":
            xp = wall_thickness + 20
        elif side == "center":
            xp = WIDTH//2 - self.platform_width//2
        else:
            xp = right_wall_x - self.platform_width - 20
        self.rect        = pygame.Rect(xp, y_pos, self.platform_width, self.platform_height)
        self.color       = (110, 70, 30) if not is_fake else (160, 40, 40)
        self.scored      = False
        self.breaking    = False
        self.break_timer = 0
        self.visible     = True

    def draw(self, surface):
        if not self.visible:
            return
        sy = self.rect.y - camera_y
        if not (-50 < sy < HEIGHT + 50):
            return
        col = (200, 50, 50) if self.breaking else self.color
        pygame.draw.rect(surface, col, (self.rect.x, sy, self.rect.width, self.rect.height))
        if self.is_fake:
            pygame.draw.rect(surface, (220, 20, 20),
                             (self.rect.x, sy, self.rect.width, self.rect.height), 3)
            pygame.draw.line(surface, (255, 0, 0),
                             (self.rect.x, sy), (self.rect.x+self.rect.width, sy+self.rect.height), 2)
            pygame.draw.line(surface, (255, 0, 0),
                             (self.rect.x+self.rect.width, sy), (self.rect.x, sy+self.rect.height), 2)
        else:
            pygame.draw.rect(surface, (70, 40, 10),
                             (self.rect.x, sy, self.rect.width, self.rect.height), 2)
            for gi in range(1, 3):
                gy2 = sy + gi*(self.rect.height//3)
                pygame.draw.line(surface, (90,55,15),
                                 (self.rect.x+4, gy2), (self.rect.x+self.rect.width-4, gy2), 1)


def generate_platforms():
    plist = []
    yp    = HEIGHT - int(HEIGHT * 0.15)
    plist.append(Platform(yp, "center", False))

    sides   = ["left", "center", "right"]
    last    = "center"

    for i in range(199):
        jump_range = random.randint(int(HEIGHT*0.17), int(HEIGHT*0.22))
        yp        -= jump_range

        available = [s for s in sides if s != last]
        real_side = random.choice(available)
        last      = real_side
        plist.append(Platform(yp, real_side, False))

        if random.randint(1, 4) == 1:
            fake_options = [s for s in sides if s != real_side]
            fake_side    = random.choice(fake_options)
            plist.append(Platform(yp, fake_side, True))

    return plist


def draw_tiled_wall(surface, wall_rect):
    tiles_in_w = max(1, wall_rect.width // tile_width)
    rows_start = int((camera_y - tile_height) // tile_height)
    rows_end   = int((camera_y + HEIGHT + tile_height*2) // tile_height)
    for row in range(rows_start, rows_end + 1):
        for col in range(tiles_in_w):
            tidx = abs(row*3 + col) % len(tiles)
            surface.blit(tiles[tidx], (wall_rect.x + col*tile_width, row*tile_height - camera_y))


def spawn_monsters(plist):
    valid  = [p for p in plist[3:] if p.visible and not p.is_fake]
    if not valid:
        return []
    count  = random.randint(8, 12)
    chosen = random.sample(valid, min(count, len(valid)))
    ms     = []
    for pl in chosen:
        mx = pl.rect.x + pl.rect.width//2 - int(player_size*0.35)
        my = pl.rect.y - int(player_size*0.7)
        ms.append(Monster(mx, my))
    return ms


def try_spawn_opat(plist):
    real_sorted = [p for p in plist if not p.is_fake and p.visible]
    if len(real_sorted) < 10:
        return None
    chosen = random.choice(real_sorted[5:min(30, len(real_sorted))])
    wall_side = random.choice(["left", "right"])
    return Opat(wall_side, chosen.rect.y)


platforms         = []
monsters          = []
opat_npc          = None
x                 = WIDTH // 2
y                 = HEIGHT - int(HEIGHT * 0.15)
y_velocity        = 0.0
on_ground         = True
jump_timer        = 0
score             = 0
facing_right      = True
moving_anim       = False
current_frame     = 0
anim_timer        = 0
fade_alpha        = 255
fade_in           = True
show_run_text     = True
run_text_timer    = 0
danger_y          = HEIGHT + int(HEIGHT * 0.3)
danger_speed      = 2
danger_moving     = False
danger_cave_pause = False
left_wall_rect    = pygame.Rect(0, 0, wall_thickness, 100000)
right_wall_rect   = pygame.Rect(right_wall_x, 0, wall_thickness, 100000)


def reset_game():
    global x, y, y_velocity, camera_y, score, on_ground, jump_timer
    global fade_alpha, fade_in, show_run_text, run_text_timer
    global current_frame, anim_timer, facing_right, moving_anim
    global danger_y, danger_speed, danger_moving, danger_cave_pause
    global platforms, monsters, opat_npc

    x              = WIDTH // 2
    y              = HEIGHT - int(HEIGHT * 0.15)
    y_velocity     = 0.0
    camera_y       = 0
    score          = 0
    on_ground      = True
    jump_timer     = 0
    fade_alpha     = 255
    fade_in        = True
    show_run_text  = True
    run_text_timer = 0
    current_frame  = 0
    anim_timer     = 0
    facing_right   = True
    moving_anim    = False
    danger_y       = HEIGHT + int(HEIGHT * 0.3)
    danger_speed   = 2
    danger_moving  = False
    danger_cave_pause = False

    platforms = generate_platforms()
    monsters  = spawn_monsters(platforms)
    opat_npc  = try_spawn_opat(platforms)


reset_game()

clock    = pygame.time.Clock()
run_game = True

while run_game:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_game = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == STATE_MENU:
                    run_game = False
                else:
                    game_state = STATE_MENU
        if game_state == STATE_MENU:
            if btn_play.is_clicked(event):
                reset_game()
                game_state = STATE_PLAYING
            if btn_quit.is_clicked(event):
                run_game = False

    if game_state == STATE_MENU:
        draw_menu(window, mouse_pos)
        pygame.display.update()
        continue

    keys = pygame.key.get_pressed()
    moved_this_frame = False
    moving_anim      = False

    if keys[pygame.K_a]:
        x               -= move_speed
        facing_right     = False
        moving_anim      = True
        moved_this_frame = True
    if keys[pygame.K_d]:
        x               += move_speed
        facing_right     = True
        moving_anim      = True
        moved_this_frame = True

    x = max(wall_thickness, min(x, right_wall_x - player_size))

    if moved_this_frame and not danger_moving:
        danger_moving = True

    if jump_timer > 0:
        jump_timer -= 1

    on_ground = False

    for platform in platforms:
        if not platform.visible:
            continue
        ph = pygame.Rect(x+10, y+15, player_size-20, player_size-25)
        if (y_velocity >= 0
                and ph.bottom <= platform.rect.y + 8
                and ph.bottom + y_velocity >= platform.rect.y
                and ph.right  > platform.rect.x + 5
                and ph.left   < platform.rect.right - 5):
            if platform.is_fake:
                reset_game()
                break
            else:
                y          = platform.rect.y - player_size
                y_velocity = 0.0
                on_ground  = True
                if not platform.scored:
                    platform.scored = True
                    score += 1
                if not platform.breaking:
                    platform.breaking    = True
                    platform.break_timer = pygame.time.get_ticks()
                break

    if not on_ground and y + player_size >= HEIGHT:
        y          = HEIGHT - player_size
        y_velocity = 0.0
        on_ground  = True

    if on_ground and jump_timer == 0:
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            y_velocity = jump_power
            on_ground  = False
            jump_timer = 12

    y_velocity += gravity
    y          += y_velocity
    camera_y    = y - HEIGHT*2//3

    if opat_npc:
        opat_npc.update()
        danger_cave_pause = opat_npc.check_player(x, y)
    else:
        danger_cave_pause = False

    if danger_moving and not danger_cave_pause:
        danger_y -= danger_speed

    ph2    = pygame.Rect(x+10, y+15, player_size-20, player_size-25)
    killed = False
    for monster in monsters:
        monster.update()
        if not killed and monster.get_rect().colliderect(ph2):
            reset_game()
            killed = True
            break

    if killed:
        continue

    if y + player_size > danger_y:
        reset_game()
        continue

    now = pygame.time.get_ticks()
    for platform in platforms:
        if platform.breaking and platform.visible:
            if now - platform.break_timer >= 1000:
                platform.visible = False

    anim_timer += 1
    if anim_timer >= 4:
        anim_timer    = 0
        current_frame = (current_frame + 1) % 36

    if background_image:
        window.blit(background_image, (0, 0))
    else:
        for ry in range(0, HEIGHT, 4):
            ratio = ry / HEIGHT
            pygame.draw.rect(window, (int(30+15*ratio), int(25+10*ratio), int(55+20*ratio)),
                             (0, ry, WIDTH, 4))

    draw_tiled_wall(window, left_wall_rect)
    draw_tiled_wall(window, right_wall_rect)

    if opat_npc:
        opat_npc.draw(window)

    lava_sy = int(danger_y - camera_y)
    if lava_sy < HEIGHT:
        pygame.draw.rect(window, (255, 40, 20), (0, lava_sy, WIDTH, HEIGHT - lava_sy + 10))
        lava_t = now // 60
        for lx in range(0, WIDTH, 20):
            wh = int(6 + 4*math.sin(lx*0.1 + lava_t*0.08))
            pygame.draw.rect(window, (255, 120, 0), (lx, lava_sy-wh, 20, wh+2))

    for platform in platforms:
        platform.draw(window)

    for monster in monsters:
        monster.draw(window)

    psy = y - camera_y
    if not on_ground:
        window.blit(flying_frames[current_frame], (x, psy))
    elif moving_anim:
        if facing_right:
            window.blit(walking_right_frames[current_frame], (x, psy))
        else:
            window.blit(walking_left_frames[current_frame], (x, psy))
    else:
        window.blit(idle_frames[current_frame], (x, psy))

    sc_txt = font_score.render("Wynik: " + str(score), True, (255, 220, 100))
    rm_txt = font_score.render("Pozostalo: " + str(max(0, 200-score)), True, (200, 180, 120))
    window.blit(sc_txt, (20, 20))
    window.blit(rm_txt, (20, 20 + int(HEIGHT*0.06)))

    lava_dist = danger_y - (y + player_size)
    if lava_dist < HEIGHT*0.3 and danger_moving:
        warn_a = min(220, int(220*(1 - lava_dist/(HEIGHT*0.3))))
        warn   = font_small.render("LAWA!", True, (255, 80, 0))
        warn.set_alpha(warn_a)
        window.blit(warn, (WIDTH//2 - warn.get_width()//2, int(HEIGHT*0.85)))

    if danger_cave_pause:
        pt = font_tiny.render("Lawa czeka... (jaskinia Opata)", True, (255, 210, 60))
        window.blit(pt, (WIDTH//2 - pt.get_width()//2, int(HEIGHT*0.92)))

    if not danger_moving:
        nt = font_tiny.render("Rusz sie aby obudzic lawe!", True, (200, 200, 100))
        window.blit(nt, (WIDTH//2 - nt.get_width()//2, int(HEIGHT*0.88)))

    if score >= 200:
        win = font_big.render("WYGRANA! Nacisnij ESC", True, (255, 215, 0))
        shd = font_big.render("WYGRANA! Nacisnij ESC", True, (0, 0, 0))
        wx  = WIDTH//2 - win.get_width()//2
        wy  = HEIGHT//2 - win.get_height()//2
        window.blit(shd, (wx+4, wy+4))
        window.blit(win, (wx, wy))

    if fade_in:
        fade_surface.set_alpha(fade_alpha)
        window.blit(fade_surface, (0, 0))
        fade_alpha -= 5
        if fade_alpha <= 0:
            fade_in = False

    if show_run_text and not fade_in:
        rs  = font_big.render("BIEGNIJ!", True, (255, 255, 255))
        rsh = font_big.render("BIEGNIJ!", True, (0, 0, 0))
        rx  = WIDTH//2 - rs.get_width()//2
        ry2 = HEIGHT//2 - rs.get_height()//2
        window.blit(rsh, (rx+3, ry2+3))
        window.blit(rs,  (rx,   ry2))
        run_text_timer += 1
        if run_text_timer > 60:
            show_run_text = False

    pygame.display.update()

pygame.quit()
