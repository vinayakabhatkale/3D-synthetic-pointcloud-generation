from matplotlib.pyplot import text
import bpy
from blendtorch.btb.SceneObject import SceneObject
from blendtorch.btb.CollisionUtility import CollisionUtility 
from blendtorch.btb.MeshObjectUtility import MeshObject, convert_to_meshes
from typing import Any

import copy
from datetime import datetime
import os

class ModifiableObject(SceneObject):
    def __init__(self, name: str, trans_min: list=None, trans_max: list=None, trans_dim_enabled: str=None, 
            rot_min: list=None, rot_max: list=None, rot_dim_enabled: str=None, remember_orig_values: bool=None,
            rotation_enabled: bool=None, translation_enabled: bool=None, scaling_enabled: bool=None, 
            scale_min: list=None, scale_max: list=None, scale_dim_enabled: str=None, verbose: bool=False, debug: bool=False,
            material_enabled: bool=None, texture_enabled: bool=None, texture_img_src: str=None, visibility_enabled: bool=None,
            defaults: dict=None):
        
        if debug:
            print(f'\nObject {name}')

        default_key = None
        if not defaults is None:
            for key in defaults:
                if key in name:
                    default_key = key

        super().__init__(name=name, remember_orig_values=remember_orig_values, 
                trans_min=trans_min, trans_max=trans_max, trans_dim_enabled=trans_dim_enabled,
                rot_min=rot_min, rot_max=rot_max, rot_dim_enabled=rot_dim_enabled, rotation_enabled=rotation_enabled,
                translation_enabled=translation_enabled, scaling_enabled=scaling_enabled, verbose=verbose, defaults=defaults, default_key=default_key)

        # default values for scaling
        # -0.2 would mean that scaling of -20% of the current value could be applied
        self._scale_min = self.set_constructor_value(given_value=scale_min, default_value=[-0.2, -0.2, -0.2], property_name='scale_min', default_key=default_key)
        self._scale_max = self.set_constructor_value(given_value=scale_max, default_value=[0.2, 0.2, 0.2], property_name='scale_max', default_key=default_key)
        self._scale_dim_enabled = self.set_constructor_value(given_value=scale_dim_enabled, default_value='XYZ', property_name='scale_dim_enabled', default_key=default_key)

        self._material_enabled = self.set_constructor_value(given_value=material_enabled, default_value=True, property_name='material_enabled', default_key=default_key) 
        self._texture_enabled = self.set_constructor_value(given_value=texture_enabled, default_value=True, property_name='texture_enabled', default_key=default_key)
        self._visibility_enabled = self.set_constructor_value(given_value=visibility_enabled, default_value=True, property_name='visibility_enabled', default_key=default_key)

        if self._texture_enabled is True:
            if texture_img_src is None:
                self._texture_img_src = "/home/andi/dtd/labels/labels_joint_anno.txt" 
                print(f"Use complete dtd dataset for {self.name}")
            else:
                self._texture_img_src = texture_img_src

        #self._texture_enabled = True 
        self._material_enabled = False
        #self.rotation_enabled = False
        #self.scaling_enabled = False
        #self.translation_enabled= False
        self._visibility_enabled = False
        self._action_fns = []
        if self._material_enabled is True:
            self._action_fns.append(self.adjust_material)
        if self._texture_enabled is True:
            self._action_fns.append(self.adjust_texture)
        if self.rotation_enabled is True:
            self._action_fns.append(self.adjust_orientation)
        if self.translation_enabled is True:
            self._action_fns.append(self.adjust_position)
        if self.scaling_enabled is True:
            self._action_fns.append(self.adjust_scaling)
        if self._visibility_enabled is True:
            self._action_fns.append(self.toggle_visibility) 

        if len(self._action_fns) < 1:
            print(f'Warning for {self.name} there is no action fn defined')
        self.check_datatypes()


    def check_datatypes(self):
        assert type(self._material_enabled) == bool
        assert type(self._texture_enabled) == bool
        assert type(self.rotation_enabled) == bool
        assert type(self.translation_enabled) == bool
        assert type(self.scaling_enabled) == bool
        assert type(self._visibility_enabled) == bool
        assert type(self._rot_dim_enabled) == str
        assert type(self._scale_dim_enabled) == str
        assert type(self._trans_dim_enabled) == str
        assert type(self._trans_max) == list or type(self._trans_max) == tuple 
        assert type(self._trans_min) == list or type(self._trans_min) == tuple 
        assert type(self._trans_min) == list or type(self._trans_min) == tuple 
        assert type(self._rot_min) == list or type(self._rot_min) == tuple 
        assert type(self._rot_max) == list or type(self._rot_max) == tuple 
        assert type(self._scale_min) == list or type(self._scale_min) == tuple 
        assert type(self._scale_max) == list or type(self._scale_max) == tuple 
        
        
    def toggle_visibility(self):
        """
           toggle visibility for rendering/point cloud creation
        """
        item = bpy.data.objects[self.name]
        if self.verbose is True:
            print(f'Toggle visibility of {self.name} to {not item.hide_get()}')
        item.hide_set(not item.hide_get())
        return True

    def make_visible(self):
        """
            make object visible in blender context
        """
        item = bpy.data.objects[self.name]
        item.hide_set(False)

    def adjust_material(self):
        if self.verbose:
            print(f'Adjusting material for {self.name}')
        # get object from context
        item = bpy.data.objects[self.name]
        
        # generate unique material name
        now = datetime.now()
        new_material_name= now.strftime("%d/%m/%Y %H:%M:%S")

        new_mat = bpy.data.materials.new(name=str(hash(new_material_name)))

        # random color
        new_mat.diffuse_color = (
                self.random_float(0., 1.),
                self.random_float(0., 1.),
                self.random_float(0., 1.),
                1)

        # random specular intensity roughness and metallic surface
        new_mat.specular_intensity = self.random_float(0., 1.)
        new_mat.roughness = self.random_float(0., 1.)
        new_mat.metallic = self.random_float(0., 1.)

        # apply material to object
        item.active_material = new_mat
        return True                    

    def adjust_scaling(self):
        """
            adapt scaling of the object
            limited in dimensions with self._scale_dim_enabled
        """
        # get object from context
        item = bpy.data.objects[self.name]

        # store current value for scaling in case scaling leads to collision
        old_value = copy.deepcopy(item.scale)
        for idx, c in enumerate('XYZ'):
            # check if this dimension for scaling is allowed
            if c in self._scale_dim_enabled:
                if self.remember_orig_values is True:
                    rel_value = self.scale[idx]
                else:
                    rel_value = item.scale[idx]
                new_value = self.random_float(self._scale_min[idx], self._scale_max[idx]) * rel_value
                if self.verbose:
                    print(f'Scaling object {self.name} in {c} to {item.scale[idx] + new_value}')
                item.scale[idx] += new_value

        # collision checking
        no_collision = self.is_object_colliding(item)
        if no_collision is False:
            if self.verbose:
                print('Collision detected')
            # Reseting item location
            item.scale= old_value
            return False
        else:
            if self.verbose:
                print(f'Scaled {self.name}')
            return True

    def adjust_position(self):
        """
            uses base function for randomly adjusting position but this was expanded by collision detection
        """
        # get object from blender context
        item = bpy.data.objects[self.name]

        # store current value for location in case translation leads to collision
        old_value = copy.deepcopy(item.location)

        # call super function for applying random translation
        super().adjust_position()

        # collision checking
        no_collision = self.is_object_colliding(item)
        if no_collision is False:
            if self.verbose:
                print('Collision detected')
            # Reseting item location
            item.location= old_value
            return False
        else:
            if self.verbose:
                print(f'Translated {self.name}')
            return True

    def adjust_orientation(self):
        """
            uses base function for randomly adjusting position but this was expanded by collision detection
        """
        # get object from blender context
        item = bpy.data.objects[self.name]

        # store current value for rotation in case rotation leads to collision
        old_value = copy.deepcopy(item.rotation_euler)
        super().adjust_orientation()
        no_collision = self.is_object_colliding(item)
        if no_collision is False:
            if self.verbose:
                print('Collision detected')
            # Reseting item location
            item.rotation_euler = old_value
            return False
        else:
            if self.verbose:
                print(f'Rotated{self.name}')
            return True

    def get_random_img_texture(self, filepath: str, prefix: str='.', file_contains_labels: bool=True):
        """
            :param filepath leads to a file containing paths to image textures in every line
            :param prefix if there is a constant offset between file containing the paths
            :param file_contains_labels: if True only the first element of each line will be considered as path. Other strings are most likely labels

        """
        with open(filepath, 'r') as f:
            data = f.readlines()

        dirname = os.path.dirname(filepath)

        if file_contains_labels is True:
            line_content = data[self.random_int(0, len(data))]
            path_to_file = line_content.split(sep=" ")[0]
        else:
            path_to_file = data[self.random_int(0, len(data))]
        texture_path = os.path.join(dirname, prefix, path_to_file)
        
        return texture_path

    def adjust_texture(self):
        """
            adjust texture from images 
            source of the images is given to the constructor of this class
        """
        try:
            if self.verbose:
                print(f'Adjusting texture for {self.name}')

            # deselect all objects
            # this is an operation that is allowed to fail
            # if no object is selected this operation throws an exception even that is no real error
            try:
                bpy.ops.object.select_all(action="DESELECT")
            except:
                pass

            obj = bpy.data.objects[self.name]
            obj.select_set(True)

            bpy.ops.object.editmode_toggle()

            # select the geometry
            bpy.ops.mesh.select_all(action="SELECT")

            bpy.ops.uv.smart_project()

            now = datetime.now()
            new_material_name= now.strftime("%d/%m/%Y %H:%M:%S")

            mat = bpy.data.materials.new(name=new_material_name)
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new("ShaderNodeTexImage")
            # line that throws error
            texImage.image = bpy.data.images.load(self.get_random_img_texture(self._texture_img_src, prefix="../images"))
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

            if obj.data.materials:
                obj.data.materials[0] = mat
            else:
                obj.data.materials.append(mat)

            bpy.ops.object.editmode_toggle()
            return True
        except Exception as e:
            if self.verbose:
                print(f'Texture adjusting went wrong {str(e)}')



    def is_object_colliding(self, obj) -> bool:
        """
            check if given object is colliding with anything in the environment
        """
        mesh = MeshObject(obj)

        # get name of current object
        name = mesh.get_name()
        blender_objs = convert_to_meshes(bpy.data.objects)

        no_collision = True
        # iterate over all objects in blender context
        for coll_obj in blender_objs:
            # disable collision checking if self collision camera or light is the object
            if name == coll_obj.get_name() or coll_obj.get_type() == 'CAMERA' or coll_obj.get_type()== 'LIGHT':
                continue
            else:
                no_collision = CollisionUtility.check_intersections(mesh, None, [coll_obj], [])
                if no_collision is False:
                    if self.verbose:
                        print(f'Collision detected between {name} and {coll_obj.get_name()}')
                    break
        return no_collision

