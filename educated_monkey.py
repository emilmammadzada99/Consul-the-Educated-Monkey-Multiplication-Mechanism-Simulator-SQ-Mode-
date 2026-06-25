import pygame
import math
import sys

# Pygame Initialization
pygame.init()
pygame.font.init()

# Screen setup (extra width for SQ slot)
WIDTH, HEIGHT = 880, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Consul the Educated Monkey - SQ (Square) Mode")
clock = pygame.time.Clock()

# --- Color Palette ---
BG_COLOR = (245, 242, 230)
LINK_COLOR = (70, 75, 80)
JOINT_COLOR = (212, 175, 55)
TEXT_COLOR = (30, 40, 50)
PIN_A_COLOR = (46, 117, 182)
PIN_B_COLOR = (197, 90, 17)
GRID_COLOR = (210, 205, 190)
BG_NUM_COLOR = (160, 165, 170)

# --- Geometry Settings ---
GROUND_Y = 560
SLOT_START_X = 100
SLOT_SPACING = 55
L = 380.0
POINTER_OFFSET = 45

# Number line slots (13th slot is SQ)
SLOTS = {i: SLOT_START_X + (i - 1) * SLOT_SPACING for i in range(1, 14)}

# Initial values
val_A = 3
val_B = 10
pos_A_x = SLOTS[val_A]
pos_B_x = SLOTS[val_B]

dragging_A = False
dragging_B = False
PIN_RADIUS = 15

# Fonts
try:
    font_small = pygame.font.SysFont("Arial", 14, bold=True)
    font_nums = pygame.font.SysFont("Georgia", 20, bold=True)
    font_bg_nums = pygame.font.SysFont("Georgia", 15, bold=True)
    font_banner = pygame.font.SysFont("Georgia", 24, bold=True)
except:
    font_small = pygame.font.Font(None, 20)
    font_nums = pygame.font.Font(None, 28)
    font_bg_nums = pygame.font.Font(None, 22)
    font_banner = pygame.font.Font(None, 32)


def solve_kinematics(ax, bx, L):
    """Compute mechanism joint positions."""
    x_left = ax
    x_right = bx

    # Real toy geometry: point P lies on a semicircle defined by AB
    px = (x_left + x_right) / 2
    py = GROUND_Y - (x_right - x_left) / 2

    mx = (x_left + px) / 2
    my = (GROUND_Y + py) / 2

    d_ap = math.sqrt((px - x_left)**2 + (py - GROUND_Y)**2)
    if d_ap < 0.1:
        d_ap = 0.1

    h = math.sqrt(max(0.1, L**2 - (d_ap / 2)**2))

    ux = (py - GROUND_Y) / d_ap
    uy = -(px - x_left) / d_ap

    ex = mx + h * ux
    ey = my + h * uy

    dx = px
    dy = ey - math.sqrt(max(0.1, L**2 - (px - ex)**2))

    cx = 2 * px - ex
    cy = ey

    return (x_left, GROUND_Y), (x_right, GROUND_Y), (px, py), (ex, ey), (dx, dy), (cx, cy)


# --- MAIN LOOP ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dist_A = math.sqrt((mouse_pos[0] - pos_A_x)**2 + (mouse_pos[1] - GROUND_Y)**2)
                dist_B = math.sqrt((mouse_pos[0] - pos_B_x)**2 + (mouse_pos[1] - GROUND_Y)**2)

                if dist_A < PIN_RADIUS:
                    dragging_A = True
                elif dist_B < PIN_RADIUS:
                    dragging_B = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if dragging_A:
                    val_A = min([k for k in SLOTS.keys() if k < val_B],
                                key=lambda k: abs(SLOTS[k] - mouse_pos[0]))
                    pos_A_x = SLOTS[val_A]
                    dragging_A = False

                if dragging_B:
                    val_B = min([k for k in SLOTS.keys() if k > val_A],
                                key=lambda k: abs(SLOTS[k] - mouse_pos[0]))
                    pos_B_x = SLOTS[val_B]
                    dragging_B = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging_A:
                pos_A_x = max(SLOT_START_X, min(pos_B_x - SLOT_SPACING // 2, mouse_pos[0]))
            if dragging_B:
                pos_B_x = max(pos_A_x + SLOT_SPACING // 2, min(SLOTS[13], mouse_pos[0]))

    # Compute mechanism state
    A, B, P, E, D, C = solve_kinematics(pos_A_x, pos_B_x, L)

    # --- DRAWING ---
    screen.fill(BG_COLOR)

    # Background multiplication triangle
    for a_lbl in range(1, 12):
        for b_lbl in range(a_lbl + 1, 13):
            prod = a_lbl * b_lbl
            px_bg = (SLOTS[a_lbl] + SLOTS[b_lbl]) / 2
            py_bg = GROUND_Y - (SLOTS[b_lbl] - SLOTS[a_lbl]) / 2 - POINTER_OFFSET

            bg_lbl = font_bg_nums.render(str(prod), True, BG_NUM_COLOR)
            screen.blit(bg_lbl, (px_bg - bg_lbl.get_width() // 2,
                                 py_bg - bg_lbl.get_height() // 2))

    # Square numbers (A² cases with SQ slot)
    for a_lbl in range(1, 13):
        prod = a_lbl * a_lbl
        px_bg = (SLOTS[a_lbl] + SLOTS[13]) / 2
        py_bg = GROUND_Y - (SLOTS[13] - SLOTS[a_lbl]) / 2 - POINTER_OFFSET

        bg_lbl = font_bg_nums.render(str(prod), True, BG_NUM_COLOR)
        screen.blit(bg_lbl, (px_bg - bg_lbl.get_width() // 2,
                             py_bg - bg_lbl.get_height() // 2))

    # Number line
    pygame.draw.line(screen, TEXT_COLOR,
                     (SLOT_START_X - 40, GROUND_Y),
                     (SLOTS[13] + 40, GROUND_Y), 3)

    for i, slot_x in SLOTS.items():
        #pygame.draw.circle(screen, GRID_COLOR, (slot_y, GROUND_Y), 4)
        pygame.draw.circle(screen, GRID_COLOR, (slot_x, GROUND_Y), 4)
        if i == 13:
            lbl = font_nums.render("SQ", True, (180, 40, 40))
        else:
            lbl = font_nums.render(str(i), True, TEXT_COLOR)

        screen.blit(lbl, (slot_x - lbl.get_width() // 2, GROUND_Y + 15))

    # Mechanism links
    links = [(A, E), (E, D), (E, P), (B, C), (C, D), (C, P)]
    for start, end in links:
        pygame.draw.line(screen, LINK_COLOR, start, end, 6)

    # Guide lines
    pygame.draw.line(screen, (180, 180, 180), A, P, 2)
    pygame.draw.line(screen, (180, 180, 180), B, P, 2)

    # Joints
    for joint in [E, D, C]:
        pygame.draw.circle(screen, JOINT_COLOR,
                           (int(joint[0]), int(joint[1])), 7)
        pygame.draw.circle(screen, LINK_COLOR,
                           (int(joint[0]), int(joint[1])), 7, 2)

    # Output ring
    ring_y = int(P[1]) - POINTER_OFFSET
    pygame.draw.line(screen, LINK_COLOR,
                     (int(P[0]), int(P[1])),
                     (int(P[0]), ring_y), 4)

    pygame.draw.circle(screen, (220, 40, 40),
                       (int(P[0]), ring_y), 22, 3)

    # Pins (A & B)
    pygame.draw.circle(screen, PIN_A_COLOR,
                       (int(pos_A_x), GROUND_Y), PIN_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255),
                       (int(pos_A_x), GROUND_Y), PIN_RADIUS, 2)

    lbl_A = font_small.render("A", True, (255, 255, 255))
    screen.blit(lbl_A,
                (pos_A_x - lbl_A.get_width() // 2,
                 GROUND_Y - lbl_A.get_height() // 2))

    current_b_color = (220, 40, 40) if val_B == 13 else PIN_B_COLOR
    pygame.draw.circle(screen, current_b_color,
                       (int(pos_B_x), GROUND_Y), PIN_RADIUS)
    pygame.draw.circle(screen, (255, 255, 255),
                       (int(pos_B_x), GROUND_Y), PIN_RADIUS, 2)

    lbl_B = font_small.render("B", True, (255, 255, 255))
    screen.blit(lbl_B,
                (pos_B_x - lbl_B.get_width() // 2,
                 GROUND_Y - lbl_B.get_height() // 2))

    # Top info panel
    if val_B == 13:
        operation_string = f"{val_A}² = {val_A * val_A}"
    else:
        operation_string = f"{val_A} × {val_B} = {val_A * val_B}"

    text_surface = font_banner.render(operation_string, True, TEXT_COLOR)
    screen.blit(text_surface, (40, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
