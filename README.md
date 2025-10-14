# DCDC-Project

## 1. Obtención del dataset:
Para obtener los datos hemos *scrapeado* todas las ofertas de trabajo disponibles en España el 11 de octubre en [eures.europa.eu](https://europa.eu/eures/portal/jv-se/home?lang=es).

Hemos obtenido 9685 ofertas (incluyendo duplicadas), de las cuales, 7435 ofertas estaban en español.

Al eliminar las ofertas duplicadas, lo guardamos en 3 csv:
- `ofertasRaw.csv`: Todas las 9685 las ofertas obtenidas. (con repetidos y varios idiomas)
- `ofertas.csv`: Todas las 7299 ofertas en español, 3562 sin título. (Relevantes, ya que el campo ocupación se podría utilizar como nombre)
- `ofertasDescriptive.csv`: Solo las 3737 ofertas con nombre descriptivo.

### Preproceso de los datos
1. Eliminamos los anuncios que no están en español
2. Eliminación de columnas con datos mal obtenidos (`educación`) y con 100% de nulos (`duración de jornada`).
3. Eliminación de ofertas sin fecha límite de solicitud

### Características del dataset:

| Columna            | % Nulos   | Descripción                                                                 |
|--------------------|-----------|------------------------------------------------------------------------------|
| url                | 0%    | Enlace a la oferta de trabajo.                                               |
| fecha_publicacion  | 0%    | Fecha en la que se publicó la oferta.                                        |
| fecha_limite       | 0%    | Fecha límite para postularse a la oferta.                                    |
| titulo             | 0%    | Título del puesto ofertado.                                                  |
| empresa            | 99%   | Nombre de la empresa que publica la oferta (casi siempre ausente).           |
| ocupacion          | 10%   | Categoría o área de ocupación del puesto.                                    |
| descripcion        | 0%    | Texto descriptivo con detalles de la oferta.                                 |
| pais               | 0%    | País donde se ofrece el empleo.                                              |
| region             | 1.6%    | Región dentro del país.                        |
| tipo_contrato      | 0.1%    | Tipo de contrato ofrecido (ej. indefinido, temporal, prácticas).             |

*Existen poco más de 400 filas con ocupación y titulo nulos. Se podrían borrar*


### Licencia

Los datos siguen la normativa de la Autoridad Laboral Europea (ELA)