# GDAL Python wrapper pro JVF DTM

![Tests](https://github.com/ctu-geoforall-lab/gdal-jvf-dtm-wrapper/actions/workflows/test_wrapper.yml/badge.svg)

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

## Porovnání s GPKG ISDMVS

- geometrie 2D vs 3D

```
ERROR: Inconsistent geometry type (JVF DTM: Point; GPKG 3D Point)
ERROR: Inconsistent geometry type (JVF DTM: Curve; GPKG 3D Line String)
```

- datové typy atributů

```
Budovy#Objekt_budovy#010000000104_Budova/BudovaDefinicniBod_ZaznamyObjektu_ZaznamObjektu
ERROR: Inconsistent field types: ID (JVFDTM: String; GPKG: Integer64),DatumVkladu (JVFDTM: DateTime; GPKG: Date),DatumZmeny (JVFDTM: DateTime; GPKG: Date),UrovenUmisteniObjektuZPS (JVFDTM: Integer; GPKG: Integer64)
...
```


- datum vkladu/zmeny

```
ERROR: Inconsistent field (DatumVkladu) values (JVF DTM: 2024/09/15 00:00:00; GPKG 2024/09/14)
ERROR: Inconsistent field (DatumZmeny) values (JVF DTM: 2022/05/04 14:09:29; GPKG 2022/05/04)
```

- boolean vs integer

```
ERROR: Inconsistent field (HraniceJinehoObjektu) values (JVF DTM: True; GPKG 1)
```

- chybějící atributy

```
Layer: Geodetické_prvky#Podrobný_bod#010000021801_Podrobný_bod_zps/PodrobnyBodZPS_ZaznamyObjektu_ZaznamObjektu
ERROR: Inconsistent field names (not found in reference): AtributyObjektu_ZpusobPorizeniPB_ZPS
```

- chybějící vrstva

```
ERROR: Reference layer Geodetické_prvky#Podrobný_bod#010000021801_Podrobný_bod_ZPS not found in JVF DTM
```

-> Nekonzistence v `podrobnybodzps`: 

```
  objektovytypnazev (String) = podrobný bod ZPS
  skupinaobjektu (String) = Podrobný bod
  obsahovacast (String) = ZPS
```
