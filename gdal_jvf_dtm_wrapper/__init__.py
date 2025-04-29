from contextlib import AbstractContextManager
from pathlib import Path
from collections import OrderedDict

from osgeo import gdal
from osgeo.ogr import Layer
gdal.UseExceptions()

from .exceptions import GdalJvfDtmWrapperError
from .logger import Logger
from .parse_xsd import XsdParser

class GdalJvfDtmWrapper(AbstractContextManager['GdalJvfDtmWrapper']):
    def __init__(self, filename):
        self._filename = filename
        xsd_path = Path(__file__).parent / "xsd" / "index" / "index_data.xsd"
        gdal.SetConfigOption('CPL_LOG', '/dev/null') # discard warning
        gdal.SetConfigOption('OGR_GMLAS_XERCES_MAX_TIME', '0')
        self._ds = gdal.OpenEx(filename, gdal.GA_ReadOnly | gdal.OF_VECTOR,
                               allowed_drivers=["GMLAS"],
                               open_options=[
                                   f"XSD={str(xsd_path)}",
                                   "REMOVE_UNUSED_LAYERS=YES"
                               ]
        )

        if self._ds.GetLayer(0).GetName() != "jvfdtm":
            raise GdalJvfDtmWrapperError("layer 'jvfdtm' not found")

        # parse XSD
        self.xsd_parser = XsdParser(xsd_path)
                
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
        for layer in self._ds:
            if 'zaznamyobjektu' not in layer.GetName():
                continue
            meta_layer = self._ds.GetLayerByName(layer.GetName().split('_')[0])
            layer_name = None
            if meta_layer is None:
                Logger.error(f"No metadata found for {layer.GetName()}")
                layer_name = layer.GetName() # use original name when no metadata found
            else:
                feat_count = len(meta_layer)
                if feat_count != 1:
                    Logger.warning(f"Unexpected feature count in {meta_layer.GetName()}: {len(meta_layer)}")
                if feat_count > 0:
                    meta_feat = meta_layer.GetNextFeature()
                    layer_name = "{}#{}#{}{}_{}".format(
                        meta_feat.GetField("kategorieobjektu").replace(' ', '_'),
                        meta_feat.GetField("skupinaobjektu").replace(' ', '_'),
                        meta_feat.GetField("objektovytypnazev_code_base"),
                        meta_feat.GetField("objektovytypnazev_code_suffix"),
                        meta_feat.GetField("objektovytypnazev").capitalize().replace(' ', '_'),
                    )
                    
                    layer_defn = layer.GetLayerDefn()
                    layer_name_gdal = layer.GetName()
                    for i in range(layer_defn.GetFieldCount()):
                        field_defn = layer_defn.GetFieldDefn(i)
                        field_name = field_defn.GetName()
                        # TODO: some attributes cannot be match due to types
                        # field_defn.SetName())
                        if field_name.startswith(('atributyobjektu', 'atribuobjekt')):
                            # new_field_name = self.xsd_parser.fieldName(layer_name_gdal, field_name)
                            field_defn.SetName(field_name.split('_')[-1])

            layers[layer_name] = layer

        return layers

    def __len__(self):
        return len(self.layers.keys())

    def __iter__(self):
        return iter(self.layers.items())

    def __getitem__(self, key):
        return self.layers[key]

    def fields(self, layer_name):
        fields = []
        layer_defn = self.layers[layer_name].GetLayerDefn()
        for idx in range(layer_defn.GetFieldCount()):
            field_defn = layer_defn.GetFieldDefn(idx)
            if 'ogr_pkid' not in field_defn.GetName():
                fields.append(field_defn.GetName())

        return fields
