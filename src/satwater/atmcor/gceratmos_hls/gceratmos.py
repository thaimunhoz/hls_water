import os
import glob
import shutil
import warnings
import rasterio
import numpy as np

from src.satwater.atmcor.gceratmos_hls import toolbox as tool
from src.satwater.atmcor.gceratmos_hls.metadata import Metadata_MSI_S2
from src.satwater.atmcor.gceratmos_hls.metadata import Metadata_OLI_L89
from src.satwater.atmcor.gceratmos_hls.atm.atmosphere import Atmosphere
from src.satwater.atmcor.gceratmos_hls.atm.correction import Correction

class Gceratmos:

    def __init__(self,
                 path_main: str,
                 path_dest: str,
                 networkdrive_letter: str,
                 satellite: str,
                 mode=None,
                 path_buffer=None):

        self.GRANULE = '/GRANULE'
        self.IMG_DATA = '/IMG_DATA'

        self.path_main = path_main
        self.path_dest = path_dest
        self.networkdrive_letter = networkdrive_letter
        self.satellite = satellite
        self.mode = mode
        self.path_buffer = path_buffer

    def run(self):

        """
        Returns the surface reflectance.
        """

        if self.satellite == 'MSI_S2':

            print(self.path_main[-65:])

            dest = tool.newdirectory(self.path_dest, self.path_main[-65:])
            tempdir = tool.newdirectory(dest, 'tempdir')

            # Accesses the images JP2 and converts them to .TIFF:
            path = [i for i in glob.glob(os.path.join(self.path_main + self.GRANULE, '*')) if 'L1C_' in i]
            band_jp2 = [i for i in glob.glob(os.path.join(path[0] + self.IMG_DATA, '*.jp2')) if '_B' in i]

            for i in band_jp2:
                tool.jp2_to_tiff_xarray(i, tempdir + '/' + i[-30:-4] + '.TIF')

            # Metadata:
            meta = Metadata_MSI_S2(self.path_main, self.path_dest, self.networkdrive_letter, self.satellite, self.mode)
            meta.run()

            # Atmospheric parameters:
            atmos_param = Atmosphere(meta)
            atmos_param.run()

            # Atmospheric correction:
            for index, band in enumerate(meta.bandname):
                arr = tool.loadarray(tempdir + '/' + band[0:-4] + '.TIF')
                print(tempdir + '/' + band[0:-4] + '.TIF')
                corr = Correction(meta, atmos_param, arr, index)
                corr.run()
                arr_c = np.where(corr.arr_sr < 0, -9999, corr.arr_sr) # NaN value.
                print(arr_c)
                tool.export(arr_c, band, tempdir + '/' + band[0:-4] + '.TIF', dest)

            tool.export_meta(meta, dest)
            shutil.rmtree(tempdir)

        elif self.satellite == 'OLI_L8/9':

            print(self.path_main[-40:])

            dest = tool.newdirectory(self.path_dest, self.path_main[-40:])

            #tempdir = tool.newdirectory(dest, 'tempdir')

            # Metadata:
            meta = Metadata_OLI_L89(self.path_main, self.path_dest, self.networkdrive_letter, self.satellite, self.mode)
            meta.run()

            # Atmospheric parameters:
            atmos_param = Atmosphere(meta)
            atmos_param.run()

            # Atmospheric correction:
            for index, band in enumerate(meta.bandname):

                with rasterio.open(meta.path_main + '/' + band[0:-4] + '.TIF') as src:
                    out_meta = src.meta.copy()
                    out_transform = src.transform
                    arr = src.read(1)

                corr = Correction(meta, atmos_param, arr, index)
                corr.run()

                arr_c = np.where(corr.arr_sr < 0, -9999, corr.arr_sr) # NaN value

                out_meta.update({"driver": "GTiff",
                                 "height": arr_c.shape[0],
                                 "width": arr_c.shape[1],
                                 "transform": out_transform,
                                 "dtype": 'float64'
                                 })

                with rasterio.open(tool.newdirectory(self.path_dest, self.path_main[-40:]) + '/' + band[0:-4] + '.TIF',"w", **out_meta) as dest:
                    dest.write(arr_c, 1)

            tool.export_meta(meta, tool.newdirectory(self.path_dest, self.path_main[-40:]))
            #shutil.rmtree(tempdir)

        else:

            warnings.warn("The sensor type was not identified in GCERATMOS.\n", UserWarning)