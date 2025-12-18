# Proyecto: Análisis y Generación de un Dataset de Ofertas Laborales en España

## Descripción general

Este proyecto analiza la evolución y características de las **ofertas de empleo publicadas en España durante el último trimestre del año** (octubre, noviembre y diciembre), con algunos datos extendidos a enero.  
A través de técnicas de **procesamiento de lenguaje natural (PLN)**, se extraen indicadores que permiten estudiar dinámicas **sectoriales, temporales y temáticas** del mercado laboral español.

El trabajo se articula en torno a varias preguntas de investigación:  
- ¿Qué sectores concentran mayor volumen de ofertas?  
- ¿Existen patrones temporales según el sector?  
- ¿Qué tópicos predominan en las descripciones?  
- ¿Cómo varía la polaridad emocional entre sectores?  
- ¿Es posible clasificar automáticamente las ofertas en sectores definidos?

Para responderlas, se han calculado indicadores como volumen temporal de publicaciones, sentimiento medio, distribución de tópicos y clasificación temática asistida por modelos de lenguaje.

El repositorio incluye:

- Scripts de **scraping** para obtener las ofertas.
- Procesos de **limpieza, normalización y transformación** de los datos.
- Documentación del flujo completo.
- Publicación final del dataset en **Hugging Face**.

El dataset resultante contiene más de **7.000 ofertas**, con campos como título, ocupación, descripción, fechas, empresa, ubicación y tipo de contrato.

---

## Estructura del repositorio
```
└── miguelgp-13-dcdc-project/
    ├── README.md
    ├── LICENSE
    ├── report.md
    ├── dataMination/
    │   ├── analysis.md
    │   └── utils.py
    ├── dataPreparation/
    │   ├── data_cleaning.md
    │   ├── motivation.md
    │   ├── provincias.py
    │   └── transformaciones.md
    └── datasetGeneration/
        ├── README.md
        ├── clean_csv.py
        ├── LinksObtainer.py
        ├── metadata.json
        ├── OfferScrapper.py
        └── OfferScrapperFast.py

```
---

## Dependencias principales

El proyecto está desarrollado íntegramente en **Python** y utiliza librerías para:

- **Scraping:** `playwright`, `asyncio`, `urllib`
- **Procesamiento de texto:** `langdetect`, `spacy`, `nltk`, `deep_translator`, `googletrans`
- **Análisis y modelado:** `pandas`, `numpy`, `sklearn`, `statsmodels`, `tslearn`
- **Visualización:** `matplotlib`, `seaborn`
- **Modelos avanzados:** `transformers`, `torch`, `tensorflow`

---

## Guía paso a paso para reproducir el proyecto

### **1. Clonar el repositorio**
```bash
git clone https://github.com/MiguelGP-13/miguelgp-13-dcdc-project.git
cd miguelgp-13-dcdc-project
```
### 2. Crear y activar un entorno virtual
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
### **4. Descargar el dataset publicado en Hugging Face**

El dataset final utilizado en el proyecto está disponible públicamente en:

**https://huggingface.co/datasets/MiguelGP-13/JobOffers_ESP**

Puedes descargarlo manualmente desde la web o mediante Git:

```bash
git clone https://huggingface.co/datasets/MiguelGP-13/JobOffers_ESP data/
```
Esto generará una carpeta `data/` con los archivos en formato CSV y Parquet, junto con su `metadata.json`.

### **5. Ejecutar el pipeline completo**

El repositorio está organizado en tres bloques principales, que deben ejecutarse en este orden para reproducir el dataset y el análisis.

---

#### 5.1. Scraping de ofertas  
**Directorio:** `datasetGeneration/`

Scripts principales:

- `LinksObtainer.py`  
  Obtiene todas las URLs de ofertas desde EURES y portales autonómicos.

- `OfferScrapper.py` y `OfferScrapperFast.py`  
  Descargan el contenido de cada oferta (título, empresa, descripción, fechas, etc.).

- `clean_csv.py`  
  Limpieza inicial del CSV generado por el scraper.

Para ejecutar el scraping:

```bash
cd datasetGeneration
python LinksObtainer.py
python OfferScrapperFast.py
python clean_csv.py
```
#### 5.2. Preparación y limpieza de datos  
**Directorio:** `dataPreparation/`

En esta fase se aplican todas las transformaciones necesarias para convertir los datos obtenidos mediante scraping en un dataset limpio, coherente y listo para análisis.  
El directorio incluye:

- `data_cleaning.md` — Detalles del proceso de limpieza avanzada (normalización de fechas, eliminación de duplicados, tratamiento de nulos, etc.).
- `transformaciones.md` — Transformaciones adicionales aplicadas a campos textuales y categóricos.
- `provincias.py` — Script para estandarizar provincias y regiones españolas.
- `motivation.md` — Explicación del diseño del pipeline y decisiones metodológicas.

Este paso produce un dataset estructurado y consistente, que posteriormente se utiliza para análisis y publicación.

---

#### 5.3. Análisis y exploración  
**Directorio:** `dataMination/`

Incluye los recursos necesarios para realizar el análisis exploratorio:

- `analysis.md` — Estadísticas descriptivas, visualizaciones y primeras conclusiones.
- `utils.py` — Funciones auxiliares para carga de datos, gráficos y métricas.

Esta fase permite comprender la distribución de las ofertas, su evolución temporal y otros patrones relevantes.

---

## Dataset publicado en Hugging Face

El dataset final contiene más de **7.000 ofertas laborales**, con los siguientes campos principales:

- `url`
- `fecha_publicacion`
- `fecha_limite`
- `titulo`
- `empresa`
- `ocupacion`
- `descripcion`
- `pais`, `region`
- `tipo_contrato`

Formatos disponibles:

- **CSV**
- **Parquet**

Enlace directo al dataset:

**https://huggingface.co/datasets/MiguelGP-13/JobOffers_ESP**

---

## Conclusión

Este repositorio proporciona un flujo completo y reproducible para:

1. Obtener ofertas laborales reales mediante scraping.  
2. Limpiarlas y transformarlas en un dataset estructurado.  
3. Publicarlas como recurso abierto en Hugging Face.  
4. Facilitar estudios sobre dinámicas sectoriales, temporales y temáticas del mercado laboral español.
