import bpy
import math
import mathutils
import json

# Parameters
total_frames = 60
radius = 1.5
height = 2

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

# Initialize a list to store camera positions and orientations
cam_pos_list = []

# Initialize the default_values dictionary
default_values = {
    "Tablar": {
        "trans_max": "0.01,0.01,0.01",
        "trans_min": "-0.01,-0.01,-0.01"
    },
    "Adapter_Box": {
        "scale_dim_enabled": "XY",
        "rot_dim_enabled": "Z",
        "remember_orig_values": "True",
        "visibility_enabled": "False"
    }
}

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

    # Calculate the rotation to make the camera look at the origin
    camera_direction = -camera.location  # Negative of the camera's location vector
    camera_rotation = camera_direction.to_track_quat('Z', 'Y').to_euler()
    
    # Format camera location and orientation as strings
    formatted_location = f"{x:.5f},{y:.5f},{z:.5f}"
    formatted_orientation = f"{camera_rotation.x:.5f},{camera_rotation.y:.5f},{camera_rotation.z:.5f}"
    
    # Append the camera position and orientation to the list
    cam_pos_list.append({
        "location": formatted_location,
        "orientation": formatted_orientation
    })

    # Print the camera's location for this frame
    print(f"Frame {frame}:")
    print("Location:", camera.location)

# Create a dictionary for the JSON structure
json_data = {
    "objects": [
        {
            "name": "Table",
            "visibility_enabled": "False"
        }
    ],
    "cam_pos": cam_pos_list,
    "default_values": default_values
}

# Write the JSON data to a file
with open("/home/andi/arbeitsraumerkundung/pytorch-blender/kiraf/scene1.json", "w+") as json_file:
    json.dump(json_data, json_file, indent=2)

# Update the scene to reflect the changes
bpy.context.view_layer.update()

