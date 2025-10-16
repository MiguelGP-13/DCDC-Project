# Ofertas de Empleo Públicas en España (EURES, 2025)

## Dataset Summary

Este dataset recopila ofertas de empleo publicadas en portales oficiales de empleo europeos y españoles, principalmente a través de la red **EURES (European Employment Services)**.  
Forma parte del proyecto desarrollado para la práctica de la **Universidad Politécnica de Madrid (UPM)** en la asignatura *Descubrimiento del Conocimiento en Datos Complejos*.  

El dataset tiene como propósito servir como fuente de información para análisis del mercado laboral, extracción de información, y aplicaciones de minería de texto o aprendizaje automático sobre descripciones de empleo públicas.  

Los datos proceden íntegramente de fuentes **públicas y abiertas** bajo políticas de datos abiertos gubernamentales.

---

## Changelog

**Versión 1.0 – Octubre 2025**
- Primera versión del dataset.
- Datos extraídos de portales oficiales mediante scrapers basados en Playwright.
- Limpieza, normalización y exportación final en formato CSV.

---

## How to use

El dataset se encuentra disponible en formato **CSV UTF-8**. Puede cargarse directamente en entornos de análisis de datos (Python, R, Excel, etc.).

### Ejemplo en Python
```python
import pandas as pd

df = pd.read_csv("empleos_espanoles_eures_2025.csv")
print(df.head())
```

### Ejemplo con Hugging Face Datasets
```python
from datasets import load_dataset

ds = load_dataset("tu-usuario/empleos-espanoles-eures-2025")
print(ds['train'][0])
```

---

## Dataset Details

### Data Structure

| Campo | Descripción | Tipo |
|--------|--------------|------|
| `url` | Enlace a la oferta original en el portal EURES o fuente autonómica oficial | string |
| `fecha_publicacion` | Fecha de publicación de la oferta (DD/MM/AAAA) | date |
| `fecha_limite` | Fecha límite para postular | date |
| `titulo` | Título del puesto ofertado | string |
| `empresa` | Nombre de la empresa o entidad contratante (si está disponible) | string |
| `ocupacion` | Ocupación o categoría profesional principal | string |
| `descripcion` | Descripción textual completa del puesto (sin datos personales) | string |
| `pais` | País de la oferta | string |
| `region` | Comunidad autónoma o provincia | string |
| `tipo_contrato` | Tipo de contrato o modalidad laboral | string |

Formato de archivo: `CSV UTF-8`  
Número estimado de registros: variable (según fecha de ejecución del scraper).  
Frecuencia de actualización: única (los scripts permiten obtener datos actualizados en futuras ejecuciones).

---

### Data Preview

Ejemplo de los primeros registros:

| url | fecha_publicacion | fecha_limite | titulo | empresa | ocupacion | descripcion | pais | region | tipo_contrato |
|-----|-------------------|---------------|---------|----------|------------|--------------|-------|----------|----------------|
| https://europa.eu/eures/portal/jv-se/jv-details/NzE4NDAzMCAxMDI?lang=es | 10/10/2025 | 31/10/2025 | CONDUCTORES DE CAMIÓN, EN GENERAL |  | Conductor de vehículo de carga | REQUIERE ESTAR EN POSESIÓN DEL CAP... | España | Palencia | Contrato |
| https://europa.eu/eures/portal/jv-se/jv-details/NzIyMDEwMCAxMDI?lang=es | 10/10/2025 | 10/10/2025 | WORK/LOCATION |  | Empleado administrativo de archivos | ES BUSCA UNA PERSONA AMB ESTUDIS... | España | Tarragona | Contrato |

---

### Data Collection

Los datos fueron recolectados mediante **scripts de scraping** desarrollados en Python utilizando la librería **Playwright**.  
Se accedió de manera automatizada a las ofertas publicadas en el portal **EURES** y, en algunos casos, a portales autonómicos integrados en la red pública de empleo.

#### Descripción del proceso de recolección:
1. Obtención de listados de URLs de ofertas a partir de buscadores públicos de empleo.
2. Acceso controlado a cada página con Playwright, respetando límites de concurrencia y tiempos de espera para evitar sobrecarga.
3. Extracción de información mediante selectores identificados (`id` y `class`) en la estructura HTML.
4. Registro de cada oferta en formato tabular (`.csv`), garantizando que los campos principales estén completos.

Todos los datos proceden de fuentes públicas de libre acceso, sin necesidad de autenticación ni recopilación de información personal.

---

### Data Processing

Tras la obtención inicial, se realizó un preprocesamiento y estandarización a través de un cuaderno (notebook) de limpieza.  
Las transformaciones incluyeron:

- **Normalización de fechas** al formato `DD/MM/AAAA`.  
- **Eliminación de caracteres HTML**, saltos de línea y espacios redundantes en las descripciones.  
- **Anonimización de datos personales** (se eliminaron contactos, correos o nombres propios presentes en los textos).  
- **Verificación de duplicados** mediante la columna `url`.  
- **Filtrado y validación de campos** obligatorios (`titulo`, `pais`, `region`, `tipo_contrato`).  
- **Exportación final a CSV UTF-8**, listo para su publicación.

El cuaderno de procesamiento acompaña al dataset para permitir la replicación del flujo completo de recolección y limpieza.

---

### Data Maintenance

Este dataset es una **recopilación única (snapshot)** de ofertas publicadas durante octubre de 2025.  
No se prevé su actualización periódica, aunque los **scripts de scraping y limpieza** incluidos permiten reproducir el proceso en cualquier momento para obtener datos más recientes.

Responsables de mantenimiento y contacto:
- Álvaro Felipe – alvaro.felipe@alumnos.upm.es  
- Miguel Gómez – miguel.gprieto@alumnos.upm.es  
- Alex Pérez – alex.pcarpente@alumnos.upm.es

---

## License

Este dataset deriva de datos abiertos del portal EURES, gestionado por la Comisión Europea y la European Labour Authority (ELA), bajo los términos de la Decision 2011/833/EU on the reuse of Commission documents.

El procesamiento, normalización y compilación de esta versión se se distribuye bajo la licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)**. 

En consecuencia, el uso de los datos originales deberá respetar las condiciones de reutilización de la Comisión Europea.


**Atribución requerida:**
> Álvaro Felipe, Miguel Gómez, Alex Pérez (2025). *Ofertas de Empleo Públicas en España (EURES, 2025)*. Universidad Politécnica de Madrid. Licencia CC BY 4.0.

En caso de reutilizar o redistribuir el dataset, por favor menciona la fuente y los autores en la forma indicada en la sección de *Citation*.

---

## Citation

Si utiliza este dataset en publicaciones académicas o proyectos derivados, se recomienda la siguiente cita:

> Álvaro Felipe, Miguel Gómez, Alex Pérez (2025). *Ofertas de Empleo Públicas en España (EURES, 2025)* [Dataset]. Universidad Politécnica de Madrid. Disponible en Hugging Face Datasets. Licencia CC BY 4.0.

---

## Acknowledgements

Los datos originales provienen de portales de empleo **oficiales y públicos**, principalmente de la red **EURES** y sus integraciones autonómicas.  
Agradecimientos a las instituciones europeas y españolas que mantienen políticas de datos abiertos, y a la comunidad de código abierto por las herramientas utilizadas, en particular:

- [Playwright](https://playwright.dev/) – automatización de navegación web.  
- [Pandas](https://pandas.pydata.org/) – procesamiento y análisis de datos.  
- [Hugging Face Datasets](https://huggingface.co/docs/datasets) – publicación y distribución abierta de datasets.  

---

*Última actualización: 15 de octubre de 2025*  
*Versión: 1.0*
