import bpy
from blendtorch.btb.SceneObject import SceneObject

class BlenderCam(SceneObject):
    def __init__(self, name: str, rotation_enabled: bool=None, translation_enabled: bool=None, trans_min: list=None, trans_max: list=None, trans_dim_enabled: str=None, 
            rot_min: list=None, rot_max: list=None, rot_dim_enabled: str=None, remember_orig_values: bool=None, list_cam_pos: list=None):
        super().__init__(name=name, remember_orig_values=remember_orig_values, 
                trans_min=trans_min, trans_max=trans_max, trans_dim_enabled=trans_dim_enabled,
                rot_min=rot_min, rot_max=rot_max, rot_dim_enabled=rot_dim_enabled, rotation_enabled=rotation_enabled, translation_enabled=translation_enabled)

        self._action_fns = []

        self.defined_cam_positions = False
        if list_cam_pos is not None:
            self.list_cam_pos = list_cam_pos
            self.iterator = None
            self.defined_cam_positions = True

        if self.defined_cam_positions is True:
            self._action_fns.append(self.next_cam_pos)
        else:
            if self.translation_enabled:
                self._action_fns.append(self.adjust_position)
            if self.rotation_enabled:
                self._action_fns.append(self.adjust_orientation)

    def reload_quaternions(self):
        obj = bpy.data.objects[self.name]
        if not obj.rotation_mode == 'QUATERNION':
            mode = obj.rotation_mode
            obj.rotation_mode = "QUATERNION"
        self.rotation_quaternion = obj.rotation_quaternion
        obj.rotation_mode = mode

    def next_cam_pos(self):
        """
            if new camera position in the list is available the pose will be adjusted
            return True is new pose was applied otherwise False
        """
        if self.iterator is None:
            self.iterator = iter(self.list_cam_pos)
        try:
            new_pos = next(self.iterator)
            success = True
            self.adjust_position(new_pos=new_pos[:3], adapt_new_pos=True)
            self.adjust_orientation(new_orientation=new_pos[3:], adapt_new_orientation=True)
            self.reload_quaternions()
            
        except Exception as e:
            print(e)
            success = False
            self.iterator = None

        return success
       
