# Transformaciones aplicadas

Este documento detalla los procesos de limpieza, normalización y traducción realizados sobre las descripciones de las ofertas de empleo antes del análisis.

---

## 1. Traducción de descripciones en catalán (`traducir_catalan.py`)

- Se identificaron las provincias catalanas: Barcelona, Girona, Tarragona y Lleida.  
- Para las ofertas de estas regiones, se comprobó si la descripción contenía palabras frecuentes del catalán (por ejemplo, `amb`, `per`, `dilluns`, `ofereix`, `incorporació`, `serveis`, etc.).
- Cuando se detectó texto en catalán, se aplicó la traducción automática mediante la librería `googletrans` (`src='ca'`, `dest='es'`).
- La descripción traducida reemplazó a la original en el campo `descripcion`.

---

## 2. Limpieza y normalización de texto (`limpieza.ipynb`)

A partir de los textos ya traducidos, se aplicaron las siguientes transformaciones sobre la columna `descripcion`:

| Paso | Descripción |
|------|--------------|
| Conversión a minúsculas | Unifica el formato del texto para reducir duplicados. |
| Eliminación de signos de puntuación y caracteres especiales | Se eliminaron comas, puntos, guiones, paréntesis y otros símbolos. |
| Eliminación de números | Se suprimieron cifras aisladas como años, cantidades y fechas. |
| Eliminación de patrones de género | Se quitaron terminaciones tipo `/a`, `/as`, `/os` para simplificar el vocabulario (p. ej., `profesor/a` → `profesor`). |
| Lematización | Se redujeron las palabras a su forma base (p. ej., “trabajando”, “trabajos” → “trabajar”). |

El resultado de este proceso se incluye como una nueva columna en el csv llamada `descripcion_proc`.

---

## 3. Exportación del dataset limpio

El resultado final del proceso anterior se almacenó en el archivo `EURES_LIMPIO.csv`, que contiene:
- Descripción original (`descripcion`)
- Descripción procesada (`descripcion_proc`)
- Otras variables de análisis (id, fecha, ocupación, etc.)


## 4. Clasificación temática con modelo LLM

Se utilizó un modelo de lenguaje (LLM) en modo zero-shot para clasificar las ofertas según su sector o temática principal.

- La columna de entrada fue descripcion_proc, previamente limpia y lematizada.
- El modelo asignó a cada descripción una etiqueta temática (por ejemplo: Tecnología, Sanidad, Educación, Ingeniería, Turismo, Comercio, etc.).
- El resultado se guardó en las columnas: sector (nombre del sector asignado) y probs (probabilidad estimada por el modelo).

El dataset final se exportó como `EURES_CATEGORIZADO.csv`, que sirvió como base para los análisis posteriores (sentimiento y tópicos).

## 5. Análisis de sentimiento y generación de indicadores (indicadoresObligatorios.ipynb)

A partir del dataset `EURES_CATEGORIZADO.csv`, se aplicó un modelo de análisis de sentimiento en español.
El modelo evaluó el tono de las descripciones, añadiendo las siguientes columnas:
- sentimiento: valor numérico de la intensidad (entre -1 y 1, siendo -1 negativo, 0 sería neutro y por último 1 es positivo).

El resultado se almacenó en el archivo `EURES_CAT_SENTIMENT.csv`, utilizado posteriormente en `hipotesis.ipynb` para visualizar tendencias y análisis comparativos entre comunidades autónomas y sectores.