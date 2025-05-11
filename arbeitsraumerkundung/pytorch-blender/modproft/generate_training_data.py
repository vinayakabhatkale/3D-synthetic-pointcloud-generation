from blendtorch import btb
import numpy as np
import bpy
from datetime import datetime
import itertools

from blendtorch.btb.CollisionUtility import CollisionUtility 
from blendtorch.btb.MeshObjectUtility import convert_to_meshes

import copy
import argparse
import json

# if using vs code debugger
#import debugpy
#debugpy.listen(5678)
#debugpy.wait_for_client()

def init_animation_controller(anim_methods: btb.AnimationMethods, pub: btb.DataPublisher):
    anim = btb.AnimationController()
    anim.pre_play.add(anim_methods.pre_play, anim)
    anim.pre_animation.add(anim_methods.pre_animation, anim)
    anim.pre_frame.add(anim_methods.pre_frame, anim)
    anim.post_frame.add(anim_methods.post_frame, anim, pub)
    anim.post_animation.add(anim_methods.post_animation, anim)
#    anim.post_play.add(anim_methods.post_play, anim, pub)
    return anim

def evaluate_scene(filepath: str, pub: btb.DataPublisher, object_json_path: str=None, texture_img_src: str=None, defaults: dict=None):
    bpy.ops.wm.open_mainfile(filepath=filepath)
    print(end="\n\n")
    print(f'Opening {filepath}')
    anim_methods = btb.AnimationMethods(verbose=True, number_random_actions=0, 
            object_json_path=object_json_path, add_noise=False, publish=True, use_camera_frame=True, defaults=defaults)

    anim = init_animation_controller(anim_methods=anim_methods, pub=pub)
    anim.play(frame_range=(1,30), num_episodes=2, use_animation=not bpy.app.background)

def main():
    btargs, remainder = btb.parse_blendtorch_args()
    with open(btargs.scenes, "r") as f:
        data = json.load(f)

    with open(btargs.defaults, "r") as f:
        defaults = json.load(f)

    pub = btb.DataPublisher(btargs.btsockets['DATA'], btargs.btid, lingerms=10000)
    for item in data['scenes']:
        evaluate_scene(filepath=item['blender_scene'], pub=pub, object_json_path=item['objects'], defaults=defaults)

# entry point
if __name__ == '__main__':
    main()
