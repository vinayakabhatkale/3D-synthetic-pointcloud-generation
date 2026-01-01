import bpy
from blendtorch.btb.SceneObject import SceneObject

class BlenderLight(SceneObject):
    def __init__(self, name: str, trans_min: list=None, trans_max: list=None, trans_dim_enabled: str=None, 
            rot_min: list=None, rot_max: list=None, rot_dim_enabled: str=None, remember_orig_values: bool=None, 
            energy_min: float=None, energy_max: float=None, dist_min: float=None, dist_max: float=None, verbose: bool=None):
        super().__init__(name=name, remember_orig_values=remember_orig_values, 
                trans_min=trans_min, trans_max=trans_max, trans_dim_enabled=trans_dim_enabled,
                rot_min=rot_min, rot_max=rot_max, rot_dim_enabled=rot_dim_enabled)

        self.action_fns = [self.adjust_position, self.adjust_lightning, self.adjust_light_type]
        self._energy_min = energy_min if energy_min is not None else 10.
        self._energy_max = energy_max if energy_max is not None else 1000.
        self._dist_min = dist_min if dist_min is not None else 20
        self._dist_max = dist_max if dist_max is not None else 200

    def adjust_lightning(self):
        """
            
        """
        if self.verbose:
            print(f'Adjust lightning for {self.name}')
        light = bpy.data.lights[self.name]

        # random color for lightning
        light.color = (
                self.random_float(0., 1.),
                self.random_float(0., 1.),
                self.random_float(0., 1.)
                )

        light.energy = self.random_float(self._energy_min, self._energy_max)
        light.distance = self.random_float(self._dist_min, self._dist_max)
        return True

    def adjust_light_type(self):
        if self.verbose:
            print(f'Adjust light type for {self.name}')
        # possible types of light sources https://docs.blender.org/api/current/bpy.ops.object.html?highlight=light_add#bpy.ops.object.light_add
        possible_types = ['POINT', 'SUN', 'SPOT', 'AREA']

        light = bpy.data.objects[self.name].data

        # don't choose the same lightning type as before
        possible_types.remove(light.type)

        # choose random light type
        light.type = possible_types[self.random_int(0, len(possible_types))]
        return True
