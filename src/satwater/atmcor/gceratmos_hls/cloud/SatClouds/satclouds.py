# -*- mode: python -*- Rejane Paulino 06-05-2024

"""
SatClouds refers to processor to recover the cloud mask from satellite images based on fmask-algorithm (Landsat-8/9/OLI and Sentinel-2/MSI)
and quality flag file (Sentinel-3/OLCI). To run this package are requested:

*/ path_img: path with TOA-images in S3X_OL_1_EFR____*.SEN3, S2X_MSIL1C_*.SAFE, and LC09_L1TP_*.
*/ sensor: sensor types, i.e., OLCI_S3, MSI_S2, or OLI_L89;
*/ dest: path with images (*.TIFF). The default folder considers the atmospherically corrected images from GCERatmos.
*/ fmask_env: path with conda environment from fmask_env '.../anaconda3/envs/fmask_env/bin/python (or python.exe)'.
              This argument is requested only to Landsat-8/9/OLI and Sentinel-2/MSI.
"""

import subprocess
import warnings

#from sentinel3 import Sentinel3

class Satcloud:

    def __init__(self, path_img, sensor, dest, fmask_env):

        self.path_img = path_img
        self.sensor = sensor
        self.dest = dest # directory with images (*.TIFF).
        self.fmask_env = fmask_env

        self.SENTINEL3 = 'OLCI_S3'
        self.SENTINEL2 = 'MSI_S2'
        self.LANDSAT89 = 'OLI_L89'
        self.ENVNAME_FMASK = 'fmask_env' # conda environment name
        self.SCRIPTS2 = r'C:\FMASK\SatClouds\sentinel2.py' # script path
        self.SCRIPTL89 = 'landsat89.py' # script path

    def run(self):

        if self.sensor == self.SENTINEL3:

            #sentinel3 = Sentinel3(self.path_img, self.dest)
            #sentinel3.run()
            pass

        elif self.sensor == self.SENTINEL2:

            # The Sentinel-2 procedure is based on fmask-algorithm using an external conda environment.
            # Here, the 'fmask_env' is executed by command line:
            # Arguments used in the sentine2.py:
            args = [self.fmask_env, self.path_img, self.dest]
            # Activates the conda environment and runs the sentine2.py script:
            activate_command = f"conda activate {self.ENVNAME_FMASK} && python {self.SCRIPTS2} {' '.join(args)}"
            process = subprocess.Popen(activate_command, shell=True)
            process.wait()

        elif self.sensor == self.LANDSAT89:

            # The Sentinel-89 procedure is based on fmask-algorithm using an external conda environment.
            # Here, the 'fmask_env' is executed by command line:
            # Arguments used in the landsat89.py:
            args = [self.fmask_env, self.path_img, self.dest]
            # Activates the conda environment and runs the landsat89.py script:
            activate_command = f"conda activate {self.ENVNAME_FMASK} && python {self.SCRIPTL89} {' '.join(args)}"
            process = subprocess.Popen(activate_command, shell=True)
            process.wait()

        else:
            warnings.warn("The sensor type was not identified in SatClouds.\n"
                          "The valid sensors are:\n"
                          ">> OLCI_S3\n"
                          ">> MSI_S2\n"
                          ">> OLI_L8/9", UserWarning)


#path_img=r'C:\Users\tml411\Downloads\teste\S2A_MSIL1C_20230915T073621_N0509_R092_T38TQQ_20230915T093826.SAFE'
#sensor='MSI_S2'
#dest=r"C:\Users\tml411\Downloads\teste\MASK_OUT"
#fmask_env=r"C:\Users\tml411\AppData\Local\anaconda3\envs\fmask_env\python"

#a = Satcloud(path_img, sensor, dest, fmask_env)
#a.run()
