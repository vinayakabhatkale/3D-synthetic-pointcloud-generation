class BlenderObject:
    def __init__(self, rotation_enabled: bool=None, translation_enabled: bool=None, scaling_enabled: bool=None):
        # set default values for parameters
        self.rotation_enabled = rotation_enabled if rotation_enabled is not None else True 
        self.translation_enabled = translation_enabled if translation_enabled is not None else True
        self.scaling_enabled = scaling_enabled if scaling_enabled is not None else True
        self.rotation_euler = None
        self.rotation_quaternion = None
        self.scale = None
        self.location = None

    def __str__(self):
        return f'Object enabled for: rotation {self.rotation_enabled}, translation {self.translation_enabled}, scaling {self.scaling_enabled}'

    def __repr__(self):
        return f'Object enabled for: rotation {self.rotation_enabled}, translation {self.translation_enabled}, scaling {self.scaling_enabled}'
