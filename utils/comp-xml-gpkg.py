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
    msg = f"Layer {layer_name}/{layer_name_gdal}: inconsistent {what}"
    if gpkg:
        msg += f" (JVF DTM: {jvf_dtm}; GPKG {gpkg})"
    else:
        msg += f": {jvf_dtm}"
    error(msg)

def collect_fields(layer):
    fields = {}
    layer_defn = layer.GetLayerDefn()
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        fields[field_defn.GetName().lower()] = field_defn.GetTypeName()
    return fields

def main(input_xml, ref_gpkg):
    # open ref data
    ds_gpkg = gdal.OpenEx(ref_gpkg, gdal.OF_VECTOR | gdal.GA_ReadOnly)
    
    with GdalJvfDtmWrapper(input_xml) as inp:
        # number of layers
        if len(inp) != len(ds_gpkg):
            error(f"Incosistent number of layers (JVF DTM:{len(inp)}; GPKG: {len(ds_gpkg)})")

        # compare JVF vs GPKG
        imp_layers = {}
        for layer_name, layer in inp:
            layer_defn = layer.GetLayerDefn()

            layer_gpkg = ds_gpkg.GetLayerByName(layer_name)
            if layer_gpkg is None:
                error(f"Layer '{layer_name}' not found in GPKG reference")
                continue

            layer_name_gdal = layer.GetName()
            if layer.GetGeomType() != layer_gpkg.GetGeomType():
                inconsistency_error(layer_name, layer_name_gdal, "geometry_type",
                                    ogr.GeometryTypeToName(layer.GetGeomType()),
                                    ogr.GeometryTypeToName(layer_gpkg.GetGeomType()))
            layer_defn_gpkg = layer_gpkg.GetLayerDefn()
            layer_field_count = len(inp.fields(layer_name))
            if layer_field_count != layer_defn_gpkg.GetFieldCount():
                inconsistency_error(layer_name, layer_name_gdal, "field count",
                                    layer_field_count,
                                    layer_defn_gpkg.GetFieldCount())
            if layer.GetFeatureCount() != layer_gpkg.GetFeatureCount():
                inconsistency_error(layer_name, layer_name_gdal, "feature count",
                                    layer.GetFeatureCount(),
                                    layer_gpkg.GetFeatureCount())

            # field_names
            fields = collect_fields(layer)
            fields_gpkg = collect_fields(layer_gpkg)

            extra = []
            mismatch_type = []
            for fname, ftype in fields.items():
                if fname not in fields_gpkg.keys():
                    extra.append(fname)
                else:
                    if ftype != fields_gpkg[fname]:
                        mismatch_type.append(fname)
            if extra:
                inconsistency_error(layer_name, layer_name_gdal, "field names (not found in reference)",
                                    ','.join(extra), None)
            if mismatch_type:
                inconsistency_error(layer_name, layer_name_gdal, "field types",
                                    ','.join(mismatch_type), None)

            # TODO: features
            break

        # compare GPKG vs JVF
        for layer in ds_gpkg:
            layer_name = layer.GetName()
            if layer_name not in inp.layers.keys():
                error(f"Reference layer {layer_name} not found in JVF DTM")

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
