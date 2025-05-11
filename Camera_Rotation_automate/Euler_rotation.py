import bpy
import math
import time
from mathutils import Vector

# Set the number of steps and pause intervals
num_steps = 360
pause_interval = num_steps // 20

# Get the camera object you want to rotate
camera_obj = bpy.data.objects.get("Camera")  # Replace with your camera's name

# Set the object you want to rotate the camera around
target_object = bpy.data.objects.get("Adapter_Box")  # Replace with your object's name

# Specify the radius for the camera rotation
radius = 2.0  # Adjust this value as needed

# Check if the camera and target object exist
if camera_obj is not None and target_object is not None:
    # Set the rotation step
    rotation_step = 2 * math.pi / num_steps

    # Add a Track To constraint to make the camera always face the target object
    track_to_constraint = camera_obj.constraints.new(type='TRACK_TO')
    track_to_constraint.target = target_object
    track_to_constraint.track_axis = 'TRACK_NEGATIVE_Z'

    # Rotate the camera around the object
    for i in range(num_steps + 1):
        bpy.context.view_layer.update()

        # Print camera parameters at specified intervals
        if i % pause_interval == 0:
            print(f"Step {i}:")
            print("Location:", camera_obj.location)
            print("Rotation:", camera_obj.rotation_euler)
            print("")

        # Calculate new camera location with a specified radius
        angle = rotation_step * i
        camera_location = target_object.location + Vector((radius * math.cos(angle), radius * math.sin(angle), 0))

        # Set the camera location
        camera_obj.location = camera_location
        camera_obj.keyframe_insert(data_path="location", frame=i)  # Optionally, add keyframes for animation

        # Pause to view the animation
        time.sleep(0.1)

else:
    print("Camera or target object not found.")

