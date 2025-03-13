###############################################################################################
# Fadil Eldin
# March/13/2025
###############################################################################################
"""
Manus
Write a Python program that shows a ball bouncing inside a spinning hexagon.
The ball should be affected by gravity and friction, and it must bounce off the rotating walls realistically.

Change spin direction randomly.
Display on the left upper corner
    Spin Direction
    Ball Velocity
    Bounce Angle
    Total Time
    direction change time

Now let's add a kick. When the ball touches any side, kich with random force and at random angle.
The ball should always remain inside the Hexagon.

(The ball escaped the hexagon)
Fixed
"""
###############################################################################################
import pygame
import sys
import math
import numpy as np
import random
import time

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 700, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Manus: Ball Bouncing in a Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# Physics constants
GRAVITY = 0.5
FRICTION = 0.98
ROTATION_SPEED = 0.01  # Radians per frame

# Kick parameters
MIN_KICK_FORCE = 3.0
MAX_KICK_FORCE = 8.0

# Ball properties
ball_radius = 15
ball_pos = np.array([WIDTH // 2, HEIGHT // 2], dtype=float)
ball_vel = np.array([2.0, 0.0], dtype=float)

# Hexagon properties
hexagon_radius = 250
hexagon_center = np.array([WIDTH // 2, HEIGHT // 2])
hexagon_angle = 0

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Disable audio to prevent ALSA errors
pygame.mixer.quit()

# Font for text display
font = pygame.font.SysFont('Arial', 16)

# Tracking variables
start_time = time.time()
last_bounce_time = start_time
last_direction_change_time = start_time
bounce_angle = 0
spin_direction = "Clockwise"  # Initial spin direction
total_bounces = 0
last_kick_force = 0.0
last_kick_angle = 0.0

# Kick effect visualization
kick_effect_time = 0
kick_effect_duration = 15  # frames

# Random direction change settings
MIN_DIRECTION_CHANGE_TIME = 3.0  # Minimum time between direction changes (seconds)
MAX_DIRECTION_CHANGE_TIME = 8.0  # Maximum time between direction changes (seconds)
next_direction_change = start_time + random.uniform(MIN_DIRECTION_CHANGE_TIME, MAX_DIRECTION_CHANGE_TIME)


def get_hexagon_vertices():
    """Calculate the vertices of the hexagon based on current rotation angle."""
    vertices = []
    for i in range(6):
        angle = hexagon_angle + i * (2 * math.pi / 6)
        x = hexagon_center[0] + hexagon_radius * math.cos(angle)
        y = hexagon_center[1] + hexagon_radius * math.sin(angle)
        vertices.append((x, y))
    return vertices


def get_hexagon_edges():
    """Get the edges (line segments) of the hexagon."""
    vertices = get_hexagon_vertices()
    edges = []
    for i in range(6):
        edges.append((vertices[i], vertices[(i + 1) % 6]))
    return edges


def distance_point_to_line(point, line_start, line_end):
    """Calculate the distance from a point to a line segment."""
    line_vec = np.array(line_end) - np.array(line_start)
    point_vec = np.array(point) - np.array(line_start)
    line_len = np.linalg.norm(line_vec)
    line_unitvec = line_vec / line_len
    point_vec_scaled = point_vec / line_len

    t = np.dot(line_unitvec, point_vec_scaled)
    t = max(0, min(1, t))  # Clamp t to [0,1]

    nearest = np.array(line_start) + t * line_vec
    dist = np.linalg.norm(np.array(point) - nearest)
    return dist, nearest


def reflect_velocity(velocity, normal):
    """Reflect velocity vector across a normal vector."""
    normal = normal / np.linalg.norm(normal)  # Normalize
    return velocity - 2 * np.dot(velocity, normal) * normal


def calculate_angle_degrees(vector):
    """Calculate the angle in degrees of a vector from the positive x-axis."""
    angle_rad = math.atan2(vector[1], vector[0])
    angle_deg = math.degrees(angle_rad)
    return (angle_deg + 360) % 360  # Normalize to [0, 360)


def apply_random_kick():
    """Apply a random kick to the ball."""
    global ball_vel, last_kick_force, last_kick_angle, kick_effect_time

    # Generate random kick force and angle
    kick_force = random.uniform(MIN_KICK_FORCE, MAX_KICK_FORCE)
    kick_angle_rad = random.uniform(0, 2 * math.pi)

    # Calculate kick vector
    kick_x = kick_force * math.cos(kick_angle_rad)
    kick_y = kick_force * math.sin(kick_angle_rad)
    kick_vector = np.array([kick_x, kick_y])

    # Apply kick to ball velocity
    ball_vel += kick_vector

    # Store kick information for display
    last_kick_force = kick_force
    last_kick_angle = math.degrees(kick_angle_rad)

    # Set kick effect visualization timer
    kick_effect_time = kick_effect_duration


def check_collision():
    """Check and handle collision between ball and hexagon edges."""
    global ball_pos, ball_vel, bounce_angle, last_bounce_time, total_bounces

    edges = get_hexagon_edges()
    collision_occurred = False

    for edge in edges:
        dist, nearest = distance_point_to_line(ball_pos, edge[0], edge[1])

        if dist <= ball_radius:
            # Calculate normal vector (perpendicular to the edge)
            edge_vec = np.array(edge[1]) - np.array(edge[0])
            normal = np.array([-edge_vec[1], edge_vec[0]])
            normal = normal / np.linalg.norm(normal)

            # Make sure normal points toward the ball
            if np.dot(normal, ball_pos - np.array(edge[0])) < 0:
                normal = -normal

            # Move ball outside the edge
            penetration = ball_radius - dist
            ball_pos = ball_pos + penetration * normal

            # Calculate bounce angle (angle between incoming velocity and normal)
            incoming_angle = calculate_angle_degrees(ball_vel)
            normal_angle = calculate_angle_degrees(normal)
            bounce_angle = abs(incoming_angle - normal_angle)
            if bounce_angle > 180:
                bounce_angle = 360 - bounce_angle

            # Reflect velocity with some energy loss (friction)
            ball_vel = reflect_velocity(ball_vel, normal) * FRICTION

            # Add some effect from the rotating hexagon
            tangent = np.array([normal[1], -normal[0]])
            rotation_effect = ROTATION_SPEED * hexagon_radius * tangent
            ball_vel = ball_vel + rotation_effect * 0.2

            # Apply random kick
            apply_random_kick()

            # Update bounce time
            last_bounce_time = time.time()
            total_bounces += 1
            collision_occurred = True

    return collision_occurred


def toggle_spin_direction():
    """Toggle the spin direction of the hexagon."""
    global ROTATION_SPEED, spin_direction, last_direction_change_time, next_direction_change
    ROTATION_SPEED = -ROTATION_SPEED
    spin_direction = "Clockwise" if ROTATION_SPEED > 0 else "Counter-Clockwise"
    last_direction_change_time = time.time()
    # Schedule next random direction change
    next_direction_change = last_direction_change_time + random.uniform(MIN_DIRECTION_CHANGE_TIME,
                                                                        MAX_DIRECTION_CHANGE_TIME)


def enforce_boundary():
    """Ensure the ball stays inside the hexagon."""
    global ball_pos, ball_vel

    # Get current hexagon vertices
    vertices = get_hexagon_vertices()

    # Check if ball is too far from center
    dist_from_center = np.linalg.norm(ball_pos - hexagon_center)
    max_safe_dist = hexagon_radius - ball_radius - 5  # 5 pixel buffer

    if dist_from_center > max_safe_dist:
        # Ball is too close to edge, apply correction
        to_center = hexagon_center - ball_pos
        to_center_norm = to_center / np.linalg.norm(to_center)

        # Move ball to safe position
        ball_pos = hexagon_center - max_safe_dist * to_center_norm

        # Add velocity component toward center
        if np.dot(ball_vel, to_center) < 0:  # If moving away from center
            ball_vel = reflect_velocity(ball_vel, to_center_norm) * FRICTION


def main():
    global ball_pos, ball_vel, hexagon_angle, next_direction_change, kick_effect_time

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    toggle_spin_direction()
                elif event.key == pygame.K_r:
                    # Reset ball position to center
                    ball_pos = np.array([WIDTH // 2, HEIGHT // 2], dtype=float)
                    ball_vel = np.array([2.0, 0.0], dtype=float)

        # Check if it's time for a random direction change
        current_time = time.time()
        if current_time >= next_direction_change:
            toggle_spin_direction()

        # Clear screen
        screen.fill(BLACK)

        # Update hexagon rotation
        hexagon_angle += ROTATION_SPEED

        # Update ball position with gravity
        ball_vel[1] += GRAVITY
        ball_pos += ball_vel

        # Check for collision with hexagon
        check_collision()

        # Enforce boundary to keep ball inside
        enforce_boundary()

        # Draw hexagon
        pygame.draw.polygon(screen, WHITE, get_hexagon_vertices(), 2)

        # Draw ball with kick effect
        ball_color = RED
        if kick_effect_time > 0:
            # Flash yellow when kicked
            ball_color = YELLOW
            kick_effect_time -= 1

            # Draw kick vector line
            kick_line_end = (
                int(ball_pos[0] + last_kick_force * 5 * math.cos(math.radians(last_kick_angle))),
                int(ball_pos[1] + last_kick_force * 5 * math.sin(math.radians(last_kick_angle)))
            )
            pygame.draw.line(screen, YELLOW, (int(ball_pos[0]), int(ball_pos[1])), kick_line_end, 2)

        pygame.draw.circle(screen, ball_color, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

        # Calculate current metrics
        elapsed_time = current_time - start_time
        time_since_direction_change = current_time - last_direction_change_time
        velocity_magnitude = np.linalg.norm(ball_vel)
        velocity_angle = calculate_angle_degrees(ball_vel)

        # Display text information
        text_lines = [
            f"Spin Direction: {spin_direction}",
            f"Ball Velocity: {velocity_magnitude:.2f} px/frame @ {velocity_angle:.1f}°",
            f"Bounce Angle: {bounce_angle:.1f}°",
            f"Total Time: {elapsed_time:.2f} sec",
            f"Direction Change Time: {time_since_direction_change:.2f} sec",
            f"Last Kick: {last_kick_force:.2f} @ {last_kick_angle:.1f}°"
        ]

        for i, line in enumerate(text_lines):
            text_surface = font.render(line, True, BLUE)
            screen.blit(text_surface, (10, 10 + i * 20))

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()


