# Síntesis del proyecto

## 1. Dataset publicado en Hugging Face

El proyecto se apoya en un dataset de **ofertas laborales en España**, recopiladas a través del portal EURES y fuentes autonómicas oficiales. La recolección se realizó durante un periodo de **tres meses**, lo que permite observar patrones temporales y sectoriales en un intervalo representativo del mercado laboral.

El dataset contiene más de **7.000 registros**, cada uno estructurado en campos que describen las características principales de las ofertas. Entre ellos destacan:

- **url**: enlace a la oferta original.  
- **fecha_publicacion**: día en que la oferta fue publicada.  
- **fecha_limite**: fecha de cierre para postular.  
- **titulo**: nombre del puesto ofertado.  
- **empresa**: entidad contratante.  
- **ocupacion**: categoría profesional principal.  
- **descripcion**: texto completo de la oferta, sin datos personales.  
- **pais** y **region/provincia**: localización geográfica de la oferta.  
- **tipo_contrato**: modalidad laboral (temporal, indefinido, etc.).  

El dataset se encuentra disponible en formatos **CSV y Parquet**, lo que facilita tanto su exploración inicial como su integración en procesos de minería de datos. Además, la documentación incluida en el repositorio describe cada campo y asegura la reproducibilidad del trabajo.

En síntesis, este dataset constituye la **base empírica del proyecto**, ya que permite analizar la evolución de las ofertas laborales en España, identificar patrones estacionales (como la campaña navideña en logística), sectoriales (como la diversidad temática en hostelería y turismo) y semanales (como el descenso de publicaciones en fines de semana). Su publicación en Hugging Face garantiza accesibilidad y transparencia, convirtiéndose en un recurso útil para futuros análisis del mercado laboral.

## 2. Indicadores calculados y síntesis de la hipótesis planteada

El análisis exploratorio y descriptivo del dataset se estructuró en torno a cuatro indicadores principales: **volumen temporal de publicaciones**, **polaridad emocional**, **tópicos latentes** y **clasificación sectorial asistida por modelos de lenguaje**. Estos indicadores permiten caracterizar el comportamiento del mercado laboral durante el periodo analizado y sirven como base para la formulación de las hipótesis del proyecto.

En primer lugar, el **volumen temporal de ofertas** proporciona información sobre la dinámica de publicación a lo largo de los meses y semanas. Este indicador permite detectar picos de actividad asociados a determinados sectores y momentos del trimestre, así como variaciones sistemáticas entre días laborables y fines de semana.

El análisis de **polaridad emocional** se realizó mediante tres modelos distintos con el fin de obtener una estimación robusta del tono presente en las descripciones de las ofertas. Aunque el lenguaje de estos textos tiende a ser neutro, este indicador permite observar matices entre sectores y complementar la interpretación temática.

La **modelización de tópicos mediante LDA** permitió identificar diez temas recurrentes en el corpus textual. La distribución de estos tópicos entre sectores y su frecuencia relativa ofrecen una visión estructurada del contenido de las ofertas, facilitando la formulación de hipótesis sobre la relación entre ciertos tópicos y áreas profesionales concretas.

Por último, la **clasificación sectorial mediante modelos de lenguaje**, implementada a través de tres clasificadores y un voting classifier final, permitió asignar cada oferta a uno de los diez sectores definidos. Este indicador proporciona una base sistemática para analizar la presencia de tópicos por sector y estudiar patrones temporales diferenciados.

A partir de estos indicadores se plantearon diversas hipótesis:
1. Las ofertas del sector logístico presentan mayor actividad en el inicio de diciembre, en preparación para la campaña navideña.
2. Los sectores de Hostelería y Turismo muestra una mayor dispersión temática con respecto a los tópicos
3. Los fines de semana aparentan un claro descenso de las ofertas laborales.

## 3. Análisis temporal y resultados principales

### Estacionariedad, estacionalidad y tendencia de las series

La estacionariedad de las series correspondientes a los distintos tópicos se evaluó mediante el test de Dickey-Fuller (ADF). Los resultados indican que todos los tópicos, excepto el tópico 4, rechazan la hipótesis nula, con p-valores inferiores al umbral del 5%  y por tanto las series se han considerado estacionarias.

El tópico 4 constituye la única excepción, presentando un p-valor elevado, lo que evidencia la presencia no estacionariedad en la media y varianza de la serie a lo largo del tiempo. Por este motivo, se aplicó una diferenciación de primer orden (d = 1), tras la cual el test ADF confirma la estacionariedad de la serie transformada. Esta decisión se justifica por el comportamiento visual de la serie que muestra oscilaciones irregulares.

La estacionalidad se analizó mediante los correlogramas ACF y PACF. En los tópicos 1, 3 y 4 se observa un patrón persistente de autocorrelación en los retardos 7 y 14, indicando la presencia de un ciclo semanal bien definido. Este resultado es consistente con el análisis descriptivo entre días laborables y fines de semana, donde se detectan diferencias sistemáticas en los valores medios de estos tópicos. En consecuencia, estas series se consideran estacionales con un período de 7 días.

Por el contrario, los tópicos 0, 2, 5, 6 y 7 no muestran picos estacionales recurrentes en los correlogramas. Aunque algunos presentan dependencia de corto plazo (principalmente en el retardo 1), esta no se traduce en una estructura cíclica, por lo que no se justifica la inclusión de componentes estacionales en sus modelos.

El análisis de tendencia refuerza estas conclusiones. En los tópicos 1 y 3, la descomposición estacional revela picos abruptos concentrados en noviembre y diciembre respectivamente, asociados a eventos puntuales de alta actividad, pero sin una tendencia sostenida en el tiempo, ya que las series retornan posteriormente a sus niveles habituales. En el tópico 4, la tendencia aparece irregular y volátil, coherente con su carácter inicialmente no estacionario, aunque sin una dirección clara. El resto de tópicos oscilan alrededor de una media estable, confirmando la ausencia de tendencia estructural.

---

### Justificación de los parámetros SARIMAX

La selección de los parámetros de los modelos SARIMAX se realizó de forma coherente con los resultados obtenidos en el análisis de estacionariedad, estacionalidad y correlogramas. En los tópicos que presentan estacionalidad persistente (1, 3 y 4), el período estacional se fijó en s = 7, reflejando el ciclo semanal detectado en los ACF/PACF y corroborado por el análisis entre semana y fin de semana.

En cuanto a la integración no estacional, se estableció d = 0 para todos los tópicos que el test ADF clasifica como estacionarios, y d = 1 exclusivamente para el tópico 4, al ser la única serie que requiere diferenciación para alcanzar la estacionariedad.

Respecto a la parte estacional, se consideró D = 1 únicamente en aquellas series donde la estacionalidad es persistente y dominante (tópicos 1, 3 y 4). Esta decisión se basa en que la diferenciación estacional permite eliminar el patrón semanal sistemático observado en los correlogramas, facilitando que el modelo capture la dinámica De la serie sin verse condicionado por ciclos repetitivos. En los tópicos sin estacionalidad no introducimos una diferenciación estacional ya que podría inducir sobreajuste y pérdida de información.

Los parámetros p, q, P y Q de cada modelo se seleccionaron mediante un procedimiento automático basado en auto-SARIMA, eligiendo aquellas combinaciones que minimizan el criterio de información AIC, lo que garantiza un equilibrio entre capacidad explicativa y complejidad del modelo. No obstante, los valores obtenidos quedan respaldados por el análisis manual de los correlogramas ACF y PACF de cada serie. En la parte no estacional, los parámetros p y q toman valores bajos (p ∈ {1,2} y q ∈ {0,1}), coherentes con el hecho de que la mayoría de los tópicos presentan una memoria temporal limitada y una dependencia de corto plazo, sin estructuras autorregresivas complejas. En cuanto a la componente estacional, los parámetros P y Q se fijan en 0 en todos los modelos SARIMA aplicados a los tópicos, ya que, aunque se detecta una estacionalidad semanal clara, los correlogramas no muestran cortes abruptos ni picos dominantes en los retardos estacionales que justifiquen la inclusión de términos autorregresivos o de media móvil estacionales. La estacionalidad observada se explica adecuadamente mediante la diferenciación estacional (D = 1), sin necesidad de añadir dinámica estacional adicional, lo que permite evitar sobreajuste.

Los resultados muestran que los modelos SARIMA y SARIMAX para los tópicos 1, 3 y 4 capturan adecuadamente la fase del ciclo semanal, aunque presentan dificultades para reproducir la magnitud de los picos extremos. Esta limitación sugiere que, aunque la estructura temporal está bien especificada, una parte importante de la variabilidad responde a ruido no modelable.

---

### Resultados del modelo LSTM

Como contraste a los modelos lineales, se entrenaron modelos LSTM para cada tópico con el objetivo de evaluar si un enfoque no lineal podía mejorar el rendimiento predictivo. La comparación de resultados muestra que las LSTM no proporcionaron una mejora significativa en las métricas de rendimiento (RMSE o MAE) en comparación con los modelos SARIMAX.

En todos los tópicos, las predicciones generadas por las LSTM tienden a ser suaves y a converger hacia valores medios, sin reproducir los picos abruptos observados en los datos reales, especialmente durante el mes de diciembre. Este comportamiento es similar al observado en los modelos SARIMA y refuerza la idea de que la volatilidad extrema está dominada por eventos externos y no por patrones temporales aprendibles.

En consecuencia, se concluye que el valor añadido del modelo neuronal no compensa su mayor complejidad y coste computacional, dado el tamaño del conjunto de datos y la naturaleza altamente ruidosa de las series analizadas.

---

### Influencia cruzada de las variables exógenas

La influencia cruzada de las variables exógenas sectoriales se analizó mediante modelos SARIMAX, incorporando la actividad de los distintos sectores como regresores externos. Los resultados muestran un comportamiento heterogéneo según el tópico analizado.

En los tópicos 1 y 4, la inclusión de variables exógenas no aporta mejoras relevantes, ya que ningún sector presenta coeficientes estadísticamente significativos. Esto indica que la dinámica temporal de estos tópicos está principalmente determinada por su propia estructura interna y por eventos puntuales no capturados por los sectores considerados. En estos casos la actividad sectorial no introduce información adicional interpretable. 

El tópico 3 constituye el caso más relevante desde el punto de vista de exogeneidad. En este tópico se identifican dependencias estadísticamente significativas con los sectores de Tecnología y Telecomunicaciones, Construcción e Inmobiliaria y Administración y Finanzas, todos ellos con coeficientes positivos. Esto sugiere que el tópico 3 no responde únicamente a su dinámica autorregresiva, y está condicionado por la evolución de sectores con periodos de mayor actividad laboral.

En los tópicos 2 y 6, los modelos SARIMAX muestran una aportación exógena muy limitada. Aunque aparece algún coeficiente significativo de forma aislada, su magnitud reducida y su signo no permiten establecer una relación estructural clara. En conjunto, estos tópicos parecen estar dominados por ruido y variaciones internas, sin una dependencia temporal robusta respecto a los sectores analizados.

De forma global, el análisis de exogeneidad indica que solo en casos concretos, la influencia exógena sectorial resulta relevante, siendo el tópico 3 el único caso donde las variables externas aportan una mejora clara en la capacidad explicativa. En la mayoría de tópicos, su comportamiento está poco condicionado por la evolución de los sectores.


## Conclusiones del proyecto

