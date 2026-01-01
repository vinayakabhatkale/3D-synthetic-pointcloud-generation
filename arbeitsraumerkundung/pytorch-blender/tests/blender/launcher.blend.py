from blendtorch import btb
from pprint import pprint
import bpy

def main():
    # Note, need to linger a bit in order to wait for unsent messages to be transmitted
    # before exiting blender.
    #scan_kinectv2()

    klt = bpy.data.objects['klt.001']
    klt.scale[2] = 3
    result = btb.scanner.scan_kinectv2(export_hdf=True)
    print(result.shape)
    btargs, remainder = btb.parse_blendtorch_args()
    #pub = btb.DataPublisher(btargs.btsockets['DATA'], btargs.btid, lingerms=10000)
    #pub.publish(btargs=vars(btargs), remainder=remainder)
main()
