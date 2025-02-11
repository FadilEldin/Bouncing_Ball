###############################################################################################
# Fadil Eldin
# Feb/9/2025
# Second week with NOAA
###############################################################################################
"""
ChatGPT-4-turbo
Write a Python program that shows a ball bouncing inside a spinning hexagon.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.
"""
# Chat GPT 4:
# All good. Ball is bouncing, Ball is bouncing and is confined inside the Hexagon.
# When the bouncing settles. Ball is spinning "heavy" with the Hexagon. i.e. no bouncing
# First 3 codes were wrong
###############################################################################################
import pygame
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
HEXAGON_RADIUS = 200
HEXAGON_ANGLE_SPEED = 0.02  # Radians per frame
BALL_RADIUS = 15
FRICTION = 0.98
ELASTICITY = 0.8

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# Function to generate hexagon points
def get_hexagon_points(center, radius, angle):
    return [
        (
            center[0] + math.cos(math.pi / 3 * i + angle) * radius,
            center[1] + math.sin(math.pi / 3 * i + angle) * radius
        ) for i in range(6)
    ]


# Function to check and handle ball-wall collision
def handle_ball_collision(ball_pos, ball_vel, hexagon_points):
    for i in range(6):
        a, b = hexagon_points[i], hexagon_points[(i + 1) % 6]

        # Wall vector
        wall_dx, wall_dy = b[0] - a[0], b[1] - a[1]
        wall_length = math.sqrt(wall_dx ** 2 + wall_dy ** 2)
        wall_normal = (-wall_dy / wall_length, wall_dx / wall_length)

        # Distance from ball to wall
        ball_to_wall = (ball_pos[0] - a[0], ball_pos[1] - a[1])
        distance = abs(ball_to_wall[0] * wall_normal[0] + ball_to_wall[1] * wall_normal[1])

        if distance < BALL_RADIUS:
            # Reflect velocity along normal
            proj_length = (ball_vel[0] * wall_normal[0] + ball_vel[1] * wall_normal[1])
            ball_vel[0] -= 2 * proj_length * wall_normal[0] * ELASTICITY
            ball_vel[1] -= 2 * proj_length * wall_normal[1] * ELASTICITY

            # Push ball out of wall to prevent tunneling
            correction = (BALL_RADIUS - distance)
            ball_pos[0] += correction * wall_normal[0]
            ball_pos[1] += correction * wall_normal[1]

            # Apply friction
            ball_vel[0] *= FRICTION
            ball_vel[1] *= FRICTION
            return


# Ball attributes
ball_pos = [WIDTH // 2, HEIGHT // 3]
ball_vel = [2, 0]
angle = 0

running = True
while running:
    screen.fill((0, 0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate hexagon
    angle += HEXAGON_ANGLE_SPEED
    hexagon_points = get_hexagon_points((WIDTH // 2, HEIGHT // 2), HEXAGON_RADIUS, angle)
    pygame.draw.polygon(screen, (255, 255, 255), hexagon_points, 2)

    # Apply gravity
    ball_vel[1] += GRAVITY

    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Handle collision
    handle_ball_collision(ball_pos, ball_vel, hexagon_points)

    # Draw ball
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

