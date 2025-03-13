###############################################################################################
# Fadil Eldin
# March/13/2025
###############################################################################################
"""
Manus
(after completing the 2D_BouncingBall_Hexagon-Manus.py
Now let's create a more interetsing version. Instead of a 2-d hexagon, let's make a 3-d cube.
Everything else is the same. Except that now the ball will bounce on 6 sides of a cube while visible (as before)
on the 2-d sides of screen, we should also see it go (deep) inside the cube and come forward on the 3-d cube.
The cube in the new version will spin in all directions, not just clockwise or counter-clockwise.
So you need to show Pitch, Yaw and Roll angles while its changing the spin.

Muns replied with:
I'll create a 3D cube version of the simulation! This is an exciting evolution that will add depth to the
visualization while maintaining the core physics you like. Let me work on implementing:
1- A 3D cube instead of a 2D hexagon
2- Ball movement in 3D space (including depth perception)
3- Full 3D rotation (pitch, yaw, and roll) instead of just 2D rotation
4- Display of all three rotation angles in the UI
5- Maintaining the same physics principles for bouncing and kicks
This will require using 3D projection techniques to display the cube and ball on a 2D screen while giving the
illusion of depth. I'll get started on this right away.
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
pygame.display.set_caption("Manus: Ball Bouncing in a 3D Cube")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Physics constants
GRAVITY = 0.05
FRICTION = 0.98

# Rotation speeds (radians per frame)
PITCH_SPEED = 0.01
YAW_SPEED = 0.01
ROLL_SPEED = 0.01

# Kick parameters
MIN_KICK_FORCE = 0.4
MAX_KICK_FORCE = 15.0

# 3D Cube properties
CUBE_SIZE = 280
cube_center = np.array([WIDTH // 2, HEIGHT // 2, 0], dtype=float)
cube_vertices = np.array([
    [-CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],  # 0: back bottom left
    [CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2],  # 1: back bottom right
    [CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],  # 2: back top right
    [-CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2],  # 3: back top left
    [-CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],  # 4: front bottom left
    [CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2],  # 5: front bottom right
    [CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2],  # 6: front top right
    [-CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2]  # 7: front top left
], dtype=float)

# Cube edges (pairs of vertex indices)
cube_edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # back face
    (4, 5), (5, 6), (6, 7), (7, 4),  # front face
    (0, 4), (1, 5), (2, 6), (3, 7)  # connecting edges
]

# Cube faces (groups of vertex indices)
cube_faces = [
    [0, 1, 2, 3],  # back face
    [4, 5, 6, 7],  # front face
    [0, 1, 5, 4],  # bottom face
    [2, 3, 7, 6],  # top face
    [0, 3, 7, 4],  # left face
    [1, 2, 6, 5]  # right face
]

# Face colors (semi-transparent)
face_colors = [
    (*PURPLE, 50),  # back face
    (*CYAN, 50),  # front face
    (*RED, 50),  # bottom face
    (*GREEN, 50),  # top face
    (*BLUE, 50),  # left face
    (*YELLOW, 50)  # right face
]

# Ball properties
BALL_RADIUS = 20
ball_pos = np.array([0, 0, 0], dtype=float)  # Center of the cube
ball_vel = np.array([random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)], dtype=float)

# Rotation angles
pitch = 0  # X-axis rotation
yaw = 0  # Y-axis rotation
roll = 0  # Z-axis rotation

# Rotation directions
pitch_direction = 1
yaw_direction = 1
roll_direction = 1

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
total_bounces = 0
last_kick_force = 0.0
last_kick_angle = 0.0
last_face_hit = "None"

# Kick effect visualization
kick_effect_time = 0
kick_effect_duration = 15  # frames

# Random direction change settings
MIN_DIRECTION_CHANGE_TIME = 3.0  # Minimum time between direction changes (seconds)
MAX_DIRECTION_CHANGE_TIME = 10.0  # Maximum time between direction changes (seconds)
next_direction_change = start_time + random.uniform(MIN_DIRECTION_CHANGE_TIME, MAX_DIRECTION_CHANGE_TIME)


def rotation_matrix_x(angle):
    """Return the rotation matrix for rotation around X axis."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return np.array([
        [1, 0, 0],
        [0, cos_a, -sin_a],
        [0, sin_a, cos_a]
    ])


def rotation_matrix_y(angle):
    """Return the rotation matrix for rotation around Y axis."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return np.array([
        [cos_a, 0, sin_a],
        [0, 1, 0],
        [-sin_a, 0, cos_a]
    ])


def rotation_matrix_z(angle):
    """Return the rotation matrix for rotation around Z axis."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])


def project_3d_to_2d(point_3d, z_scale=400):
    """Project a 3D point to 2D screen coordinates using perspective projection."""
    # Perspective division (further objects appear smaller)
    z = max(0.1, point_3d[2] + z_scale)  # Avoid division by zero
    scale_factor = z_scale / z

    # Project to 2D and translate to screen center
    x = point_3d[0] * scale_factor + WIDTH // 2
    y = point_3d[1] * scale_factor + HEIGHT // 2

    return (x, y)


def rotate_point(point, rotation_matrices):
    """Rotate a 3D point using the given rotation matrices."""
    # Apply all rotation matrices in sequence
    rotated_point = point.copy()
    for matrix in rotation_matrices:
        rotated_point = np.dot(matrix, rotated_point)
    return rotated_point


def get_rotated_vertices():
    """Get the rotated vertices of the cube."""
    # Create rotation matrices
    rot_x = rotation_matrix_x(pitch)
    rot_y = rotation_matrix_y(yaw)
    rot_z = rotation_matrix_z(roll)

    # Apply rotations in order: first pitch, then yaw, then roll
    rotation_matrices = [rot_x, rot_y, rot_z]

    # Rotate each vertex
    rotated_vertices = []
    for vertex in cube_vertices:
        rotated_vertex = rotate_point(vertex, rotation_matrices)
        rotated_vertices.append(rotated_vertex)

    return np.array(rotated_vertices)


def get_projected_vertices(rotated_vertices):
    """Project the rotated vertices to 2D screen coordinates."""
    projected_vertices = []
    for vertex in rotated_vertices:
        projected_vertex = project_3d_to_2d(vertex)
        projected_vertices.append(projected_vertex)

    return projected_vertices


def calculate_face_depths(rotated_vertices):
    """Calculate the average depth (z-coordinate) of each face."""
    face_depths = []
    for face in cube_faces:
        # Calculate average z-coordinate of the face
        avg_z = sum(rotated_vertices[i][2] for i in face) / len(face)
        face_depths.append(avg_z)

    return face_depths


def draw_cube(projected_vertices, face_depths):
    """Draw the cube with proper depth ordering."""
    # Sort faces by depth (back to front)
    sorted_indices = np.argsort(face_depths)

    # Draw faces from back to front (painter's algorithm)
    for idx in sorted_indices:
        face = cube_faces[idx]
        color = face_colors[idx]

        # Get the projected vertices for this face
        face_vertices = [projected_vertices[i] for i in face]

        # Draw face with semi-transparency
        face_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(face_surface, color, face_vertices)
        screen.blit(face_surface, (0, 0))

    # Draw edges
    for edge in cube_edges:
        pygame.draw.line(screen, WHITE, projected_vertices[edge[0]], projected_vertices[edge[1]], 1)


def project_ball(ball_pos, z_scale=400):
    """Project the 3D ball position to 2D screen coordinates."""
    projected_pos = project_3d_to_2d(ball_pos, z_scale)

    # Scale ball size based on depth
    z = max(0.1, ball_pos[2] + z_scale)
    scale_factor = z_scale / z
    radius = int(BALL_RADIUS * scale_factor)

    return projected_pos, radius


def check_cube_collision():
    """Check and handle collision between ball and cube faces."""
    global ball_pos, ball_vel, bounce_angle, last_bounce_time, total_bounces, last_face_hit

    # Half size of the cube
    half_size = CUBE_SIZE / 2
    collision_occurred = False

    # Check collision with each face
    face_names = ["Back", "Front", "Bottom", "Top", "Left", "Right"]

    # Check X boundaries (left and right faces)
    if abs(ball_pos[0]) + BALL_RADIUS > half_size:
        # Determine which face was hit
        face_index = 5 if ball_pos[0] > 0 else 4  # 5 = right, 4 = left

        # Calculate normal vector (pointing inward)
        normal = np.array([-1 if ball_pos[0] > 0 else 1, 0, 0], dtype=float)

        # Move ball inside
        penetration = abs(ball_pos[0]) + BALL_RADIUS - half_size
        ball_pos[0] -= penetration * np.sign(ball_pos[0])

        # Apply collision response
        apply_collision_response(normal, face_names[face_index])
        collision_occurred = True

    # Check Y boundaries (top and bottom faces)
    if abs(ball_pos[1]) + BALL_RADIUS > half_size:
        # Determine which face was hit
        face_index = 3 if ball_pos[1] > 0 else 2  # 3 = top, 2 = bottom

        # Calculate normal vector (pointing inward)
        normal = np.array([0, -1 if ball_pos[1] > 0 else 1, 0], dtype=float)

        # Move ball inside
        penetration = abs(ball_pos[1]) + BALL_RADIUS - half_size
        ball_pos[1] -= penetration * np.sign(ball_pos[1])

        # Apply collision response
        apply_collision_response(normal, face_names[face_index])
        collision_occurred = True

    # Check Z boundaries (front and back faces)
    if abs(ball_pos[2]) + BALL_RADIUS > half_size:
        # Determine which face was hit
        face_index = 1 if ball_pos[2] > 0 else 0  # 1 = front, 0 = back

        # Calculate normal vector (pointing inward)
        normal = np.array([0, 0, -1 if ball_pos[2] > 0 else 1], dtype=float)

        # Move ball inside
        penetration = abs(ball_pos[2]) + BALL_RADIUS - half_size
        ball_pos[2] -= penetration * np.sign(ball_pos[2])

        # Apply collision response
        apply_collision_response(normal, face_names[face_index])
        collision_occurred = True

    return collision_occurred


def apply_collision_response(normal, face_name):
    """Apply collision response including reflection and random kick."""
    global ball_vel, bounce_angle, last_bounce_time, total_bounces, last_face_hit

    # Calculate bounce angle
    incoming_velocity = np.linalg.norm(ball_vel)
    dot_product = np.dot(ball_vel, normal)
    bounce_angle = math.degrees(math.acos(abs(dot_product) / (incoming_velocity * np.linalg.norm(normal))))

    # Reflect velocity
    ball_vel = ball_vel - 2 * np.dot(ball_vel, normal) * normal

    # Apply friction
    ball_vel = ball_vel * FRICTION

    # Apply random kick
    apply_random_kick()

    # Update tracking variables
    last_bounce_time = time.time()
    total_bounces += 1
    last_face_hit = face_name


def apply_random_kick():
    """Apply a random kick to the ball."""
    global ball_vel, last_kick_force, last_kick_angle, kick_effect_time

    # Generate random kick force and direction
    kick_force = random.uniform(MIN_KICK_FORCE, MAX_KICK_FORCE)

    # Random 3D direction
    theta = random.uniform(0, math.pi * 2)  # Azimuthal angle
    phi = random.uniform(0, math.pi)  # Polar angle

    # Convert spherical to Cartesian coordinates
    kick_x = kick_force * math.sin(phi) * math.cos(theta)
    kick_y = kick_force * math.sin(phi) * math.sin(theta)
    kick_z = kick_force * math.cos(phi)

    kick_vector = np.array([kick_x, kick_y, kick_z])

    # Apply kick to ball velocity
    ball_vel += kick_vector

    # Store kick information for display
    last_kick_force = kick_force
    last_kick_angle = math.degrees(theta)  # Just store azimuthal angle for display

    # Set kick effect visualization timer
    kick_effect_time = kick_effect_duration


def toggle_rotation_direction():
    """Randomly toggle one of the rotation directions."""
    global pitch_direction, yaw_direction, roll_direction, last_direction_change_time, next_direction_change

    # Choose which rotation to change
    rotation_choice = random.randint(0, 2)

    if rotation_choice == 0:
        pitch_direction *= -1
    elif rotation_choice == 1:
        yaw_direction *= -1
    else:
        roll_direction *= -1

    # Update timing
    last_direction_change_time = time.time()
    next_direction_change = last_direction_change_time + random.uniform(MIN_DIRECTION_CHANGE_TIME,
                                                                        MAX_DIRECTION_CHANGE_TIME)


def enforce_boundary():
    """Ensure the ball stays inside the cube."""
    global ball_pos, ball_vel

    # Half size of the cube
    half_size = CUBE_SIZE / 2 - BALL_RADIUS

    # Clamp ball position to cube boundaries
    ball_pos[0] = np.clip(ball_pos[0], -half_size, half_size)
    ball_pos[1] = np.clip(ball_pos[1], -half_size, half_size)
    ball_pos[2] = np.clip(ball_pos[2], -half_size, half_size)


def main():
    global ball_pos, ball_vel, pitch, yaw, roll, pitch_direction, yaw_direction, roll_direction
    global next_direction_change, kick_effect_time

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    toggle_rotation_direction()
                elif event.key == pygame.K_r:
                    # Reset ball position to center
                    ball_pos = np.array([0, 0, 0], dtype=float)
                    ball_vel = np.array([random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)],
                                        dtype=float)

        # Check if it's time for a random direction change
        current_time = time.time()
        if current_time >= next_direction_change:
            toggle_rotation_direction()

        # Clear screen
        screen.fill(BLACK)

        # Update rotation angles
        pitch += PITCH_SPEED * pitch_direction
        yaw += YAW_SPEED * yaw_direction
        roll += ROLL_SPEED * roll_direction

        # Get rotated and projected cube vertices
        rotated_vertices = get_rotated_vertices()
        projected_vertices = get_projected_vertices(rotated_vertices)

        # Calculate face depths for proper rendering order
        face_depths = calculate_face_depths(rotated_vertices)

        # Apply gravity in the rotated coordinate system
        # Rotate gravity vector according to cube orientation
        gravity_vector = np.array([0, GRAVITY, 0])  # Default gravity is along Y axis
        rot_x = rotation_matrix_x(pitch)
        rot_y = rotation_matrix_y(yaw)
        rot_z = rotation_matrix_z(roll)
        rotated_gravity = rotate_point(gravity_vector, [rot_z, rot_y, rot_x])  # Apply in reverse order

        # Update ball velocity with rotated gravity
        ball_vel += rotated_gravity

        # Update ball position
        ball_pos += ball_vel

        # Check for collision with cube
        check_cube_collision()

        # Enforce boundary to keep ball inside
        enforce_boundary()

        # Draw cube
        draw_cube(projected_vertices, face_depths)

        # Project ball to 2D and draw
        projected_ball_pos, projected_radius = project_ball(ball_pos)

        # Draw ball with kick effect
        ball_color = RED
        if kick_effect_time > 0:
            # Flash yellow when kicked
            ball_color = YELLOW
            kick_effect_time -= 1

        pygame.draw.circle(screen, ball_color, (int(projected_ball_pos[0]), int(projected_ball_pos[1])),
                           projected_radius)

        # Calculate current metrics
        elapsed_time = current_time - start_time
        time_since_direction_change = current_time - last_direction_change_time
        velocity_magnitude = np.linalg.norm(ball_vel)

        # Display text information
        text_lines = [
            f"Pitch: {math.degrees(pitch):.1f}° ({pitch_direction})",
            f"Yaw: {math.degrees(yaw):.1f}° ({yaw_direction})",
            f"Roll: {math.degrees(roll):.1f}° ({roll_direction})",
            f"Ball Velocity: {velocity_magnitude:.2f}",
            f"Bounce Angle: {bounce_angle:.1f}°",
            f"Last Face Hit: {last_face_hit}",
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
