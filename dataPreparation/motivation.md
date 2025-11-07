# Motivación
## Objetivo general del proyecto

El objetivo principal de este proyecto es analizar la evolución y características de las ofertas de empleo publicadas en España durante el último trimestre del año (octubre, noviembre y diciembre), con algunos datos extendidos a enero. A través de técnicas de procesamiento de lenguaje natural (PLN), se busca extraer indicadores clave que permitan comprender dinámicas sectoriales, temporales y temáticas del mercado laboral español.

## Preguntas de investigación y hipótesis planteadas

### Preguntas de investigación

- ¿Qué sectores concentran mayor volumen de ofertas laborales en el último trimestre del año?
- ¿Existen patrones temporales en la publicación de ofertas según el sector?
- ¿Qué tópicos predominan en las descripciones de ofertas laborales en España?
- ¿Qué nivel de polaridad emocional presentan las ofertas laborales y varía según el sector?
- ¿Es posible categorizar automáticamente las ofertas en sectores definidos usando modelos de lenguaje?

### Hipótesis planteadas

1. El volumen de ofertas en el sector sanitario aumenta durante el mes de diciembre, coincidiendo con refuerzos estacionales en atención médica.
2. Las ofertas del sector logístico presentan mayor actividad en el inicio de diciembre, en preparación para la campaña navideña.
3. Los tópicos relacionados con `formación` y `flexibilidad` aparecen con mayor frecuencia en sectores como educación y cultura.

## Justificación del dataset y de los indicadores calculados

El dataset FAIR utilizado contiene miles de registros de ofertas laborales en España, con campos como título, ocupación, descripción y categoría. Su cobertura nacional y diversidad sectorial lo convierten en una fuente representativa para el análisis del mercado laboral.

Se han calculado los siguientes indicadores:

- Volumen temporal de publicaciones: permite detectar picos de actividad por sector y mes.
- Sentimiento medio agregado: aunque predominan los valores neutros, se han aplicado tres modelos para mejorar la sensibilidad del análisis.
- Distribución de tópicos: se ha utilizado LDA para identificar 10 temas recurrentes en las descripciones.
- Clasificación temática asistida por LLM: se han entrenado tres modelos para categorizar las ofertas en 10 sectores definidos, combinando sus predicciones mediante un voting classifier.

Estos indicadores permiten formular hipótesis verificables y explorar patrones relevantes en el mercado laboral.

## Limitaciones y posibles sesgos detectados

- Sesgo geográfico: aunque el dataset cubre toda España, las grandes ciudades concentran más ofertas, lo que puede distorsionar la representatividad regional.
- Sesgo institucional: la mayoría de ofertas provienen de canales públicos, lo que puede influir en el estilo y contenido de las descripciones.
- Limitaciones del análisis de sentimiento: dado el carácter formal y objetivo de las ofertas laborales, los modelos tienden a clasificar la mayoría de textos como neutros.
- Ambigüedad en la clasificación temática: algunas ofertas presentan descripciones vagas o genéricas, lo que dificulta su categorización precisa.
