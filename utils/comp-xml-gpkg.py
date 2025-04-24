#!/usr/bin/env python3

import argparse
from gdal_jvf_dtm_wrapper import GdalJvfDtmWrapper

def main(input_xml, ref_gpkg):
    with GdalJvfDtmWrapper(input_xml) as inp:
        print(inp.meta['verze'])
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compare data in JVF DTM (xml) with reference data in OGC GeoPackage format.'
    )
    parser.add_argument('input_xml', help="Path to input data in JVF DTM")
    parser.add_argument('ref_gpkg', help="Path to reference OGC GeoPackage file")

    args = parser.parse_args()

    main(agrs.input_xml, args.ref_gpkg)
