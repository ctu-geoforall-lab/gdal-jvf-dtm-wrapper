# GDAL Python wrapper pro JVF DTM

**Experimentální** prototyp Python wrapperu (API)

Počáteční motivace: [GIVS 2025](https://tinyurl.com/givs2025-landa)

Cíle:

- Usnadnit práci s [JVF DTM](https://cuzk.gov.cz/DMVS/JVF-DTM.aspx) v
  Pythonu
- Řešit nalezené problémy při čtení JVF DTM
- Přiblížit se k referenčním datům (GPKG poskytované
  [ISDMVS](https://dmvs.cuzk.gov.cz/portal))
- **Přechodné** řešení: cílem je upravit [GDAL
  GMLAS](https://gdal.org/en/stable/drivers/vector/gmlas.html) driver
  pro potřeby JVF DTM

## Použití

[Python API](./docs/notebooks/usage.ipynb)

Příklad `ogrinfo`:

```
ogrinfo \
 --config OGR_GMLAS_XERCES_MAX_TIME=0 \
 -oo XSD=gdal_jvf_dtm_wrapper/xsd/index/index_data.xsd \
 -oo CONFIG_FILE=gdal_jvf_dtm_wrapper/gmlasconf.xml \
 GMLAS:tests/sample_data/ukazka_ZPS.xml
```
