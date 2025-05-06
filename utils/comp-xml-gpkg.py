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
    msg = f"Inconsistent {what}"
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
        if field_defn.IsIgnored():
            continue
        fields[field_defn.GetName()] = field_defn.GetTypeName()
    return fields

def get_layer_by_name_case_insensitive(datasource, target_name):
    target_name_lower = target_name.lower()
    for i in range(datasource.GetLayerCount()):
        layer = datasource.GetLayerByIndex(i)
        if layer.GetName().lower() == target_name_lower:
            return layer
    return None

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
            print(f"Layer: {layer_name}/{layer.GetName()}", file=sys.stderr)
            layer_defn = layer.GetLayerDefn()

            layer_gpkg = ds_gpkg.GetLayerByName(layer_name)
            # layer_gpkg = get_layer_by_name_case_insensitive(ds_gpkg, layer_name)
            if layer_gpkg is None:
                error(f"Layer '{layer_name}' not found in GPKG reference")
                continue

            layer_name_gdal = layer.GetName()
            if layer.GetGeomType() != layer_gpkg.GetGeomType():
                inconsistency_error(layer_name, layer_name_gdal, "geometry type",
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

            fields_extra = []
            mismatch_type = []
            for fname, ftype in fields.items():
                if fname not in fields_gpkg.keys():
                    fields_extra.append(fname)
                else:
                    if ftype != fields_gpkg[fname]:
                        mismatch_type.append(f"{fname} (JVFDTM: {ftype}; GPKG: {fields_gpkg[fname]})")
            if fields_extra:
                inconsistency_error(layer_name, layer_name_gdal, "field names (not found in reference)",
                                    ','.join(fields_extra), None)
            if mismatch_type:
                inconsistency_error(layer_name, layer_name_gdal, "field types",
                                    ','.join(mismatch_type), None)

            while True:
                feat = layer.GetNextFeature()
                if feat is None:
                    break

                feat_id = feat.GetField("ID")
                layer_gpkg.SetAttributeFilter(f"ID = {feat_id}")
                feat_gpkg = layer_gpkg.GetNextFeature()
                if feat_gpkg is None:
                    inconsistency_error(layer_name, layer_name_gdal, "feature (ID) not found",
                                        feat_id, None)
                    continue

                # comp geometry
                geom = feat.GetGeometryRef()
                geom.FlattenTo2D()
                geom_gpkg = feat_gpkg.GetGeometryRef()
                geom_gpkg.FlattenTo2D()
                if geom.Equals(geom_gpkg) is False:
                    inconsistency_error(layer_name, layer_name_gdal, "geometries not equal",
                                        feat.GetFID(), None)

                # comp fields
                for i in range(layer_defn.GetFieldCount()):
                    field_defn = layer_defn.GetFieldDefn(i)
                    if field_defn.IsIgnored():
                        continue
                    field_name = field_defn.GetName()
                    if field_name in fields_extra:
                        continue
                    value_gpkg = feat_gpkg.GetField(field_name)
                    if str(feat.GetField(i)) != str(value_gpkg):
                        inconsistency_error(layer_name, layer_name_gdal,
                                            f"field ({field_name}) values",
                                            feat.GetField(i), value_gpkg)
            print('-' * 80, file=sys.stderr)

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
