###############################################################################################
# Fadil Eldin
# Feb/9/2025
# Second week with NOAA
###############################################################################################
"""
GPT-4o
Write a Python program that shows a ball bouncing inside a spinning hexagon.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.
"""
# Perplexity 1:
# All good. Ball is bouncing, Ball is bouncing and is confined inside the Hexagon.
# Works first time
###############################################################################################
import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Rotating Hexagon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Physics constants
GRAVITY = 0.5
FRICTION = 0.98
BOUNCE_FACTOR = 0.8

# Ball properties
ball_radius = 20
ball_pos = [WIDTH // 2, HEIGHT // 4]
ball_vel = [random.uniform(-5, 5), random.uniform(-5, 5)]

# Hexagon properties
hex_radius = 200
hex_center = (WIDTH // 2, HEIGHT // 2)
hex_rotation_speed = 2  # degrees per frame
hex_angle = 0


def get_hexagon_points(center, radius, angle):
    """Calculate the vertices of a rotated hexagon."""
    points = []
    for i in range(6):
        theta = math.radians(angle + i * 60)  # Each vertex is separated by 60 degrees
        x = center[0] + radius * math.cos(theta)
        y = center[1] + radius * math.sin(theta)
        points.append((x, y))
    return points


def reflect_vector(vx, vy, nx, ny):
    """Reflect a vector (vx, vy) off a surface with normal (nx, ny)."""
    dot_product = vx * nx + vy * ny
    reflected_vx = vx - 2 * dot_product * nx
    reflected_vy = vy - 2 * dot_product * ny
    return reflected_vx, reflected_vy

def main():
    global hex_angle

    running = True
    while running:
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update hexagon rotation angle
        hex_angle += hex_rotation_speed
        hex_points = get_hexagon_points(hex_center, hex_radius, hex_angle)

        # Draw the hexagon
        pygame.draw.polygon(screen, WHITE, hex_points, width=2)

        # Update ball position with gravity and velocity
        ball_vel[1] += GRAVITY
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]

        # Check collision with hexagon walls
        for i in range(len(hex_points)):
            p1 = hex_points[i]
            p2 = hex_points[(i + 1) % len(hex_points)]

            # Wall vector and normal vector calculation
            wall_dx = p2[0] - p1[0]
            wall_dy = p2[1] - p1[1]
            wall_length = math.sqrt(wall_dx**2 + wall_dy**2)
            wall_normal_x = -wall_dy / wall_length
            wall_normal_y = wall_dx / wall_length

            # Ball-to-wall collision detection using line projection and distance check
            t = ((ball_pos[0] - p1[0]) * wall_dx + (ball_pos[1] - p1[1]) * wall_dy) / (wall_length**2)
            closest_x = p1[0] + t * wall_dx
            closest_y = p1[1] + t * wall_dy

            distance_to_wall = math.sqrt((ball_pos[0] - closest_x)**2 + (ball_pos[1] - closest_y)**2)

            if distance_to_wall <= ball_radius and 0 <= t <= 1:
                # Reflect the ball's velocity off the wall's normal vector
                ball_vel[0], ball_vel[1] = reflect_vector(ball_vel[0], ball_vel[1], wall_normal_x, wall_normal_y)
                ball_vel[0] *= FRICTION
                ball_vel[1] *= FRICTION

                # Move the ball out of collision to prevent sticking to the wall
                overlap_dist = ball_radius - distance_to_wall
                ball_pos[0] += overlap_dist * wall_normal_x
                ball_pos[1] += overlap_dist * wall_normal_y

        # Bounce off screen edges (optional safeguard)
        if ball_pos[0] < ball_radius or ball_pos[0] > WIDTH - ball_radius:
            ball_vel[0] *= -BOUNCE_FACTOR
            ball_pos[0] = max(ball_radius, min(WIDTH - ball_radius, ball_pos[0]))
        if ball_pos[1] < ball_radius or ball_pos[1] > HEIGHT - ball_radius:
            ball_vel[1] *= -BOUNCE_FACTOR
            ball_pos[1] = max(ball_radius, min(HEIGHT - ball_radius, ball_pos[1]))

        # Draw the bouncing ball
        pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

        # Update the display and tick the clock
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
