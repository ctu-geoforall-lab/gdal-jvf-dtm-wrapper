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
