###############################################################################################
# Fadil Eldin
# Feb/9/2025
###############################################################################################
"""
GPT-4o
Write a Python program that shows a ball bouncing inside a spinning hexagon.
when the ball hits a hexagon wall, it gets kicked back at random angle at random force.
The ball should not go out of the hexagon and any time.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.
Make the hexagon reverse its spin direction at random times.
Display information about the hexagon's rotation direction, ball velocity, and bounce angle in the upper left corner of the screen.
"""
###############################################################################################
import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 750, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GPT-4o: Ball Bouncing Inside a Spinning Hexagon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (127, 127, 127)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Font setup
font = pygame.font.Font(None, 24)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Physics constants
GRAVITY = 0.2
FRICTION = 0.98
KICK_FORCE_MIN = 1
KICK_FORCE_MAX = 7

# Hexagon properties
HEX_RADIUS = 250
HEX_CENTER = (WIDTH // 2, HEIGHT // 2)
HEX_ANGLE_SPEED = math.radians(0.5)  # Speed of rotation in radians per frame

# Ball properties
BALL_RADIUS = 20
ball_pos = [WIDTH // 2, HEIGHT // 2 - HEX_RADIUS + BALL_RADIUS * 2]
ball_velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]

# Rotation direction
rotation_direction = 1  # 1 for clockwise, -1 for counterclockwise
last_direction_change = pygame.time.get_ticks()

def rotate_point(point, center, angle):
    px, py = point
    cx, cy = center
    s, c = math.sin(angle), math.cos(angle)
    px -= cx
    py -= cy
    x_new = px * c - py * s + cx
    y_new = px * s + py * c + cy
    return x_new, y_new

def get_hexagon_points(center, radius, angle):
    points = []
    for i in range(6):
        theta = math.radians(60 * i) + angle
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        points.append((x, y))
    return points

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def point_line_distance(point, line_start, line_end):
    px, py = point
    x1, y1 = line_start
    x2, y2 = line_end
    A = y2 - y1
    B = x1 - x2
    C = x2 * y1 - x1 * y2
    dist = abs(A * px + B * py + C) / math.sqrt(A**2 + B**2)
    return dist

def is_near_corner(ball_pos, hex_points, threshold=20):
    return any(distance(ball_pos, point) < threshold for point in hex_points)

def reflect_ball(ball_velocity, normal):
    dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1]
    ball_velocity[0] -= 2 * dot_product * normal[0]
    ball_velocity[1] -= 2 * dot_product * normal[1]
    ball_velocity[0] *= FRICTION
    ball_velocity[1] *= FRICTION
# ----------------------------------------------------------------------
def WRONG_keep_ball_inside(ball_pos, hex_points):
    """
    With this implementation the ball shows sometimes outside the edge line of the hexagon.
    While DeepSeek corrects the def. Perplixity Pedal-Perplexity-2.py keeps this def
    But it updates the collision detection in the main loop... for i in range(6): line 176
    """
    center_x, center_y = HEX_CENTER
    dx = ball_pos[0] - center_x
    dy = ball_pos[1] - center_y
    dist = math.sqrt(dx**2 + dy**2)
    if dist > HEX_RADIUS - BALL_RADIUS:
        angle = math.atan2(dy, dx)
        ball_pos[0] = center_x + (HEX_RADIUS - BALL_RADIUS) * math.cos(angle)
        ball_pos[1] = center_y + (HEX_RADIUS - BALL_RADIUS) * math.sin(angle)
# ---------
def keep_ball_inside(ball_pos, hex_points):
    """
    Fixed by DeepSeek.  Which said:
    The current implementation of keep_ball_inside only ensures that
    the ball's center stays within the hexagon's radius,
    but it doesn't account for the ball's radius when checking against the hexagon's edges.
    Here’s how you can modify the keep_ball_inside function to ensure that the ball stays entirely within the hexagon:
       Check the distance from the ball's center to each edge of the hexagon.
       Adjust the ball's position if it is too close to an edge, considering the ball's radius.
    """
    for i in range(6):
        start_point = hex_points[i]
        end_point = hex_points[(i + 1) % 6]

        # Calculate the normal vector of the edge
        edge_vector = [end_point[0] - start_point[0], end_point[1] - start_point[1]]
        normal = [-edge_vector[1], edge_vector[0]]
        normal_mag = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
        normal = [n / normal_mag for n in normal]

        # Calculate the distance from the ball's center to the edge
        dist = point_line_distance(ball_pos, start_point, end_point)

        # If the ball is too close to the edge, move it back inside
        if dist < BALL_RADIUS:
            # Calculate the overlap
            overlap = BALL_RADIUS - dist

            # Move the ball's center away from the edge by the overlap distance
            ball_pos[0] += normal[0] * overlap
            ball_pos[1] += normal[1] * overlap
# ---------------------------------------------------------------------
running = True
hex_angle = 0
bounce_angle = 0

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()
    if current_time - last_direction_change > random.randint(3000, 8000):
        rotation_direction *= -1
        last_direction_change = current_time

    hex_angle += HEX_ANGLE_SPEED * rotation_direction
    hex_points = get_hexagon_points(HEX_CENTER, HEX_RADIUS, hex_angle)

    ball_velocity[1] += GRAVITY
    new_ball_pos = [ball_pos[0] + ball_velocity[0], ball_pos[1] + ball_velocity[1]]

    for i in range(6):
        start_point = hex_points[i]
        end_point = hex_points[(i + 1) % 6]
        pygame.draw.line(screen, WHITE, start_point, end_point, 3)

        if point_line_distance(new_ball_pos, start_point, end_point) < BALL_RADIUS:
            normal = [-(end_point[1] - start_point[1]), end_point[0] - start_point[0]]
            normal_mag = math.sqrt(normal[0]**2 + normal[1]**2)
            normal = [n / normal_mag for n in normal]

            if not is_near_corner(new_ball_pos, hex_points):
                kick_angle = random.uniform(0, math.pi * 2)
                kick_force = random.uniform(KICK_FORCE_MIN, KICK_FORCE_MAX)
                ball_velocity[0] += math.cos(kick_angle) * kick_force
                ball_velocity[1] += math.sin(kick_angle) * kick_force

            reflect_ball(ball_velocity, normal)
            bounce_angle = math.degrees(math.atan2(-ball_velocity[1], ball_velocity[0]))

    ball_pos = new_ball_pos
    keep_ball_inside(ball_pos, hex_points)

    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    rotation_text = f"Rotation: {'Clockwise' if rotation_direction == 1 else 'Counterclockwise'}"
    velocity_text = f"Ball Velocity: {math.sqrt(ball_velocity[0]**2 + ball_velocity[1]**2):.2f}"
    bounce_text = f"Bounce Angle: {bounce_angle:.2f}°"

    rotation_surface = font.render(rotation_text, True, YELLOW)
    velocity_surface = font.render(velocity_text, True, YELLOW)
    bounce_surface = font.render(bounce_text, True, YELLOW)

    screen.blit(rotation_surface, (10, 10))
    screen.blit(velocity_surface, (10, 40))
    screen.blit(bounce_surface, (10, 70))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
