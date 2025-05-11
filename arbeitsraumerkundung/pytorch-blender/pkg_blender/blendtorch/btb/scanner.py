import range_scanner
import bpy
import yaml

class Scanner:
    def __init__(self, path_to_presets: str='/home/andi/.config/blender/2.93/scripts/addons/range_scanner/ui/presets.yaml', cam_type: str='realsense'):
        with open(path_to_presets, "r") as f:
            try:
                data = yaml.safe_load(f)
                for cam_dict in data:
                    if cam_type in cam_dict.values():
                        self.resolutionX = cam_dict['resolutionX']
                        self.resolutionY = cam_dict['resolutionY']
                        self.fovX = cam_dict['fovX']
                        self.fovY = cam_dict['fovY']
                        self.reflectivityLower= cam_dict['reflectivityLower']
                        self.reflectivityUpper= cam_dict['reflectivityUpper']
                        self.distanceLower = cam_dict['distanceLower']
                        self.distanceUpper = cam_dict['distanceUpper']
                        self.resolutionPercentage = cam_dict['resolutionPercentage']

            except yaml.YAMLError as exc:
                print(exc)

    def scan(self, export_rendered_img: bool=False, export_np: bool=	True, export_seg_img: bool=False, export_hdf: bool=False,
            export_csv: bool=False, path: str="/home/andi/arbeitsraumerkundung/outputs", filename: str="pcl", 
            export_single_frames: bool=False, addNoise: bool=False):
        result = range_scanner.ui.user_interface.scan_static(
            bpy.context, 

            scannerObject=bpy.context.scene.objects["Camera"],

            resolutionX=self.resolutionX, fovX=self.fovX, resolutionY=self.resolutionY, fovY=self.fovY, resolutionPercentage=self.resolutionPercentage,

            reflectivityLower=self.reflectivityLower, distanceLower=self.distanceLower, reflectivityUpper=self.reflectivityUpper, distanceUpper=self.distanceUpper, maxReflectionDepth=10,
            
            enableAnimation=False, frameStart=1, frameEnd=5, frameStep=1, frameRate=24,

            addNoise=addNoise, noiseType='gaussian', mu=0.0, sigma=0.01, noiseAbsoluteOffset=0.0, noiseRelativeOffset=0.0,

            simulateRain=False, rainfallRate=0.0, 

            addMesh=False,

            exportLAS=False, exportHDF=export_hdf, exportCSV=export_csv, exportNPY=export_np, exportSingleFrames=export_single_frames,
            exportRenderedImage=export_rendered_img, exportSegmentedImage=export_seg_img, exportPascalVoc=False, exportDepthmap=False, 
            depthMinDistance=0.0, depthMaxDistance=100.0, dataFilePath=path, dataFileName=filename,
            
            debugLines=False, debugOutput=False, outputProgress=True, measureTime=False, singleRay=False, destinationObject=None, targetObject=None

            )
        return result

