import enum
import re
from weakref import ref
import bpy
from blendtorch.btb.BlenderObject import BlenderObject
import numpy as np

import copy
import random
from typing import Any

class SceneObject(BlenderObject):
    def __init__(self, name, rotation_enabled: bool=None, translation_enabled: bool=None, scaling_enabled: bool=None, 
            remember_orig_values: bool=None, trans_min: list=None, trans_max: list=None, trans_dim_enabled: list=None, 
            rot_min: list=None, rot_max: list=None, rot_dim_enabled: list=None, defaults: dict=None, verbose: bool=False, default_key: str=None, debug: bool=False):

        super().__init__(rotation_enabled=rotation_enabled, translation_enabled=translation_enabled, scaling_enabled=scaling_enabled)

        self.debug = debug
        self.defaults = defaults
        self.name = name
        self.remember_orig_values = remember_orig_values if remember_orig_values is not None else True
        if self.remember_orig_values is True:
            self._store_orig_values()
        self._trans_min = self.set_constructor_value(given_value=trans_min, default_value=[-0.5, -0.5, -0.5], default_key=default_key, property_name='trans_min')
        self._trans_max = self.set_constructor_value(given_value=trans_max, default_value=[0.5, 0.5, 0.5], default_key=default_key, property_name='trans_max')
        self._trans_dim_enabled = self.set_constructor_value(given_value=trans_dim_enabled, default_value='XZ', default_key=default_key, property_name='trans_dim_enabled')
        self._rot_min = self.set_constructor_value(given_value=rot_min, default_value=[-0.5, -0.5, -0.2], default_key=default_key, property_name='rot_min')
        self._rot_max = self.set_constructor_value(given_value=rot_max, default_value=[0.5, 0.5, 0.2], default_key=default_key, property_name='rot_max')
        self._rot_dim_enabled = self.set_constructor_value(given_value=rot_dim_enabled, default_value='Z', default_key=default_key, property_name='rot_dim_enabled')

        self.verbose = verbose

        self._action_fns = [self.adjust_position, self.adjust_orientation]

        self._already_modified = False

    def set_constructor_value(self, given_value: Any, default_value: Any, property_name: str, default_key: str):
        """
            given_value:    value explicitely set for this object
            default_value:  default_value that is written hardcoded in the python script that only will be used if no default value for this class of 
                            objects  is defined by user in json file
            
            property_name:  name of attribute that will be set, e.g. trans_min, trans_max, scale_dim_enabled
            default_key:    key for dict defaults (given to constructor, defines the class of objects, e.g. klt or storage_rack
        """
        if not given_value is None:
            if self.debug:
                print('Setting given value')

            return given_value
        elif default_key is None:
            return default_value
        elif property_name in self.defaults[default_key]:
            if self.debug:
                print('Setting default property')
            try:
                return eval(self.defaults[default_key][property_name])
            except:
                return self.defaults[default_key][property_name]

        elif not default_value is None:
            return default_value

        else:
            return None

    def reset_modified_state(self):
        self._already_modified = False

    def _store_orig_values(self):
        item = bpy.data.objects[self.name]
        self.rotation_euler = copy.deepcopy(item.rotation_euler)
        self.rotation_quaternion = item.rotation_quaternion
        self.scale = copy.deepcopy(item.scale)
        self.location = copy.deepcopy(item.location)

    def reset_obj(self):
        item = bpy.data.objects[self.name]
        item.rotation_euler = self.rotation_euler
        item.scale = self.scale
        item.location = self.location

    def random_int(self, a: int=0, b: int=256) -> float:
        """
            returns a random int number in interval [a,b]
            default interval is [0., 1.]
        """
        # unexpected case
        if a > b:
            a,b = b,a
            print('Warning, a should be smaller than b, switched values a, b')

        x = np.random.randint(a, b)
        return x

    def random_float(self, a: float=0., b: float=1.) -> float:
        """
            returns a float random number in interval [a,b]
            default interval is [0., 1.]
        """
        # unexpected case
        if a > b:
            a,b = b,a
            print('Warning, a should be smaller than b, switched values a, b')

        x = (b-a) * np.random.random_sample() + a
        return x

    def adapt_value_randomly(self, ref_point: float, min: float, max: float) -> float:
        return ref_point + self.random_float(min, max)

    def adjust_position(self, new_pos: np.ndarray=None, adapt_new_pos: bool=False) -> None:
        """
            adjust position of object 
            limits are given by self._trans_min and self._trans_max
            In which dimensions the object is allowed to be translated is defined by self._trans_dim_enabled
            
        """
        obj = bpy.data.objects[self.name]
        if new_pos is None:
            for idx, c in enumerate('XYZ'):
                if c in self._trans_dim_enabled:
                    if self.remember_orig_values is True:
                        ref_point = self.location[idx]
                    else:
                        ref_point = obj.location[idx]
                    new_value = self.adapt_value_randomly(ref_point=ref_point, min=self._trans_min[idx], max=self._trans_max[idx])
                    obj.location[idx] = new_value
                    if self.verbose:
                        print(f'Adapt {self.name} position in {c}-direction to {new_value}')
        else:
            if adapt_new_pos is True:
                for idx, c in enumerate('XYZ'):
                    new_value = self.adapt_value_randomly(ref_point=new_pos[idx], min=self._trans_min[idx], max=self._trans_max[idx])
                    obj.location[idx] = new_value
            else:
                obj.location = new_pos


    def adjust_orientation(self, new_orientation: np.ndarray=None, adapt_new_orientation: bool=False) -> None:
        """
            adjust orientation of object 
            limits are given by self._rot_min and self._rot_max
            In which dimensions the object is allowed to be rotated is defined by self._rot_dim_enabled
        """       
        obj = bpy.data.objects[self.name]
        if new_orientation is None:
            for idx, c in enumerate(obj.rotation_mode):
                if c in self._rot_dim_enabled:
                    if self.remember_orig_values is True:
                        ref_point = self.rotation_euler[idx]
                    else:
                        ref_point = obj.rotation_euler[idx]
                    new_value = ref_point + self.random_float(self._trans_min[idx], self._trans_max[idx])
                    obj.rotation_euler[idx] = new_value
                    if self.verbose:
                        print(f'Adapt {self.name} orientation in {c}-direction to {new_value}')
        else:
            if adapt_new_orientation is True:
                for idx, c in enumerate('XYZ'):
                    new_value = self.adapt_value_randomly(ref_point=new_orientation[idx], min=self._rot_min[idx], max=self._rot_max[idx])
                    obj.rotation_euler[idx] = new_value
            else:
                obj.rotation_euler = new_orientation

    def apply_random_action(self):
        if len(self._action_fns) > 1:
            action_fn = random.choice(self._action_fns)
        else:
            action_fn = self._action_fns[0]
        self._already_modified = True
        return action_fn()

    def is_already_modified(self):
        return self._already_modified
