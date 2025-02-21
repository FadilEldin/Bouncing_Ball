###############################################################################################
# Fadil Eldin
# Feb/9/2025
###############################################################################################
"""
DeepSeek-V3 (DeepThink R1)
Write a Python program that shows a ball bouncing inside a spinning hexagon.
when the ball hits a hexagon wall, it gets kicked back at random angle and random force.
The ball should not go out of the hexagon and any time.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.
"""
###############################################################################################
import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 750, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DeepThink R1: Bouncing Ball in Spinning Hexagon")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (127, 127, 127)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Hexagon properties
hexagon_radius = 250
hexagon_center = (WIDTH // 2, HEIGHT // 2)
hexagon_angle = 0  # Initial rotation angle
hexagon_angular_velocity = 0.5  # Slower rotation speed in degrees per frame
hexagon_spin_direction = 1  # 1 for clockwise, -1 for counterclockwise
spin_reverse_timer = 0  # Timer to reverse spin direction
SPIN_DURATION_MIN = 300   # Spin in one direction between SPIN_DURATION_MIN_MS and SPIN_DURATION_MAZ_MS milliseconds
SPIN_DURATION_MAX = 1200
hexagon_wall_thickness = 5  # Thicker walls

# Ball properties
ball_radius = 20
ball_position = [WIDTH // 2, HEIGHT // 2]
ball_velocity = [5, -10]  # Initial velocity
gravity = 0.5
friction = 0.99

# Counters
total_time_counter = 0  # Counter for total time elapsed
direction_change_counter = 0  # Counter for time since last direction change

# Function to draw a hexagon with thicker walls
def draw_hexagon(surface, center, radius, angle, color, thickness):
    points = []
    for i in range(6):
        x = center[0] + radius * math.cos(math.radians(60 * i + angle))
        y = center[1] + radius * math.sin(math.radians(60 * i + angle))
        points.append((x, y))
    pygame.draw.polygon(surface, color, points, thickness)

# Function to check if a point is inside the hexagon
def is_point_inside_hexagon(point, center, radius, angle):
    x, y = point
    cx, cy = center
    # Translate point to hexagon's local coordinates
    x -= cx
    y -= cy
    # Rotate point to align with hexagon's orientation
    rad = math.radians(-angle)
    x_rot = x * math.cos(rad) - y * math.sin(rad)
    y_rot = x * math.sin(rad) + y * math.cos(rad)
    # Check if the point is inside the hexagon
    return abs(x_rot) <= radius and abs(y_rot) <= radius * math.sin(math.radians(60))

# Function to constrain the ball inside the hexagon
def constrain_ball_inside_hexagon(ball_pos, hex_center, hex_radius, hex_angle):
    if not is_point_inside_hexagon(ball_pos, hex_center, hex_radius, hex_angle):
        # Move the ball back to the closest point inside the hexagon
        angle_to_center = math.atan2(ball_pos[1] - hex_center[1], ball_pos[0] - hex_center[0])
        ball_pos[0] = hex_center[0] + (hex_radius - ball_radius) * math.cos(angle_to_center)
        ball_pos[1] = hex_center[1] + (hex_radius - ball_radius) * math.sin(angle_to_center)

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
            # Check if the ball is near a corner
            corner_threshold = 10  # Pixels from the corner
            if abs(projection) < corner_threshold or abs(projection - wall_length) < corner_threshold:
                # Roll with the hexagon's spin
                ball_vel[0] += hexagon_angular_velocity * 0.1
                ball_vel[1] += hexagon_angular_velocity * 0.1
            else:
                # Kick the ball with a random angle and force
                kick_angle = random.uniform(-45, 45)  # Random angle
                kick_force = random.uniform(5, 15)  # Random force
                ball_vel[0] += kick_force * math.cos(math.radians(kick_angle))
                ball_vel[1] += kick_force * math.sin(math.radians(kick_angle))

            # Reflect the ball's velocity
            normal_vector = (-wall_unit_vector[1], wall_unit_vector[0])
            dot_product = ball_vel[0] * normal_vector[0] + ball_vel[1] * normal_vector[1]
            ball_vel[0] -= 2 * dot_product * normal_vector[0]
            ball_vel[1] -= 2 * dot_product * normal_vector[1]

            # Move the ball out of the wall to prevent sticking
            overlap = ball_radius - distance
            ball_pos[0] += overlap * normal_vector[0]
            ball_pos[1] += overlap * normal_vector[1]

# Function to display information
def display_info(surface, hex_spin_direction, ball_vel, bounce_angle, total_time, direction_change_time):
    font = pygame.font.SysFont("Arial", 20)
    spin_text = f"Spin Direction: {'Clockwise' if hex_spin_direction == 1 else 'Counterclockwise'}"
    vel_text = f"Ball Velocity: ({ball_vel[0]:.2f}, {ball_vel[1]:.2f})"
    angle_text = f"Bounce Angle: {bounce_angle:.2f}°"
    total_time_text = f"Total Time: {total_time:.2f} s"
    direction_change_text = f"{direction_change_time:.1f} s"

    # Combine spin direction and direction change time into one line
    spin_and_direction_text = f"{spin_text} ({direction_change_text}) "

    # Render the text surfaces
    total_time_surface = font.render(total_time_text, True, BLUE)
    spin_and_direction_surface = font.render(spin_and_direction_text, True, BLUE)
    vel_surface = font.render(vel_text, True, BLUE)
    angle_surface = font.render(angle_text, True, BLUE)

    # Display the text on the screen
    surface.blit(total_time_surface, (10, 10))
    surface.blit(spin_and_direction_surface, (10, 30))
    surface.blit(vel_surface, (10, 50))
    surface.blit(angle_surface, (10, 70))


# Main loop
# Main loop
clock = pygame.time.Clock()
running = True
spin_duration = random.randint(SPIN_DURATION_MIN, SPIN_DURATION_MAX)  # Generate a random duration once
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update hexagon rotation
    hexagon_angle += hexagon_angular_velocity * hexagon_spin_direction
    if hexagon_angle >= 360:
        hexagon_angle -= 360
    elif hexagon_angle < 0:
        hexagon_angle += 360

    # Randomly reverse hexagon spin direction
    spin_reverse_timer += 1
    if spin_reverse_timer > spin_duration:  # Compare to the fixed random duration
        hexagon_spin_direction *= -1
        spin_reverse_timer = 0
        direction_change_counter = 0  # Reset the direction change counter
        spin_duration = random.randint(SPIN_DURATION_MIN, SPIN_DURATION_MAX)  # Generate a new random duration

    # Update ball position and velocity
    ball_velocity[1] += gravity  # Apply gravity
    ball_velocity[0] *= friction  # Apply friction
    ball_velocity[1] *= friction  # Apply friction
    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    # Constrain the ball inside the hexagon
    constrain_ball_inside_hexagon(ball_position, hexagon_center, hexagon_radius, hexagon_angle)

    # Check for collisions with hexagon walls
    check_collision(ball_position, ball_velocity, hexagon_center, hexagon_radius, hexagon_angle)

    # Update counters
    total_time_counter += clock.get_time() / 1000  # Convert milliseconds to seconds
    direction_change_counter += clock.get_time() / 1000  # Convert milliseconds to seconds

    # Clear the screen
    screen.fill(WHITE)

    # Draw the hexagon with thicker walls
    draw_hexagon(screen, hexagon_center, hexagon_radius, hexagon_angle, BLACK, hexagon_wall_thickness)

    # Draw the ball
    pygame.draw.circle(screen, BLUE, (int(ball_position[0]), int(ball_position[1])), ball_radius)

    # Display information
    bounce_angle = math.degrees(math.atan2(ball_velocity[1], ball_velocity[0]))
    display_info(screen, hexagon_spin_direction, ball_velocity, bounce_angle, total_time_counter, direction_change_counter)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)