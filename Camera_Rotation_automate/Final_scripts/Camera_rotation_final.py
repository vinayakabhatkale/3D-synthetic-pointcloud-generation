import bpy
import math
import mathutils

# Parameters
total_frames = 20
radius = 2.0
height = 2.0

# Get the camera object by its name (replace 'Camera' with your camera's name)
camera = bpy.data.objects['Camera']

# Clear all existing keyframes
camera.animation_data_clear()

# Set the camera's field of view (FOV)
bpy.data.cameras[camera.data.name].angle = math.radians(60)  # Set the desired FOV angle

# Add a "Track To" constraint to make the camera always look at the origin
target = bpy.data.objects.new("Target", None)
bpy.context.collection.objects.link(target)
target.location = (0, 0, 0)
track_to_constraint = camera.constraints.new(type='TRACK_TO')
track_to_constraint.target = target
track_to_constraint.track_axis = 'TRACK_NEGATIVE_Z'

# Iterate through frames
for frame in range(1, total_frames + 1):
    # Calculate the angle for rotation around the Z-axis
    angle = (2 * math.pi * frame) / total_frames
    
    # Calculate the camera's new position
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = height
    
    # Set the camera's location
    camera.location = mathutils.Vector((x, y, z))
    
    # Keyframe the camera's location
    camera.keyframe_insert(data_path="location", frame=frame)

    # Print the camera's location for this frame
    print(f"Frame {frame}:")
    print("Location:", camera.location)

# Update the scene to reflect the changes
bpy.context.view_layer.update()

