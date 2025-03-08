from pathlib import Path

from gdal_jvf_dtm_wrapper import GdalJvfDtmWrapper

class TestGdalJvfDtmWrapper:
    data_dir = Path(__file__).parent / "sample_data"

    def test_open(self):
        with GdalJvfDtmWrapper(self.data_dir / "ukazka_ZPS.xml") as wrp:
            pass
            # print(wrp.meta)
