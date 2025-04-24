from contextlib import AbstractContextManager
from pathlib import Path
from collections import OrderedDict

from osgeo import gdal
from osgeo.ogr import Layer
gdal.UseExceptions()

from .exceptions import GdalJvfDtmWrapperError
from .logger import Logger

class GdalJvfDtmWrapper(AbstractContextManager['GdalJvfDtmWrapper']):
    def __init__(self, filename):
        self._filename = filename
        xsd_path = Path(__file__).parent / "xsd" / "index" / "index_data.xsd"
        self._ds = gdal.OpenEx(filename, gdal.GA_ReadOnly,
                               allowed_drivers=["GMLAS"],
                               open_options=[
                                   f"XSD={str(xsd_path)}",
                                   "REMOVE_UNUSED_LAYERS=YES"]
        )

        if self._ds.GetLayer(0).GetName() != "jvfdtm":
            raise GdalJvfDtmWrapperError("layer 'jvfdtm' not found")

        self.meta = self._read_metadata()
        Logger.info(f"Version {self.meta['verze']} detected")
        self.layers = self._read_layers()

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
            raise GdalJvfDtmWrapperError(f"Unable to read metadata {lyr_name}")

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

    def _read_layers(self):
        layers = OrderedDict()
        for lyr in self._ds:
            if 'zaznamyobjektu' not in lyr.GetName():
                continue
            meta_lyr = self._ds.GetLayerByName(lyr.GetName().split('_')[0])
            layer_name = None
            if meta_lyr is None:
                Logger.error(f"No metadata found for {lyr.GetName()}")
                layer_name = lyr.GetName() # use original name when no metadata found
            else:
                feat_count = len(meta_lyr)
                if feat_count != 1:
                    Logger.warning(f"Unexpected feature count in {meta_lyr.GetName()}: {len(meta_lyr)}")
                if feat_count > 0:
                    meta_feat = meta_lyr.GetNextFeature()
                    layer_name = "{}#{}#{}{}_{}".format(
                        meta_feat.GetField("kategorieobjektu").replace(' ', '_'),
                        meta_feat.GetField("skupinaobjektu").replace(' ', '_'),
                        meta_feat.GetField("objektovytypnazev_code_base"),
                        meta_feat.GetField("objektovytypnazev_code_suffix"),
                        meta_feat.GetField("objektovytypnazev").capitalize().replace(' ', '_'),
                    )

            layers[layer_name] = lyr

        return layers

    def __len__(self):
        return len(self.layers.keys())

    def __iter__(self):
        return iter(self.layers.items())
