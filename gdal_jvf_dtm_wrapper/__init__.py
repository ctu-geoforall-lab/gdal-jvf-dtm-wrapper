from contextlib import AbstractContextManager
from pathlib import Path

from osgeo import gdal
gdal.UseExceptions()

from .exceptions import GdalJvfDtmWrapperError

class GdalJvfDtmWrapper(AbstractContextManager['GdalJvfDtmWrapper']):
    def __init__(self, filename):
        self._filename = filename
        xsd_path = Path(__file__).parent / "xsd" / "index" / "index_data.xsd"
        self._ds = gdal.OpenEx(filename, gdal.GA_ReadOnly,
                               allowed_drivers=["GMLAS"],
                               open_options=[
                                   f"XSD={str(xsd_path)}",
                                   "REMOVE_UNUSED_LAYERS=YES",
                                   "REMOVE_UNUSED_FIELDS=YES"]
        )

        if self._ds.GetLayer(0).GetName() != "jvfdtm":
            raise GdalJvfDtmWrapperError("layer 'jvfdtm' not found")

        self.meta = self._read_metadata()
        
    def __del__(self):
        if self._ds:
            self._ds.Close()
        
    def __enter__(self):
        """Enter context manager protocol.
        """
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager protocol.
        """
        super().__exit__(exc_type, exc_val, exc_tb)
        

    def _read_metadata(self):
        lyr_name = "datajvfdtm"
        lyr = self._ds.GetLayerByName(lyr_name)
        if lyr is None:
            raise GdalJvfDtmWrapperError(f"unable to read metadata {lyr_name}")

        count = lyr.GetFeatureCount()
        if count != 1:
            raise GdalJvfDtmWrapperError(f"unexpected metadata records ({count})")

        feat = lyr.GetNextFeature()
        meta = {
            "verze": feat["verzejvfdtm"],
            "datumzapisu": feat["datumzapisu"],
            "typzapisu": feat["typzapisu"]
        }
        feat = None

        return meta
