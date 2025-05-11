import numpy as np
import os
from pathlib import Path

def appendData(handle, attribute, data):
    # see: https://stackoverflow.com/a/47074545/13440564

    # add a new line
    handle[attribute].resize((handle[attribute].shape[0] + 1), axis = 0)
    
    # write data at the end
    handle[attribute][-1] = data

def export(filePath, fileName, data, exportNoiseData):
    print("Exporting data into .np format...") 

    # in contrast to the other export methods, we only have ONE
    # file to export all data
    filePath = os.path.join(filePath, "%s.npy" % fileName)

    if exportNoiseData is False:
        np_array = np.column_stack((
                data[0], # label
                data[2], # x
                data[3], # y
                data[4], # z
                data[7], # red
                data[8], # green
                data[9], # blue
            )
        )
    else:
        np_array = np.column_stack((
                data[0], # label
                data[10], # x
                data[11], # y
                data[12], # z
                data[7], # red
                data[8], # green
                data[9], # blue
            )
        )

    np.save(filePath, np_array)

     
    print("Done.")
