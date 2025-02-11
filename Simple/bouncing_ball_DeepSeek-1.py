###############################################################################################
# Fadil Eldin
# Feb/9/2025
# Second week with NOAA
###############################################################################################
"""
DeepSeek-V3
Write a Python program that shows a ball bouncing inside a spinning hexagon.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.
"""
# DeepSeek 1:
# First code, Ball is bouncing, is confined inside the Hexagon. But the hexagon is not spinning
###############################################################################################
import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Hexagon properties
hexagon_radius = 250
hexagon_center = (WIDTH // 2, HEIGHT // 2)
hexagon_angle = 0  # Rotation angle
hexagon_angular_velocity = 0.01  # Rotation speed

# Ball properties
ball_radius = 20
ball_position = [WIDTH // 2, HEIGHT // 2]
ball_velocity = [5, -10]  # Initial velocity
gravity = 0.5
friction = 0.99

# Function to draw a hexagon
def draw_hexagon(surface, center, radius, angle, color):
    points = []
    for i in range(6):
        x = center[0] + radius * math.cos(math.radians(60 * i + angle))
        y = center[1] + radius * math.sin(math.radians(60 * i + angle))
        points.append((x, y))
    pygame.draw.polygon(surface, color, points, 2)

# Function to check collision between ball and hexagon walls
def check_collision(ball_pos, ball_vel, hex_center, hex_radius, hex_angle):
    for i in range(6):
        # Get two points of the hexagon wall
        x1 = hex_center[0] + hex_radius * math.cos(math.radians(60 * i + hex_angle))
        y1 = hex_center[1] + hex_radius * math.sin(math.radians(60 * i + hex_angle))
        x2 = hex_center[0] + hex_radius * math.cos(math.radians(60 * (i + 1) + hex_angle))
        y2 = hex_center[1] + hex_radius * math.sin(math.radians(60 * (i + 1) + hex_angle))

        # Vector of the wall
        wall_vector = (x2 - x1, y2 - y1)
        wall_length = math.hypot(wall_vector[0], wall_vector[1])
        wall_unit_vector = (wall_vector[0] / wall_length, wall_vector[1] / wall_length)

        # Vector from ball to wall start
        ball_to_wall = (ball_pos[0] - x1, ball_pos[1] - y1)

        # Project ball position onto the wall vector
        projection = (ball_to_wall[0] * wall_unit_vector[0] + ball_to_wall[1] * wall_unit_vector[1])

        # Closest point on the wall to the ball
        closest_point = (x1 + projection * wall_unit_vector[0], y1 + projection * wall_unit_vector[1])

        # Distance from ball to closest point on the wall
        distance = math.hypot(ball_pos[0] - closest_point[0], ball_pos[1] - closest_point[1])

        # Check if the ball is colliding with the wall
        if distance <= ball_radius:
            # Reflect the ball's velocity
            normal_vector = (-wall_unit_vector[1], wall_unit_vector[0])
            dot_product = ball_vel[0] * normal_vector[0] + ball_vel[1] * normal_vector[1]
            ball_vel[0] -= 2 * dot_product * normal_vector[0]
            ball_vel[1] -= 2 * dot_product * normal_vector[1]

            # Move the ball out of the wall to prevent sticking
            overlap = ball_radius - distance
            ball_pos[0] += overlap * normal_vector[0]
            ball_pos[1] += overlap * normal_vector[1]

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    hexagon_angle += hexagon_angular_velocity

    # Update ball position and velocity
    ball_velocity[1] += gravity  # Apply gravity
    ball_velocity[0] *= friction  # Apply friction
    ball_velocity[1] *= friction  # Apply friction
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    # Check for collisions with hexagon walls
    check_collision(ball_position, ball_velocity, hexagon_center, hexagon_radius, hexagon_angle)

    # Clear the screen
    screen.fill(WHITE)

    # Draw the hexagon
    draw_hexagon(screen, hexagon_center, hexagon_radius, hexagon_angle, BLACK)

    # Draw the ball
    pygame.draw.circle(screen, RED, (int(ball_position[0]), int(ball_position[1])), ball_radius)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()