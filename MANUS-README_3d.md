# 3D Cube Ball Bounce Simulation - README

This Python program simulates a ball bouncing inside a 3D cube with realistic physics, including gravity, friction, and random kicks.

## Requirements
- Python 3.x
- Pygame library

## Installation
```
pip install pygame
```

## How to Run
```
python bouncing_ball_3d.py
```

## Controls
- Press ESC to exit the simulation
- Press SPACE to manually toggle a rotation direction
- Press R to reset the ball to the center position

## Features
- Full 3D simulation with perspective projection
- Ball bounces realistically off all six faces of the cube
- Depth perception - the ball appears smaller when further away
- 3D rotation with pitch, yaw, and roll (all three axes)
- Random rotation direction changes
- Semi-transparent cube faces with proper depth sorting
- Gravity that rotates with the cube
- Random kicks applied when the ball hits any face
- Visual kick effects when the ball bounces
- Real-time display of 3D metrics in the upper left corner:
  - Pitch, Yaw, and Roll angles with direction indicators
  - Ball Velocity
  - Bounce Angle
  - Last Face Hit
  - Total Time
  - Direction Change Time
  - Last Kick information

## How It Works
1. The cube rotates in 3D space with independent pitch, yaw, and roll rotations
2. The ball moves in 3D space under the influence of gravity (which rotates with the cube)
3. When the ball collides with a cube face:
   - The collision is detected in 3D space
   - The ball's velocity is reflected across the face normal
   - Friction is applied to reduce the ball's energy
   - A random 3D kick is applied
   - Visual effects show the collision
4. The 3D scene is projected onto the 2D screen using perspective projection
5. Faces are drawn with proper depth ordering (painter's algorithm)
6. The ball size changes based on its depth to enhance 3D perception

## 3D Techniques Used
- Rotation matrices for 3D transformations
- Perspective projection for 3D to 2D conversion
- Painter's algorithm for proper depth rendering
- Semi-transparent faces for better visibility
- Depth-based scaling for size perception
- 3D collision detection and response

## Code Structure
- `rotation_matrix_x/y/z()`: Create rotation matrices for each axis
- `project_3d_to_2d()`: Project 3D points to 2D screen coordinates
- `rotate_point()`: Apply rotation matrices to 3D points
- `get_rotated_vertices()`: Calculate rotated cube vertices
- `get_projected_vertices()`: Project rotated vertices to 2D
- `calculate_face_depths()`: Determine rendering order
- `draw_cube()`: Render the cube with proper depth sorting
- `project_ball()`: Project the 3D ball with depth-based scaling
- `check_cube_collision()`: Detect and handle 3D collisions
- `apply_collision_response()`: Handle physics of bouncing
- `apply_random_kick()`: Apply random 3D force vector
- `toggle_rotation_direction()`: Change rotation directions
- `enforce_boundary()`: Ensure ball stays inside cube
