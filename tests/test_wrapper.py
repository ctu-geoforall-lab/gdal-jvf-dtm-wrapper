from pathlib import Path

from osgeo import ogr

from gdal_jvf_dtm_wrapper import GdalJvfDtmWrapper

ref_layers = {
    'Budovy#Objekt_budovy#010000000104_Budova': ('Point', 10, 6), # geom type, field count, feature count
    'Rekreační,_kulturní_a_sakrální_stavby#Stavba_kulturní,_sakrální#010000015901_Drobná_kulturní_stavba': ('Point', 14, 24),
    'Konstrukční_prvky_objektů#Základní_konstrukční_prvek#010000029902_Hranice_budovy': ('Curve', 13, 64),
    'Konstrukční_prvky_objektů#Základní_konstrukční_prvek#010000030402_Hranice_dopravní_stavby_nebo_plochy': ('Curve', 14, 236),
    'Konstrukční_prvky_objektů#Základní_konstrukční_prvek#010000030102_Hranice_schodiště': ('Curve', 14, 112),
    'Součásti_a_příslušenství_staveb#Stavba_společná_pro_více_skupin#010000016202_Plot': ('Curve', 15, 21),
    'Geodetické_prvky#Podrobný_bod#010000021801_Podrobný_bod_zps': ('Point', 14, 893),
    'Vodstvo,_vegetace_a_terén#Terénní_útvar#010000021702_Terénní_hrana': ('Curve', 14, 55)
}

class TestGdalJvfDtmWrapper:
    data_dir = Path(__file__).parent / "sample_data"
    zps_file = data_dir / "ukazka_ZPS.xml"

    def test_001_open(self):
        """Open data and check metadata."""
        with GdalJvfDtmWrapper(self.zps_file) as wrp:
            assert wrp.meta['verze'] == '1.4.3'

    def test_002_layers(self):
        """Test number of reported layers."""
        with GdalJvfDtmWrapper(self.zps_file) as wrp:
            # number of reported layers
            assert len(wrp) == 8

            # check names
            assert list(wrp.layers.keys()) == list(ref_layers.keys())

            for name, lyr in wrp:
                ref_data = ref_layers[name]
                
                # check geometry type
                geom_type = lyr.GetGeomType()
                assert ogr.GeometryTypeToName(geom_type) == ref_data[0]

                # number of attributes
                layer_defn = lyr.GetLayerDefn()
                assert layer_defn.GetFieldCount() == ref_data[1]

                # number of features
                assert lyr.GetFeatureCount() == ref_data[2]
