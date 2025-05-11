from blendtorch.btb.scanner import Scanner
from blendtorch.btb.BlenderObject import BlenderObject
from blendtorch.btb.CollisionUtility import CollisionUtility 
from blendtorch.btb.MeshObjectUtility import MeshObject, convert_to_meshes
from blendtorch.btb.BlenderCam import BlenderCam
from blendtorch.btb.BlenderLight import BlenderLight
from blendtorch.btb.ModifiableObject import ModifiableObject

import bpy
from datetime import datetime
import numpy as np
from collections import defaultdict
from functools import partial
import itertools
from mathutils import Vector

import random
import json
from typing import Tuple
import logging
logging.basicConfig(filename='/home/andi/arbeitsraumerkundung/synth_data_generation.log', level=logging.INFO)

import open3d as o3d

import matplotlib.pyplot as plt
import yaml

class AnimationMethods:
    def __init__(self, enable_light: bool=False, verbose: bool=False,
            number_random_actions: int=None, num_cam_pos: int=None, defaults: dict=None,
            object_json_path: str=None, add_noise: bool=True, snr: float=0.05, publish: bool=True, use_camera_frame: bool=True):
        """
            enable_light: enable random actions on lights in Blender scene
            number_random_actions: number of actions that are applied to the objects before new point cloud will be generated
            num_cam_pos: number of different camera positions for one scene
            defaults: defaults that apply to all scenes that will be randomized here
            object_json_path: file path of json file that describes the limits applied to the Blender Scene
            add_noise: True if noise should be added to the generated point cloud
            snr: signal to noise ratio
            use_camera_frame: bool to determine if the point cloud should be transformed into camera coordinates or stay in world coordinates
        """
        self.verbose = verbose
        self.enable_light = enable_light
        self.add_noise = add_noise
        self.use_noise_points = True if add_noise is True else False
        self.snr = snr
        self.enable_publish = publish
        self.use_camera_frame = use_camera_frame
        self.defaults = defaults

        self.scene_name = object_json_path.split('/')[-1].split('.')[0]

        # blender objects that are enabled/disabled for scaling/rotation/translation through file
        self._object_json_path = object_json_path
        if self._object_json_path is not None:
            self.bobjs = self.get_modifiable_objects(filename=object_json_path)
        else:
            self.bobjs = self.get_modifiable_objects()

        self.meshes = convert_to_meshes(bpy.data.objects)
        self.list_points_orig_pcl = list()

        if self.is_world_collision_free() is False:
            logging.info('Attention: Basic world already has collisions')

        ## number of objects that are randomly adapted before each frame
        self._number_random_actions = number_random_actions if number_random_actions is not None else 2

        # attributes that define how many camera positions for one scene are taken for generating point cloud
        self.__num_cam_pos = num_cam_pos if num_cam_pos is not None else 45 # number of different camera positions for one scene

        self.__new_scene_needed = False # if this is true objects in the world should be adapted
        self.__cam_pos_counter = 0
        self.__scanner = Scanner()

    def get_modifiable_objects(self, filename: str="./objects.json") -> dict:
        """
            get objects that are not or only partly used for randomization
            modifiable_objects is a defaultdict because in the file only the object with partly randomization are listed
            all other objects can be fully randomized, so other object keys that are used later from this dict are not limited in randomization
        """

        def str2bool(expr: str) -> bool:
            """
            /
                convert a string to bool
            """
            if expr is None:
                return None

            value = True if expr == "True" or expr == "true" else False
            return value

        def get_key_for_default_from_obj_name(obj_name: str) -> list:
            """
                get the key in defaults.json for a specific obj name, 
                e.g. obj_name is klt.0001 -> klt would be the key in the defaults.json file 
                we want this key as this gets us the default value in self.defaults
            """ 
            liste = [name for name in self.defaults.keys() if name in obj_name ]
            if len(liste) > 0:
                return liste[0]
            else:
                return None

        def get_default_value(obj: dict, key: str) -> str:
            """
                there are either default values for each scene for a group of objects or
                there are default values for objects in each scene
                the one specific to each scene have priority
            """
            if key in obj.keys():
                return obj[key]
            else:
                if 'name' in obj.keys():
                    # obj is dictionary read from json file
                    default_name = get_key_for_default_from_obj_name(obj['name'])
                else:
                    # obj is bpy object
                    default_name = get_key_for_default_from_obj_name(obj.name)

                if default_name is None:
                    raise Exception("JSON File and Blender File do not match")

                if key in self.defaults[default_name].keys():
                    return self.defaults[default_name][key]
                else:
                    return None

        # file that contains the limits for each individual scene
        with open(filename, 'r') as f:
            data = json.load(f)
            objects = data['objects']
            if 'cam_pos' in data.keys():
                cam_pos = data['cam_pos']
            else:
                cam_pos = None
            default_values = data['default_values']

        modifiable_objects = dict()
        modifiable_objects['objects'] = dict()
        modifiable_objects['lights'] = list()
        for obj in objects:

            # overall defaults
            key = get_key_for_default_from_obj_name(obj['name'])
            if key is not None:
                texture_img_src = self.defaults[key]['texture_img_src']
            else:
                texture_img_src = None

            modifiable_objects['objects'][obj['name']] = ModifiableObject(
                    name=obj['name'], 
                    translation_enabled = str2bool(get_default_value(obj, 'translation_enabled')),
                    rotation_enabled = str2bool(obj['rotation_enabled']) if 'rotation_enabled' in obj.keys() else None,
                    scaling_enabled = str2bool(obj['scaling_enabled']) if 'scaling_enabled' in obj.keys() else None, 
                    texture_enabled= str2bool(get_default_value(obj, "texture_enabled")),
                    scale_dim_enabled = obj['scale_dim_enabled'] if 'scale_dim_enabled' in obj.keys() else None,
                    trans_dim_enabled = obj['trans_dim_enabled'] if 'trans_dim_enabled' in obj.keys() else None,
                    rot_dim_enabled = obj['rot_dim_enabled'] if 'rot_dim_enabled' in obj.keys() else None, 
                    remember_orig_values = str2bool(obj['remember_orig_values']) if 'remember_orig_values' in obj.keys() else None, 
                    visibility_enabled = str2bool(obj['visibility_enabled']) if 'visibility_enabled' in obj.keys() else None, 
                    texture_img_src=texture_img_src,
                    verbose=self.verbose,
                    defaults=default_values
                    )

        for key, item in bpy.data.objects.items():
            if key in modifiable_objects['objects'].keys():
                # we processed that object already in the loop above
                continue
            if item.type == 'LIGHT':
                modifiable_objects['lights'].append(BlenderLight(name=key))
            elif item.type == 'CAMERA':
                # default: all dimensions for translation and rotation are allowed for camera
                list_cam_pos = self.parse_cam_pos(cam_pos)
                modifiable_objects['camera'] = BlenderCam(name = key, translation_enabled=False, rot_dim_enabled='YZ', list_cam_pos=list_cam_pos)
            elif item.type == 'MESH':
                # overall defaults
                default_key = get_key_for_default_from_obj_name(item.name)
                if default_key is not None:
                    texture_img_src = self.defaults[default_key]['texture_img_src']
                else:
                    texture_img_src = None

                modifiable_objects['objects'][key] = ModifiableObject(
                    name = key,
                    translation_enabled=str2bool(get_default_value(item, "translation_enabled")),
                    rotation_enabled=str2bool(get_default_value(item, "rotation_enabled")),
                    scaling_enabled=str2bool(get_default_value(item, "scaling_enabled")),
                    texture_enabled=str2bool(get_default_value(item, "texture_enabled")),
                    rot_dim_enabled=get_default_value(item, "rot_dim_enabled"), 
                    trans_dim_enabled=get_default_value(item, "trans_dim_enabled"), 
                    scale_dim_enabled=get_default_value(item, "scale_dim_enabled"), 
                    verbose=self.verbose, 
                    texture_img_src=texture_img_src,
                    defaults=default_values
                    )
            else:
                logging.info(f'Undefined Object type found in Scene {item.name}')

        return modifiable_objects

    def parse_cam_pos(self, data: list) -> list:
        """
            returns list of camera positions if in json file defined
            otherwise random camera positions relative to the current one in the blender scene will be applied
        """
        if data is None:
            self.random_cam_pos = True
            return None
        else:
            self.random_cam_pos = False

        list_cam_pos = list()
        for item in data:
            location = list(eval(item['location']))
            orientation = list(eval(item['orientation']))
            location.extend(orientation)
            list_cam_pos.append(np.array(location))

        return list_cam_pos

    def is_every_obj_in_env_modified(self):
        every_obj_modified = True
        for item in list(self.bobjs['objects'].values()):
            if item.is_already_modified() is False:
                every_obj_modified = False

        if self.verbose:
            outstr = 'Every obj in environment is modified'
            prefix = 'Not ' if every_obj_modified is False else ''
            #print(prefix + outstr)

        return every_obj_modified

    def reset_modified_state_of_objs(self):
        for item in list(self.bobjs['objects'].values()):
            item.reset_modified_state()


    def pre_play(self, anim):
        pass

    def pre_animation(self, anim):
        pass

    def pre_frame(self, anim):
        """
            before every frame some random actions should be applied to the contexts
        """

        cam = self.bobjs['camera']
        if self.__new_scene_needed is True:
            self.__new_scene_needed = False
            count = 0
            while count < self._number_random_actions:
                # choose item to randomly adapt
                key, item = random.choice(list(self.bobjs['objects'].items()))
                if item.is_already_modified() is True:
                    if self.is_every_obj_in_env_modified() is True:
                        self.reset_modified_state_of_objs()
                    continue
                if item.apply_random_action() is True:
                    count += 1
        else:
            if self.verbose:
                print('Adjusting camera pose')

            for light in self.bobjs['lights']:
                if self.enable_light:
                    light.apply_random_action()
                    if self.verbose:
                        print('Adjust lightning')
            cam.apply_random_action()

    def post_frame(self, anim, pub):
        """

        """
        now = datetime.now()
        #result = np.load('./result.npy').T
        result = self.__scanner.scan(path="/home/andi/arbeitsraumerkundung/outputs/training_data", export_hdf=True,export_np=True, export_rendered_img=False, export_single_frames=False, filename= now.strftime("%M:%S"), addNoise=self.add_noise)

        # if there is no point cloud we should make all objects visible again and maybe try 
        # to reset camera position
        if result is None:
            for key, item in self.bobjs['objects'].items():
                item.make_visible()
            cam = self.bobjs['camera']
            cam.reset_obj()
        else:
            result = result.T
            result[:, [0]]
            pcl = self.pcl_dict_from_scanning_result(result=result)
            
            
            if self.is_pcl_valid(pcl['label']) is False:
                dummy_pcl = dict()
                pub.publish(pcl=dummy_pcl)
                return
            
            if self.enable_publish:
                pub.publish(pcl=pcl)

            self.list_points_orig_pcl.append(pcl['label'].shape)

        self.__cam_pos_counter += 1
        if self.__cam_pos_counter > self.__num_cam_pos:
            self.__cam_pos_counter = 0
            self.__new_scene_needed = True

    def post_animation(self, anim):
        pass

    def post_play(self, anim, pub):        
        pass
    
        
    def is_pcl_valid(self, labels: np.ndarray) -> bool:
        values, counts = np.unique(labels, return_counts=True)
        percentages = counts / np.sum(counts)
        # for some reasons we get a tuple back here
        # we want to get the number of classes with too few points in the point cloud
        #num_classes_to_forget = np.where(percentages < 0.1)[0].shape[0]
        #num_classes = values.shape[0] - num_classes_to_forget
        num_classes = values.shape[0] 
        print(num_classes)
        print(values)
        if num_classes < 2:
            print('Removed point cloud due to not enough classes')
            return False
            

        if np.shape(labels)[0] < 20000:
            print('Removed point cloud because there are too few points')
            return False

        return True
       
      
    def point_cloud_to_camera_frame(self, pcl_dict: dict, cam_yaml_file: str='./camera_rotation.yml', used_cam: str='realsense') -> dict:
        """
            transform point cloud from world coordinate system to camera coordinate system

            pcl_dict: dict containing at least numpy arrays at key 'xyz' and 'rgb' with according values stored
            cam_yaml_file: str containing the file path to a yaml file that has the rotation from the camera mesh coordinate frame
            to the camera coordinate frame used from the real camera
            zivid: camera that is used in real life
            return: modified input dictionary containing the transformed point cloud
        """

        def quaternion_multiply(quaternion1, quaternion0):
            """
                https://stackoverflow.com/questions/39000758/how-to-multiply-two-quaternions-by-python-or-numpy
            """
            w0, x0, y0, z0 = quaternion0
            w1, x1, y1, z1 = quaternion1
            return np.array([-x1 * x0 - y1 * y0 - z1 * z0 + w1 * w0,
                             x1 * w0 + y1 * z0 - z1 * y0 + w1 * x0,
                             -x1 * z0 + y1 * w0 + z1 * x0 + w1 * y0,
                             x1 * y0 - y1 * x0 + z1 * w0 + w1 * z0], dtype=np.float64)

        with open(cam_yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        camera_data = data[used_cam]

        z_rot_quat = (camera_data['w'], camera_data['x'], camera_data['y'], camera_data['z'])


        pcl = o3d.geometry.PointCloud()
        pcl.points = o3d.utility.Vector3dVector(pcl_dict['xyz'])
        pcl.colors = o3d.utility.Vector3dVector(pcl_dict['rgb'])

        bcam = self.bobjs['camera']
        x,y,z = bcam.location

        T = np.eye(4)

        # translation
        T[0,3] = x
        T[1,3] = y
        T[2,3] = z

        origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=(0,0,0))
        cam = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=(0,0,0))
        
        # rotation 
        complete_quat = quaternion_multiply(bcam.rotation_quaternion, z_rot_quat)
        cam_rotation_matrix = o3d.geometry.TriangleMesh.get_rotation_matrix_from_quaternion(complete_quat)
        T[:3, :3] = cam_rotation_matrix

        # visualizing help        
        #cam.transform(T)

        # calculate the inverse transformation matrix
        # https://math.stackexchange.com/questions/152462/inverse-of-transformation-matrix
        T_inv = np.eye(4)
        rot_mat_inv = cam_rotation_matrix.transpose()

        T_inv[:3, :3] = rot_mat_inv
        translation_inv = np.matmul(-1 * T_inv[:3,:3], T[:3,3])
        T_inv[:3,3] = translation_inv

        # transform point cloud
        pcl.transform(T_inv)

        # visualizing help
        #o3d.visualization.draw_geometries([origin, pcl])

        pcl_dict['xyz'] = np.asarray(pcl.points)
        pcl_dict['rgb'] = np.asarray(pcl.colors)

        return pcl_dict

    def get_instance_labels_from_class(self, labels: np.ndarray, class_for_instance: int):
        instance_labels_idxs = np.where(labels[:,0] == class_for_instance)[0]
        instances = np.unique(labels[:, 1][instance_labels_idxs])
        points = None
        idxs_to_keep = list()
        for idx, instance in enumerate(instances):
            idx_current_instance = np.where(labels[:,1] == instance)[0]
            idxs_to_keep.extend(idx_current_instance.tolist())
            labels[:,1][idx_current_instance] = idx
        
        return labels, idxs_to_keep

    def pcl_dict_from_scanning_result(self, result: np.ndarray, instance_seg: bool=False, class_label: int=1) -> dict:
        """generate a dictionary containing the necessary information from the scanned point cloud

        Args:
            result (np.ndarray): array containing the result
            instance_seg (bool, optional): true if data should be used for instance segmentation network. Defaults to True.
            class_label (int, optional): class that is used for instance segmentation. Currently only instance segmentation
            for one class is supported. Defaults to 1. explanation of the indices: https://github.com/ln-12/blainder-range-scanner/blob/main/range_scanner/export/exporter.py

        Returns:
            dict: dict containing only semantic or instance segmentation labeled point cloud
        """

        pcl = dict()
        if instance_seg is True:
            result[:, [0,1]], idxs_to_keep = self.get_instance_labels_from_class(result[:,[0,1]], class_for_instance=class_label)
            result = result[idxs_to_keep]
            pcl['instance'] = result[:,[1]]
        pcl['label'] = result[:, [0]]
        if self.use_noise_points is True:
            pcl['xyz'] = result[:, [10, 11, 12]]
        else:
            pcl['xyz'] = result[:, [2, 3, 4]]
        pcl['rgb'] = result[:, [7, 8, 9]]
        #pcl['intensity'] = result[:, [6]]

        if self.add_noise and not self.use_noise_points:
            num_points = int(pcl['label'].shape[0])
            num_noise_points = int(self.snr * num_points)
            print(f'Type of num_points {num_points}, type num_noise_points {num_noise_points}')
            point_idxs = random.sample(range(0, num_points), num_noise_points)
            # x,y,z of the noise values
            noise = result[:, [10, 11, 12]]
            pcl['xyz'][point_idxs] = noise[point_idxs]
            print(f'Inserted {num_noise_points} points to original point cloud with {num_points} points')

        if self.use_camera_frame:
            pcl = self.point_cloud_to_camera_frame(pcl)
        return pcl


    def make_all_objs_visible(self):
        """
            make every object in the environment visible again
        """
        for key, item in self.bobjs['objects'].items():
            item.make_visible()

    def is_world_collision_free(self):
        """
           checks if there is any collision in the bpy context
           if no collision is found True is returned, False otherwise
        """
        combinations = list(itertools.combinations(self.meshes, 2))
        for obj1, obj2 in combinations:
            if obj1.get_type() != 'MESH' or obj2.get_type() != 'MESH':
                continue
            no_collision = CollisionUtility.check_intersections(obj1, None, [obj2], [])
            if no_collision is False:
                print(f'Collision found between {obj1.get_name()} and {obj2.get_name()}')
                # if there is any collision we should stop
                break
        return no_collision

    
