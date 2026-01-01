from typing import List, Union, Tuple, Optional

import bpy
import numpy as np
import bmesh
import mathutils
from mathutils import Vector, Matrix

from blendtorch.btb.EntityUtility import Entity

class MeshObject(Entity):

    def __init__(self, bpy_object: bpy.types.Object):
        super().__init__(bpy_object)

    def create_bvh_tree(self) -> mathutils.bvhtree.BVHTree:
        """ Builds a bvh tree based on the object's mesh.
        :return: The new bvh tree
        """
        bm = bmesh.new()
        bm.from_mesh(self.get_mesh())
        bm.transform(Matrix(self.get_local2world_mat()))
        bvh_tree = mathutils.bvhtree.BVHTree.FromBMesh(bm)
        bm.free()
        return bvh_tree

    def get_mesh(self) -> bpy.types.Mesh:
        """ Returns the blender mesh of the object.
        :return: The mesh.
        """
        return self.blender_obj.data

    def get_type(self):
        return self.blender_obj.type

    def get_bound_box(self, local_coords: bool = False) -> np.ndarray:
        """
        :return: 8x3 array describing the object aligned bounding box coordinates in world coordinates
        """
        if not local_coords:
            local2world = Matrix(self.get_local2world_mat())
            return np.array([local2world @ Vector(cord) for cord in self.blender_obj.bound_box])
        else:
            return np.array([Vector(cord) for cord in self.blender_obj.bound_box])

def convert_to_meshes(blender_objects: list) -> List["MeshObject"]:
    """ Converts the given list of blender objects to mesh objects
    :param blender_objects: List of blender objects.
    :return: The list of meshes.
    """
    return [MeshObject(obj) for obj in blender_objects]
