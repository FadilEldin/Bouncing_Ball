###############################################################################################
# Fadil Eldin
# Feb/9/2025
###############################################################################################
"""
DeepSeek-V3 (DeepThink R1)
Provided the GPT solution and asked to suggest improvements:
Answer:
Your code is already well-structured and functional, but there are a few areas where improvements can be made to enhance performance,
 readability, and realism. Here are some suggestions:
1. Improve Ball Collision Handling
  Issue: The ball's collision logic is axis-aligned, which can lead to unrealistic behavior when the cube is rotating.
  Solution: Use the cube's rotated normals to handle collisions more accurately. This ensures the ball bounces correctly
            even when the cube is spinning.
2. Add Depth Sorting for Realistic Rendering
  Issue: The cube's edges and the ball are drawn without considering depth, which can make the rendering look incorrect.
  Solution: Sort the cube's edges and the ball based on their depth (Z-coordinate) and draw them in the correct order.
3. Add Lighting and Shading
  Issue: The cube and ball look flat and lack depth.
  Solution: Simulate simple lighting by shading the cube's faces based on their orientation relative to a light source.
4. Optimize Performance
  Issue: The code recalculates the cube's vertices and normals every frame, which can be inefficient.
  Solution: Cache the cube's vertices and normals and only update them when necessary.
5. Add User Interaction
  Issue: The simulation is static and lacks interactivity.
  Solution: Allow the user to control the cube's rotation or the ball's initial velocity.

ChatGPT:
When KICK_FORCE_MAX is increased over 10, the ball bounces outside the cube:
Answer:
  Clamp the velocity after applying the kick force: Limit the maximum velocity of the ball along each axis to prevent it
  from gaining excessive speed.
  Correct the position after collision to prevent tunneling: Adjust the ball's position so that it remains inside
  the cube after a collision.
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
pygame.display.set_caption("3D Spinning Glass Cube with Bouncing Ball")

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
KICK_FORCE_MAX = 15  # Increase kick force here, up to 15 without ball escaping the cube.

# Maximum velocity clamp
MAX_VELOCITY = 20

# Projection properties (for simulating depth)
FOV = 500
PROJECTION_CENTER_X = WIDTH // 2
PROJECTION_CENTER_Y = HEIGHT // 2

# Timer for controlling spin direction changes
last_direction_change_time = pygame.time.get_ticks()
SPIN_DURATION_MS = 5000  # Spin in one direction for at least 5 seconds

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
    """Rotate a point in 3D space around the X, Y, and Z axes."""
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


def get_cube_normals(rotated_vertices):
    """Calculate the normal vectors of the cube's faces."""
    normals = []
    # Front and back faces (Z-axis)
    normals.append([0, 0, 1])  # Front face
    normals.append([0, 0, -1])  # Back face
    # Left and right faces (X-axis)
    normals.append([-1, 0, 0])  # Left face
    normals.append([1, 0, 0])  # Right face
    # Top and bottom faces (Y-axis)
    normals.append([0, 1, 0])  # Top face
    normals.append([0, -1, 0])  # Bottom face
    return normals


def handle_ball_collision(ball_pos, ball_velocity, rotated_vertices):
    """Handle collisions between the ball and the cube walls using face normals."""
    normals = get_cube_normals(rotated_vertices)
    for normal in normals:
        # Calculate the distance from the ball to the face
        distance = abs(ball_pos[0] * normal[0] + ball_pos[1] * normal[1] + ball_pos[2] * normal[2] - CUBE_SIZE / 2)
        if distance < BALL_RADIUS:
            # Reflect the ball's velocity off the face
            dot_product = ball_velocity[0] * normal[0] + ball_velocity[1] * normal[1] + ball_velocity[2] * normal[2]
            ball_velocity[0] -= 2 * dot_product * normal[0]
            ball_velocity[1] -= 2 * dot_product * normal[1]
            ball_velocity[2] -= 2 * dot_product * normal[2]

            # Add a random kick force
            kick_force = random.uniform(KICK_FORCE_MIN, KICK_FORCE_MAX)
            kick_angle_xy = random.uniform(0, math.pi * 2)
            ball_velocity[0] += math.cos(kick_angle_xy) * kick_force
            ball_velocity[1] += math.sin(kick_angle_xy) * kick_force
            ball_velocity[2] += random.uniform(-1, 1) * kick_force

            # Apply velocity clamping
            for i in range(3):
                ball_velocity[i] = max(-MAX_VELOCITY, min(MAX_VELOCITY, ball_velocity[i]))

            # Apply friction
            for i in range(3):
                ball_velocity[i] *= FRICTION

            # Correct position to ensure it doesn't "tunnel" through walls
            for i in range(3):
                if ball_pos[i] > CUBE_SIZE / 2 - BALL_RADIUS:
                    ball_pos[i] = CUBE_SIZE / 2 - BALL_RADIUS
                if ball_pos[i] < -CUBE_SIZE / 2 + BALL_RADIUS:
                    ball_pos[i] = -CUBE_SIZE / 2 + BALL_RADIUS


def calculate_face_brightness(normal, light_direction):
    """Calculate the brightness of a face based on its normal and a light direction."""
    dot_product = normal[0] * light_direction[0] + normal[1] * light_direction[1] + normal[2] * light_direction[2]
    brightness = max(0, min(1, (dot_product + 1) / 2))  # Normalize to [0, 1]
    return brightness


def draw_cube_with_lighting(rotated_vertices, projected_vertices):
    """Draw the cube's edges with lighting."""
    light_direction = [0, 0, -1]  # Light coming from the front
    normals = get_cube_normals(rotated_vertices)
    edges_with_brightness = []

    for edge in cube_edges:
        start_idx, end_idx = edge
        # Calculate the average normal of the two vertices
        normal = [(rotated_vertices[start_idx][i] + rotated_vertices[end_idx][i]) / 2 for i in range(3)]
        brightness = calculate_face_brightness(normal, light_direction)
        edges_with_brightness.append((brightness, edge))

    # Draw edges with brightness
    for brightness, edge in edges_with_brightness:
        start_idx, end_idx = edge
        color = tuple(int(GLASS_COLOR[i] * brightness) for i in range(3))
        pygame.draw.line(screen, color, projected_vertices[start_idx], projected_vertices[end_idx], width=1)


# Precompute cube vertices and normals
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

cube_normals_local = [
    [0, 0, 1],  # Front face
    [0, 0, -1],  # Back face
    [-1, 0, 0],  # Left face
    [1, 0, 0],  # Right face
    [0, 1, 0],  # Top face
    [0, -1, 0]  # Bottom face
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
    spin_text = font.render(spin_direction, True, YELLOW)
    velocity_text = font.render(f"Ball Speed: {ball_speed:.2f}", True, YELLOW)
    bounce_text = font.render(f"Bounce Angle: {bounce_angle:.2f}°", True, YELLOW)

    # Convert radians to degrees for display
    angle_x_deg = math.degrees(angle_x) % 360
    angle_y_deg = math.degrees(angle_y) % 360
    angle_z_deg = math.degrees(angle_z) % 360

    # Determine rotation directions
    x_direction = "+" if rotation_direction_x > 0 else "-"
    y_direction = "+" if rotation_direction_y > 0 else "-"
    z_direction = "+" if rotation_direction_z > 0 else "-"

    # Render rotation text
    pitch_text = font.render(f"Pitch (X): {x_direction}{angle_x_deg:.2f}°", True, YELLOW)
    yaw_text = font.render(f"Yaw (Y): {y_direction}{angle_y_deg:.2f}°", True, YELLOW)
    roll_text = font.render(f"Roll (Z): {z_direction}{angle_z_deg:.2f}°", True, YELLOW)

    # Display rotation text on the screen
    screen.blit(pitch_text, (10, 10))
    screen.blit(yaw_text, (10, 40))
    screen.blit(roll_text, (10, 70))
    screen.blit(velocity_text, (10, 100))
    screen.blit(bounce_text, (10, 130))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Change rotation direction after SPIN_DURATION_MS has passed
    current_time = pygame.time.get_ticks()
    if current_time - last_direction_change_time > SPIN_DURATION_MS:
        rotation_direction_x *= -1
        rotation_direction_y *= -1
        rotation_direction_z *= -1
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

    # handle_ball_collision()
    handle_ball_collision(ball_pos, ball_velocity, rotated_vertices)

    # Rotate and project the ball's position along with the cube's rotation axes
    rotated_ball_pos = rotate_point_3d(ball_pos, angle_x, angle_y, angle_z)
    projected_ball_pos = project_point(rotated_ball_pos)

    # Draw the bouncing ball inside the spinning cube as a red circle on screen
    pygame.draw.circle(screen, YELLOW, projected_ball_pos, BALL_RADIUS)

    # Update display and control frame rate to maintain smooth animation
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
