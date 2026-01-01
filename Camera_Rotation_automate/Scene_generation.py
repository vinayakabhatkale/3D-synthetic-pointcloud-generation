import bpy
import bpy
import random

# Define a list of object names that you want to swap
objects_to_swap = ["AdapterboxCAD", "Tablar", "Tablar.001", "Tablar.002", "Adapter_Box"]

# Define the directory where you want to save the new .blend files
directory_path = '/home/vinayaka/3dfiles/ModProFT_scene'



# Set the number of iterations
iterations = 5


import bpy

# Define a list of object names that you want to swap
objects_to_swap = ["AdapterboxCAD", "Tablar", "Tablar.001", "Tablar.002", "Adapter_Box"]

## Create a dictionary to store the original positions and rotations
original_positions = {}
original_rotations = {}

# Store the original positions and rotations of each object
for obj_name in objects_to_swap:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        original_positions[obj_name] = obj.location.copy()
        original_rotations[obj_name] = obj.rotation_euler.copy()

# Swap the positions of the specified objects while preserving rotation
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











'''
# Define the offset values
offset_x = 0.05  # Adjust the offset values as needed
offset_y = 0.0
offset_z = 0.0

# Function to swap two objects in the scene with an offset
def swap_objects_with_offset(offset_x, offset_y, offset_z):
    for i in range(len(objects_to_swap)):
        current_obj_name = objects_to_swap[i]
        next_obj_name = objects_to_swap[(i + 1) % len(objects_to_swap)]  # Wrap around to the first object at the end

        current_obj = bpy.data.objects.get(current_obj_name)
        next_obj = bpy.data.objects.get(next_obj_name)

        if current_obj and next_obj:
            # Swap positions with offset
            temp_location = current_obj.location.copy()
            current_obj.location = next_obj.location + bpy.mathutils.Vector((offset_x, offset_y, offset_z))
            next_obj.location = temp_location + bpy.mathutils.Vector((-offset_x, -offset_y, -offset_z))

# Perform swapping and export in each iteration
for iteration in range(1, iterations + 1):
    bpy.ops.wm.save_as_mainfile(filepath=f"{directory_path}swapped_scene_{iteration}.blend")
    swap_objects_with_offset(offset_x, offset_y, offset_z)

'''
