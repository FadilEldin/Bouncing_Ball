###############################################################################################
# Fadil Eldin
# Feb/9/2025
###############################################################################################
"""
GPT-4o
Make a 3d spinning glass cube that rotates in all directions around its center
and let the ball bounce inside the cube.
Make the ball bounce off the walls of the cube . When it hits a wall it gets kicked back at random angle and random force
"""
###############################################################################################
import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("G: 3D Spinning Glass Cube with Bouncing Ball")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (127, 127, 127)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GLASS_COLOR = (100, 100, 255, 128)  # Semi-transparent blue for glass effect

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Cube properties
CUBE_SIZE = 300
CUBE_CENTER = [WIDTH // 2, HEIGHT // 2]
ROTATION_SPEED = math.radians(0.5)  # Speed of rotation in radians per frame

# Ball properties
BALL_RADIUS = 20
ball_pos = [0, 0, 0]  # Ball's position in the cube's local coordinate system
ball_velocity = [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)]
FRICTION = 0.98
KICK_FORCE_MIN = 2
KICK_FORCE_MAX = 7

# Projection properties (for simulating depth)
FOV = 500
PROJECTION_CENTER_X = WIDTH // 2
PROJECTION_CENTER_Y = HEIGHT // 2

# Timer for controlling spin direction changes
last_direction_change_time = pygame.time.get_ticks()
SPIN_DURATION_MIN_MS = 2000   # Spin in one direction between SPIN_DURATION_MIN_MS and SPIN_DURATION_MAZ_MS milliseconds
SPIN_DURATION_MAX_MS = 10000

# Rotation directions (X=Pitch, Y=Yaw, Z=Roll)
rotation_direction_x = random.choice([-1, 1])
rotation_direction_y = random.choice([-1, 1])
rotation_direction_z = random.choice([-1, 1])

def project_point(point):
    """Project a 3D point onto the screen."""
    x, y, z = point
    factor = FOV / (FOV + z) if FOV + z != 0 else FOV / (FOV + 1)
    projected_x = int(PROJECTION_CENTER_X + x * factor)
    projected_y = int(PROJECTION_CENTER_Y - y * factor)
    return projected_x, projected_y


def rotate_point_3d(point, angle_x, angle_y, angle_z):
    """Rotate a point in 3D space around the X and Y axes."""
    x, y, z = point

    # Rotate around X-axis (Pitch)
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y_new = y * cos_x - z * sin_x
    z_new = y * sin_x + z * cos_x

    # Rotate around Y-axis (Yaw)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x_new = x * cos_y + z_new * sin_y
    z_new = -x * sin_y + z_new * cos_y

    # Rotate around Z-axis (Roll)
    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x_final = x_new * cos_z - y_new * sin_z
    y_final = x_new * sin_z + y_new * cos_z

    return x_final, y_final, z_new


def handle_ball_collision():
    """Handle collisions between the ball and the cube walls."""
    global ball_pos, ball_velocity

    for i in range(3):  # Check each axis (x, y, z)
        if abs(ball_pos[i]) + BALL_RADIUS > CUBE_SIZE / 2:
            # Reverse direction and apply random kickback force and angle
            kick_force = random.uniform(KICK_FORCE_MIN, KICK_FORCE_MAX)
            kick_angle_xy = random.uniform(0, math.pi * 2)  # Random angle in XY plane

            if i == 0:  # X-axis collision
                ball_velocity[0] *= -1
                ball_velocity[1] += math.sin(kick_angle_xy) * kick_force
                ball_velocity[2] += math.cos(kick_angle_xy) * kick_force

            elif i == 1:  # Y-axis collision
                ball_velocity[1] *= -1
                ball_velocity[0] += math.cos(kick_angle_xy) * kick_force
                ball_velocity[2] += math.sin(kick_angle_xy) * kick_force

            elif i == 2:  # Z-axis collision
                ball_velocity[2] *= -1
                ball_velocity[0] += math.cos(kick_angle_xy) * kick_force
                ball_velocity[1] += math.sin(kick_angle_xy) * kick_force

            # Apply friction to slow down slightly after collision
            for j in range(3):
                ball_velocity[j] *= FRICTION

            # Correct position to ensure it doesn't "tunnel" through walls
            ball_pos[i] = math.copysign(CUBE_SIZE / 2 - BALL_RADIUS - 1e-3, ball_pos[i])


# Cube vertices in local space
cube_vertices_local = [
    [-CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],
    [CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],
    [CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],
    [-CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],
    [-CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],
    [CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],
    [CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2],
    [-CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2]
]

# Cube edges connecting vertices (pairs of indices from `cube_vertices_local`)
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back face edges
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front face edges
    (0, 4), (1, 5), (2, 6), (3, 7)  # Connecting edges between front and back faces
]

# Rotation angles for the cube
angle_x = angle_y = angle_z = math.radians(45)

running = True
while running:
    screen.fill(BLACK)

    # 3 lines displaying spin angle, ball velocity, and bounce angle
    # Calculate ball velocity magnitude
    font = pygame.font.SysFont("Arial", 20)
    ball_speed = math.sqrt(ball_velocity[0] ** 2 + ball_velocity[1] ** 2 + ball_velocity[2] ** 2)

    # Determine spin direction
    spin_direction = f"Spin: {'Clockwise' if rotation_direction_x == 1 else 'Counterclockwise'}"

    # Calculate bounce angle (angle of ball velocity in the XY plane)
    if ball_velocity[0] != 0 or ball_velocity[1] != 0:
        bounce_angle = math.degrees(math.atan2(ball_velocity[1], ball_velocity[0]))
    else:
        bounce_angle = 0

    # Render text
    spin_text = font.render(spin_direction, True, ORANGE)
    velocity_text = font.render(f"Ball Speed: {ball_speed:.2f}", True, ORANGE)
    bounce_text = font.render(f"Bounce Angle: {bounce_angle:.2f}°", True, ORANGE)

    # Convert radians to degrees for display
    angle_x_deg = math.degrees(angle_x) % 360
    angle_y_deg = math.degrees(angle_y) % 360
    angle_z_deg = math.degrees(angle_z) % 360

    # Determine rotation directions
    x_direction = "+" if rotation_direction_x > 0 else "-"
    y_direction = "+" if rotation_direction_y > 0 else "-"
    z_direction = "+" if rotation_direction_z > 0 else "-"

    # Render rotation text
    pitch_text = font.render(f"Pitch (X): {x_direction}{angle_x_deg:.2f}°", True, ORANGE)
    yaw_text = font.render(f"Yaw (Y): {y_direction}{angle_y_deg:.2f}°", True, ORANGE)
    roll_text = font.render(f"Roll (Z): {z_direction}{angle_z_deg:.2f}°", True, ORANGE)

    # Display rotation text on the screen
    screen.blit(pitch_text, (10, 10))
    screen.blit(yaw_text, (10, 40))
    screen.blit(roll_text, (10, 70))
    screen.blit(velocity_text, (10, 100))
    screen.blit(bounce_text, (10, 130))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Change rotation direction after random SPIN_DURATION_MIN_MS
    current_time = pygame.time.get_ticks()
    if current_time - last_direction_change_time > random.randint(SPIN_DURATION_MIN_MS, SPIN_DURATION_MAX_MS):
        rotation_direction_x *= -1
        rotation_direction_y *= -1
        last_direction_change_time = current_time

    # Rotate the cube around its center using current directions
    angle_x += ROTATION_SPEED * rotation_direction_x
    angle_y += ROTATION_SPEED * rotation_direction_y
    angle_z += ROTATION_SPEED * rotation_direction_z

    # Rotate cube vertices in local space to simulate spinning
    rotated_vertices = [rotate_point_3d(vertex, angle_x, angle_y, angle_z) for vertex in cube_vertices_local]
    rotated_ball_pos = rotate_point_3d(ball_pos, angle_x, angle_y, angle_z)


    # Project vertices onto the screen for rendering in pseudo-3D space
    projected_vertices = [project_point(vertex) for vertex in rotated_vertices]

    # Draw cube edges to form the spinning glass cube effect
    for edge in cube_edges:
        start_idx, end_idx = edge
        pygame.draw.line(screen, GLASS_COLOR, projected_vertices[start_idx], projected_vertices[end_idx], width=1)

    # Update ball position based on velocity
    for i in range(3):
        ball_pos[i] += ball_velocity[i]

    # Handle collisions between the ball and the walls of the cube
    handle_ball_collision()

    # Rotate and project the ball's position along with the cube's rotation axes
    rotated_ball_pos = rotate_point_3d(ball_pos, angle_x, angle_y,angle_z)
    projected_ball_pos = project_point(rotated_ball_pos)

    # Draw the bouncing ball inside the spinning cube as a red circle on screen
    pygame.draw.circle(screen, RED, projected_ball_pos, BALL_RADIUS)

    # Update display and control frame rate to maintain smooth animation
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
