import bpy
import os
import random
import datetime

# Define a list of object names that you want to swap
objects_to_swap = ["AdapterboxCAD", "Tablar", "Tablar.001", "Tablar.002", "Adapter_Box"]

# Create a directory to save the scenes
output_directory = "/home/andi/3dfiles/ModProFT_scene"  # Change this to the directory where you want to save the blend files

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Create a dictionary to store the original positions and rotations
original_positions = {}
original_rotations = {}

# Store the original positions and rotations of each object
for obj_name in objects_to_swap:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        original_positions[obj_name] = obj.location.copy()
        original_rotations[obj_name] = obj.rotation_euler.copy()

# Number of random configurations to generate
num_configurations = 10  # Change this to the desired number of configurations

for config_num in range(num_configurations):
    # Randomize the positions of the specified objects while preserving rotation
    for i in range(len(objects_to_swap)):
        current_obj_name = objects_to_swap[i]
        next_obj_name = objects_to_swap[(i + 1) % len(objects_to_swap)]  # Wrap around to the first object at the end

        current_obj = bpy.data.objects.get(current_obj_name)
        next_obj = bpy.data.objects.get(next_obj_name)

        if current_obj and next_obj:
            # Swap positions
            temp_location = current_obj.location.copy()
            current_obj.location = next_obj.location
            next_obj.location = temp_location

            # Preserve rotations
            current_obj.rotation_euler = original_rotations[next_obj_name]
            next_obj.rotation_euler = original_rotations[current_obj_name]

    # Save the scene as a new blend file
    scene_name = f"Randomized_Scene_{config_num + 1}"
    blend_file_path = os.path.join(output_directory, f"{scene_name}.blend")

    bpy.ops.wm.save_as_mainfile(filepath=blend_file_path)

# Restore the original positions and rotations
for obj_name in objects_to_swap:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.location = original_positions[obj_name]
        obj.rotation_euler = original_rotations[obj_name]

