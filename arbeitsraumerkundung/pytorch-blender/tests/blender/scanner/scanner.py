import range_scanner
import bpy

def scan_kinectv2():
    range_scanner.ui.user_interface.scan_static(
        bpy.context, 

        scannerObject=bpy.context.scene.objects["Camera"],

        resolutionX=512, fovX=70, resolutionY=424, fovY=60, resolutionPercentage=100,

        reflectivityLower=0.0, distanceLower=0.50, reflectivityUpper=0.0, distanceUpper=4.5, maxReflectionDepth=10,
        
        enableAnimation=False, frameStart=1, frameEnd=5, frameStep=1, frameRate=24,

        addNoise=False, noiseType='gaussian', mu=0.0, sigma=0.01, noiseAbsoluteOffset=0.0, noiseRelativeOffset=0.0,

        simulateRain=False, rainfallRate=0.0, 

        addMesh=True,

        exportLAS=False, exportHDF=True, exportCSV=False, exportSingleFrames=False,
        exportRenderedImage=True, exportSegmentedImage=False, exportPascalVoc=False, exportDepthmap=False, depthMinDistance=0.0, depthMaxDistance=100.0, 
        dataFilePath="/home/vinayaka/arbeitsraumerkundung/outputs", dataFileName="pcl",
        
        debugLines=False, debugOutput=False, outputProgress=True, measureTime=False, singleRay=False, destinationObject=None, targetObject=None
    )    
