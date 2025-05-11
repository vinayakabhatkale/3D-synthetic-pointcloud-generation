import bpy
import math
import time
from mathutils import Vector

# Set the number of steps and pause intervals
num_steps = 360
pause_interval = num_steps // 20

# Get the camera object you want to rotate
camera_obj = bpy.data.objects.get("Camera")  # Replace with your camera's name

# Specify the radius for the camera rotation
radius = 1.5  # Adjust this value as needed

# Set the desired height for the camera
camera_height = 1.5  # Adjust this value as needed

# Check if the camera exists
if camera_obj is not None:
    # Set the rotation step
    rotation_step = 2 * math.pi / num_steps

    # Rotate the camera around the origin
    for i in range(num_steps + 1):
        bpy.context.view_layer.update()

        # Print camera parameters at specified intervals
        if i % pause_interval == 0:
            print(f"Step {i}:")
            print("Location:", camera_obj.location)
            print("Rotation:", camera_obj.rotation_euler)
            print("")

        # Calculate new camera location with a specified radius and height
        angle = rotation_step * i
        camera_location = Vector((radius * math.cos(angle), radius * math.sin(angle), camera_height))

        # Set the camera location
        camera_obj.location = camera_location
        camera_obj.keyframe_insert(data_path="location", frame=i)  # Optionally, add keyframes for animation

        # Calculate the rotation to make the camera look at the origin
        camera_direction = -camera_location  # Negative of the camera's location vector
        camera_rotation = camera_direction.to_track_quat('Z', 'Y').to_euler()
        camera_obj.rotation_euler = camera_rotation

        # Pause to view the animation
        time.sleep(0.1)

else:
    print("Camera not found.")

