#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

from osgeo import gdal, ogr

sys.path.insert(0, str(Path(__file__).parent.parent))
from gdal_jvf_dtm_wrapper import GdalJvfDtmWrapper

def error(msg):
    print("ERROR: " + msg, file=sys.stderr)

def inconsistency_error(layer_name, layer_name_gdal, what, jvf_dtm, gpkg):
    error(f"Layer {layer_name}/{layer_name_gdal}: inconsistent {what} (JVF DTM: {jvf_dtm}; GPKG {gpkg})")

def main(input_xml, ref_gpkg):
    # open ref data
    ds_gpkg = gdal.OpenEx(ref_gpkg, gdal.OF_VECTOR | gdal.GA_ReadOnly)
    
    with GdalJvfDtmWrapper(input_xml) as inp:
        # number of layers
        if len(inp) != len(ds_gpkg):
            error(f"Incosistent number of layers (JVF DTM:{len(inp)}; GPKG: {len(ds_gpkg)})")

        # compare JVF vs GPKG
        imp_layers = {}
        for lyr_name, lyr in inp:
            layer_defn = lyr.GetLayerDefn()

            lyr_gpkg = ds_gpkg.GetLayerByName(lyr_name)
            if lyr_gpkg is None:
                error(f"Layer '{lyr_name}' not found in GPKG reference")
                continue

            lyr_name_gdal = lyr.GetName()
            if lyr.GetGeomType() != lyr_gpkg.GetGeomType():
                inconsistency_error(lyr_name, lyr_name_gdal, "geometry_type",
                                    ogr.GeometryTypeToName(lyr.GetGeomType()),
                                    ogr.GeometryTypeToName(lyr_gpkg.GetGeomType()))
            layer_defn_gpkg = lyr_gpkg.GetLayerDefn()
            if layer_defn.GetFieldCount() != layer_defn_gpkg.GetFieldCount():
                inconsistency_error(lyr_name, lyr_name_gdal, "field count",
                                    layer_defn.GetFieldCount(),
                                    layer_defn_gpkg.GetFieldCount())
            if lyr.GetFeatureCount() != lyr_gpkg.GetFeatureCount():
                inconsistency_error(lyr_name, lyr_name_gdal, "feature count",
                                    lyr.GetFeatureCount(),
                                    lyr_gpkg.GetFeatureCount())

            # TODO: field types
            # TODO: features
            break

        # compare GPKG vs JVF
        for lyr in ds_gpkg:
            lyr_name = lyr.GetName()
            if lyr_name not in inp.layers.keys():
                error(f"Reference layer {lyr_name} not found in JVF DTM")

    # close ref data
    ds_gpkg.Close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compare data in JVF DTM (xml) with reference data in OGC GeoPackage format.'
    )
    parser.add_argument('input_xml', help="Path to input data in JVF DTM")
    parser.add_argument('ref_gpkg', help="Path to reference OGC GeoPackage file")

    args = parser.parse_args()

    main(args.input_xml, args.ref_gpkg)
