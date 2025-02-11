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
# Chat GPT 1:
# Hexagon is spinning, Ball is bouncing. But after few bounces ball drops and is stuck at bottom of window
###############################################################################################
import pygame
import math

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 900
HEXAGON_RADIUS = 200
HEXAGON_ANGLE_SPEED = 0.02  # Radians per frame
BALL_RADIUS = 15
FRICTION = 0.9
ELASTICITY = 0.8

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# Function to draw hexagon
def draw_hexagon(surface, center, radius, angle):
    points = [
        (
            center[0] + math.cos(math.pi / 3 * i + angle) * radius,
            center[1] + math.sin(math.pi / 3 * i + angle) * radius
        ) for i in range(6)
    ]
    pygame.draw.polygon(surface, (255, 255, 255), points, 2)


# Ball attributes
ball_pos = [WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 0]
ball_acc = [0, GRAVITY / FPS]

running = True
angle = 0
while running:
    screen.fill((0, 0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate hexagon
    angle += HEXAGON_ANGLE_SPEED
    draw_hexagon(screen, (WIDTH // 2, HEIGHT // 2), HEXAGON_RADIUS, angle)

    # Update ball position
    ball_vel[1] += ball_acc[1]
    ball_pos[1] += ball_vel[1]

    # Ball collision with floor
    if ball_pos[1] + BALL_RADIUS >= HEIGHT:
        ball_pos[1] = HEIGHT - BALL_RADIUS
        ball_vel[1] = -ball_vel[1] * ELASTICITY

    pygame.draw.circle(screen, (255, 0, 0), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
