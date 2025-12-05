# Minería de Datos Complejos

## Hipótesis: 
1. Las ofertas del sector logístico presentan mayor actividad en el inicio de diciembre, en preparación para la campaña navideña.
2. Los sectores de Hostelería y Turismo muestra una mayor dispersión temática con respecto a los tópicos
3. Los fines de semana aparentan un claro descenso de las ofertas laborales.

## Técnicas aplicadas:

### Análisis preliminar y preparación de datos:
Hemos empezado previsualizando el comportamiento temporal de todos los indicadores: tópicos, sector y sentimiento.
Para ello decidimos agrupar por días, calcular la media diaria de los valores.
![Tendencia temporal de todos los indicadores](results/AllIndicators.png)

Vimos una gran similitud entre varias gráficas, sobretodo en los sectores, donde se puede ver que, por ejemplo, `Tecnología y Telecomunicaciones`, se parece mucho a `Comercio y Ventas` o `Industria y Manufactura` con `Logística y Transporte`, compartiendo picos, pudiendo indicar correlación.

Viendo al alta correlación entre los temas, decidimos centrarnos en los tópicos.

### Busqueda estacionariedad:
Se ha utilizado el test de estacinariedad (ADF), y se ha descubierto que el tópico 4 es el único no estacionario. Hemos aplicado nuevamente el ADF a su diferenciación y hemos determinado que sólamente es necesario 1 diferenciación para lograr la serie estacionaria.


### Busqueda estacionalidad:
Para obtener información sobre la estacionalidad, hemos calculado y gráficado el ACF y PACF para todos los tópicos.

### Análisis de Tendencia:

Para analizar la tendencia, hemos aplicado la decomposición estacional para los tópicos que pueden contener estacionalidad y la media movil para buscar la tendencia en el resto de tópicos.

### Suavizado exponencial
Para los tópicos 1, 3 y 4, los que tienen estacionalidad, al tener un ciclo de 7 días, hemos usado Holt-Winters (Triple Suavizado).
Para el resto de tópicos ,como no tienen ni estacionalidad, ni estacionariedad ni tendencia, se ha aplicado el Suavizado Exponencial Simple, que simplemente estima filtrando el ruido.

### SARIMA
Los tópicos estacionales son siempre cada 7 dias, por tanto el valor estacional es siempre 7. Para todos los topicos salvo el 4 (donde d=1), el valor de d=0 ya que no requiere diferenciación para lograr ser estacionaria.

Para determinar los parámetros óptimos (p, q, P, Q) de cada modelo, hemos implementado una Grid Search que evalúa múltiples combinaciones respetando las restricciones de integración y estacionalidad de cada tópico.

La selección del mejor modelo se ha basado en minimizar el Criterio de Información de Akaike (AIC). Hemos preferido el AIC sobre el BIC porque nuestro objetivo es maximizar la capacidad predictiva a corto plazo. El AIC estima mejor el error de predicción futuro y evita el riesgo de seleccionar modelos demasiado simples que el BIC podría favorecer al penalizar, además nuestra muestra no es demasido densa y el BIC tiende a tener mejor desempeño cuando la muestra es grande, para evitar el sobreajuste.

### SARIMAX
Por último hemos aplicado SARIMAX, para buscar exogenias con los sectores de las ofertas en los tópicos 1,3 y 4.

### LSTM 
Además de los modelos clásicos, se ha entrenado un modelo de red neuronal LSTM por cada tópico con tres objetivos:

1. Comparar su capacidad de ajuste frente a los modelos lineales.
2. Detectar días anómalos a partir del error de predicción.
3. Generar predicciones a corto plazo (10 días) para estudiar el comportamiento futuro.

Para cada `topico_i`:

- Se construye una serie diaria mediante la media por día.
- Se escalan los valores a \([0,1]\) con `MinMaxScaler`.
- Se generan ventanas de 7 días como entrada y el valor del día siguiente como salida.
- Se entrena una LSTM con 100 unidades y una capa densa final, optimizada con Adam y pérdida MSE.

Sobre estas predicciones se realiza después:
- la detección de anomalías (Top-10 errores absolutos por tópico),
- la comparación de periodos (entrenamiento vs test),
- y la predicción futura a 10 días vista.


## Resultados

### Busqueda estacionariedad:
Utilizando el test de estacinariedad (ADF), hemos visto que todos los tópicos menos el 4 son estacionarios, por lo que solo se ha integrado el tópico 4, conseguiendo que también sea estacionario.
| Tópico   | ADF Statistic        | p-value | Estacionaria |
|----------|----------------------|---------|--------------|
| topico_0 | -9.067006715956293   | 0.000   | True         |
| topico_1 | -3.4636076305279686  | 0.009   | True         |
| topico_2 | -6.525953686345409   | 0.000   | True         |
| topico_3 | -8.377697691552502   | 0.000   | True         |
| topico_4 | -1.9993058288520613  | 0.287   | False        |
| topico_5 | -6.454042146456745   | 0.000   | True         |
| topico_6 | -9.037405829997091   | 0.000   | True         |
| topico_7 | -8.698242667419844   | 0.000   | True         |

El número mínimo de diferenciaciones necesarias para hacer la serie estacionaria corresponde únicamente al **tópico 4**, donde se requiere $\mathbf{d=1}$. Este es el valor que debe utilizar en su modelo ARIMA para dicho caso, es decir, $\text{ARIMA}(p,\mathbf{1},q)$. Para el resto de los tópicos, al ser ya estacionarios, el valor adecuado es $\text{ARIMA}(p,0,q)$.

### Busqueda estacionalidad:

El único tópico que el test de Dickey-Fuller identificó como no estacionario fue el **tópico 4** con un p-value muy alto de 0.872. Esto indica que la serie debe ser tratada con diferenciación.

Al observar sus correlogramas (ACF/PACF), destaca un patrón de dependencia estacional significativa cada 7 y 14 días. Para capturar esta estructura, un suavizado exponencial simple no es suficiente.

Los **tópicos 1 y 3** presentan un p-value de 0.000 en el test ADF, lo que confirma que las series son estacionarias.

Sin embargo, al analizar sus correlogramas, observamos una estacionalidad clara cada 7 días en ambos casos.  Esto nos indica que su comportamiento parece estar regido por un ciclo semanal.

El resto de Tópicos (0, 2, 5, 6, 7) no parecen estacionarios, aunque algunos muestran una ligera influencia del día inmediatamente anterior (como el 2 y el 5), esto refleja una memoria muy corta y no una estructura cíclica que justifique un modelo estacional complejo.

### Análisis de Tendencia:

En lo referente a los **Tópicos 1 y 3**, la descomposición captura picos significativos de actividad (en noviembre para el Tópico 1 y diciembre para el Tópico 3), que se reflejan como subidas bruscas y aisladas en la tendencia. En el caso del Tópico 3, esto sugiere la presencia de una anomalía específica o un shock exógeno, respaldando la hipótesis planteada en el estudio: *"Las ofertas del sector logístico presentan mayor actividad en el inicio de diciembre, en preparación para la campaña navideña"*. Con respecto al Tópico 1 no podemos añadir información adicional sobre sus causas por que no hay nigún sector determinante ni plateamos ninguna hipótesis respeto a el. Descartando estos eventos puntuales, ninguna de las dos series muestra una tendencia significativa a largo plazo, retornando a sus niveles base tras los periodos de mayor actividad.

Respecto al **Tópico 4**, se observa una tendencia "nerviosa" que confirma la no estacionariedad estadística de la serie. Sin embargo, la tendencia oscila constantemente sin una dirección determinada y, por tanto, consideramos que no se detecta una tendencia sostenida de crecimiento o decrecimiento.

Finalmente, de carácter general, el **resto de tópicos (0, 2, 5, 6 y 7)** no presentan ninguna tendencia direccional a destacar. A diferencia de los casos anteriores, estos tópicos exhiben un comportamiento estacionario en media, oscilando alrededor de valores constantes con desviaciones similares entre sí. Aunque se observan picos puntuales de volatilidad, estos no se traducen en cambios estructurales y son considerados como ruido.

### Suavizado exponencial
Para los tópicos 1, 3 y 4, los que tienen estacionalidad, al tener un ciclo de 7 días, hemos usado Holt-Winters (Triple Suavizado).
Para el resto de tópciso,como no tienen ni estacionalidad, ni estacionariedad ni tendencia, se ha aplicado el Suavizado Exponencial Simple, que simplemente estima filtrando el ruido.

#### Resultados Holt-Winters:
![Resultado Holt-Winters del tópico 1](results/HoltWinters1.png)
![Resultado Holt-Winters del tópico 3](results/HoltWinters3.png)
![Resultado Holt-Winters del tópico 4](results/HoltWinters4.png)

Para los **Tópicos 1, 3 y 4**, al aplicar el modelo de triple suavizado (Holt-Winters), el modelo logra capturar correctamente la fase del ciclo (acierta en las subidas y bajadas semanales), vuelve a corroborar la estacionalidad de 7 días. Sin embargo, la predicción no es perfecta en cuanto a magnitud por que el modelo tiende a ser conservador y el componente aleatorio tiene un peso muy significativo que cuesta predecir con exactitud. 

Para el **resto de tópicos (0, 2, 5, 6 y 7)**, la aplicación del Suavizado Exponencial Simple arroja una predicción plana. Este resultado tiene sentido ya que al no considerar ni tendencia ni estacionalidad, el modelo determina que la mejor predicción posible es el nivel medio actual. La gran diferencia entre la predicción y los datos reales ilustra un nivel de ruido muy intenso, lo que nos puede dar a pensar que existe alguna influencia exogenea en las series. 

### SARIMA
#### Tópico 4
El modelo SARIMA seleccionado `(1, 1, 1)x(0, 1, 0, 7)` arroja resultados muy similares a los obtenidos previamente con el suavizado exponencial. Aunque el modelo identifica la periodicidad y la dirección de los cambios, **falla sistemáticamente en capturar la magnitud de la volatilidad**, como sucedía con el Holt-Winters. La predicción incapaz de alcanzar los picos extremos de la serie real. Esto evidencia que la complejidad adicional del modelo SARIMA no aporta una ventaja frente al suavizado exponencial en nuestro caso, ya que el componente de ruido  es tan dominante que limita la precisión de cualquier modelo.
![Predicción SARIMAX del tópico 4](results/SARIMA4.png)

#### Tópicos 1 y 3
De manera análoga, los modelos SARIMA para los Tópicos 1 y 3 muestran las mismas limitaciones que sus contrapartes de suavizado, solo se detecta una pequeña mejora en el tópico 1. Capturan el ciclo base, pero se ven desbordados por la variabilidad de la serie.

A pesar de los picos exógenos observados (noviembre/diciembre), hemos decidido no utilizar modelos SARIMAX, ya que estos eventos puntuales (campaña navideña y Black Friday) introducen unos valores que no responden con la dinámica interna de la serie. Podemos respaldar que la dificultad de predicción no es un fallo en los modelos, sino una característica intrínseca de series que no se puede modelar ya que están afectadas por eventos de alto impacto.

![Predicción SARIMAX del tópico 1](results/SARIMA1.png)
![Predicción SARIMAX del tópico 3](results/SARIMA3.png)

### SARIMAX

Tanto en los tópicos 1 y 4, al aplicar el modelo SARIMA que mejor se ajusta a cada serie, observamos que la inclusión de variables exógenas no aporta información relevante, ya que todos los coeficientes asociados presentan p-valores superiores a 0.05, lo que indica ausencia de significancia estadística.

En cambio, el tópico 3 sí se detectan dependencias respecto a algunas variables exógenas. Los sectores que muestran coeficientes con p-valores inferiores a 0.05 son:

- Sanitario y Salud  
- Construcción e Inmobiliaria  
- Administración y Finanzas  

Los 3 con coeficientes positivos, que indican que un aumento en la actividad de estos sectores se asocia con un incremento en el valor del tópico 3

Esto significa que la dinámica del tópico 3, relacionado con términos como *alimentario, casa, incapacidad, bajo, flexibilidad, telefónico, reconocido, asignado, cuadrante, logística*, no depende únicamente de su propia estructura temporal, sino que está condicionada por la actividad en estos sectores. La incorporación de estas variables externas mejora la capacidad explicativa del modelo, indicando que los cambios en dichos sectores pueden estar asociados con variaciones significativas en el comportamiento del tópico.

| Sector                        | Coeficiente | p-valor | Significancia |
|-------------------------------|-------------|---------|---------------|
| Sanitario y Salud             | 0.2077      | 0.003   | Sí            |
| Construcción e Inmobiliaria   | 0.8271      | 0.006   | Sí            |
| Administración y Finanzas     | 0.8660      | 0.015   | Sí            |
| Hostelería y Turismo          | 0.1285      | 0.843   | No            |
| Educación y Formación         | 0.1858      | 0.314   | No            |
| Tecnología y Telecomunicaciones | 0.7366    | 0.165   | No            |
| Industria y Manufactura       | 0.3980      | 0.416   | No            |
| Comercio y Ventas             | 0.4311      | 0.439   | No            |
| Logística y Transporte        | 0.3918      | 0.301   | No            |
| Cultura, Arte y Ocio          | -0.8352     | 0.478   | No            |
*Resultado SARIMAX para el tópico 3*

En el caso del tópico 2, la estimación del modelo SARIMAX tampoco muestra una aportación relevante de las variables exógenas. La mayoría de sectores presentan p-valores muy superiores a 0.05, lo que indica ausencia de significancia estadística y, por tanto, falta de dependencia temporal respecto a su actividad. El único sector con un coeficiente significativo es Administración y Finanzas (p = 0.039), aunque su efecto es negativo y de magnitud moderada, por lo que no resulta interpretable en términos de una relación estructural. En conjunto, el modelo sugiere que la dinámica del tópico 2 está dominada por ruido y variaciones internas, sin que los sectores analizados expliquen su comportamiento temporal.

En el caso del tópico 6, el modelo SARIMAX muestra que el coeficiente asociado al sector Administración y Finanzas no es significativo (p = 0.530), lo que indica que su actividad no explica la evolución temporal del tópico. La mayoría de sectores presentan igualmente p-valores elevados, evidenciando la ausencia de relaciones temporales consistentes. El único coeficiente significativo corresponde al sector Sanitario y Salud (p = 0.012), aunque su efecto es negativo y de magnitud reducida, por lo que no resulta interpretable como una relación estructural.

### LSTM

#### Detección de anomalías mediante el residuo de predicción (LSTM)
El modelo LSTM genera una predicción diaria basada en los 7 días anteriores.
A partir de esta predicción, se calcula el **residuo**:

\[
\text{residuo}_t = y^{real}_t - y^{pred}_t
\]

Los días con mayor error absoluto se consideran **anomalías**, ya que se alejan del
comportamiento “esperado” aprendido por el modelo.

|    Fecha   | Valor real |  Predicción |  Residuo  | Residuo (absoluto)|   
|------------|------------|-------------|-----------|-------------------|                                      
| 2025-12-27 | 0.000000   | 0.103619    | -0.103619 | 0.103619          |   
| 2026-01-02 | 0.183208   | 0.101527    | 0.081681  | 0.081681          | 
| 2026-01-04 | 0.047996   | 0.118739    | -0.070743 | 0.070743          | 
| 2026-01-03 | 0.174218   | 0.104754    | 0.069464  | 0.069464          | 
| 2025-12-26 | 0.142153   | 0.098815    | 0.043338  | 0.043338          | 
| 2025-12-22 | 0.136790   | 0.094768    | 0.042022  | 0.042022          | 
| 2025-12-24 | 0.123790   | 0.094073    | 0.029717  | 0.029717          | 
| 2026-01-01 | 0.128888   | 0.099869    | 0.029019  | 0.029019          | 
| 2025-12-29 | 0.128409   | 0.100622    | 0.027787  | 0.027787          | 
| 2026-01-05 | 0.097385   | 0.114487    | -0.017103 | 0.017103          | 
*Ejemplo de anomalías LSTM para topico_1*

![Anomalías LSTM – Tópico 1](results/imagen_topico1_anomalias.png)
![Anomalías LSTM – Tópico 3](results/imagen_topico3_anomalias.png)
![Anomalías LSTM – Tópico 4](results/imagen_topico4_anomalias.png)
![Anomalías LSTM – Tópico 5](results/imagen_topico5_anomalias.png)



**Observación clave:**  
En TODOS los tópicos, el día **2025-12-27** aparece como anomalía principal.  
Esto indica una caída excepcional del valor en un día donde el modelo esperaba actividad normal, probablemente asociada a eventos navideños.

#### Predicción futura: horizonte de 10 días
La LSTM genera predicciones autoregresivas para los 10 días posteriores al final de la serie.
En todos los tópicos se observa un patrón común:
- El modelo proyecta valores suaves y estables, sin replicar los picos bruscos de diciembre.
- En la mayoría de tópicos la predicción converge a un valor cercano al promedio reciente.
- Tópicos como topico_5 muestran mayor variabilidad por haber presentado picos extremos.

![Predicción futura – Tópico 0](results/topico0_pred_future.png)
![Predicción futura – Tópico 1](results/topico1_pred_future.png)
![Predicción futura – Tópico 2](results/topico2_pred_future.png)
![Predicción futura – Tópico 3](results/topico3_pred_future.png)
![Predicción futura – Tópico 4](results/topico4_pred_future.png)
![Predicción futura – Tópico 5](results/topico5_pred_future.png)
![Predicción futura – Tópico 6](results/topico6_pred_future.png)
![Predicción futura – Tópico 7](results/topico7_pred_future.png)

**Observaciones:** 
El comportamiento esperado para la mayoría de tópicos es estabilidad alrededor del nivel medio de cada serie.
Esto concuerda con el patrón estacional detectado: diciembre muestra mayores fluctuaciones por motivos festivos, que después se normalizan.

#### Análisis mensual: detección de estacionalidad
Para identificar patrones a medio plazo, se calculó la media mensual de cada tópico.

|   Mes   | topico_0 | topico_1 | topico_2 | topico_3 | topico_4 | topico_5 | topico_6 | topico_7 |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|
| 2025-10 | 0.124361 | 0.116303 | 0.151883 | 0.123794 | 0.130493 | 0.121140 | 0.109849 | 0.122176 |
| 2025-11 | 0.128488 | 0.114860 | 0.156895 | 0.105462 | 0.140792 | 0.108302 | 0.116768 | 0.128432 |
| 2025-12 | 0.107523 | 0.100321 | 0.161340 | 0.136098 | 0.130987 | 0.104537 | 0.120979 | 0.138215 |
| 2026-01 | 0.133089 | 0.122967 | 0.088293 | 0.131431 | 0.145961 | 0.174096 | 0.099001 | 0.105162 |

**Observaciones:** 
Diciembre es el mes más atípico: Algunos tópicos suben fuerte (3, 7) mientras otros bajan notablemente (0, 1, 5).
Enero muestra un “rebote” general tras las fiestas, coherente con las predicciones LSTM.

#### Análisis entre semana vs fin de semana: detección de estacionalidad
Para entender patrones semanales, se calculó la media en días laborables vs fines de semana:

| Tópico    | Entre semana | Fin de semana  |
|-----------|--------------|----------------|
| topico_0  | 0.122036     | 0.117505       |
| topico_1  | 0.117246     | 0.094844       |
| topico_2  | 0.145671     | 0.167342       |
| topico_3  | 0.107713     | 0.159866       |
| topico_4  | 0.149010     | 0.100371       |
| topico_5  | 0.108139     | 0.133921       |
| topico_6  | 0.120522     | 0.101149       |
| topico_7  | 0.129662     | 0.125003       |

El análisis semanal se complementa con las correlaciones más altas entre tópicos y sectores:

|               col1              |   col2   | correlacion |
|---------------------------------|----------|-------------|
| Sanitario y Salud               | topico_2 | 0.2506      |
| Administración y Finanzas       | topico_6 | 0.2318      |
| Hostelería y Turismo            | topico_1 | 0.1732      |
| Tecnología y Telecomunicaciones | topico_6 | 0.1503      |
| Educación y Formación           | topico_0 | 0.1247      |

**Observaciones:**
- **tópico_6**, que es claramente más fuerte entre semana, aparece correlado con *Administración y Finanzas* y *Tecnología y Telecomunicaciones*, sectores típicamente de actividad laboral intensa.
- **tópico_2**, más activo en fin de semana, se asocia a *Sanitario y Salud*, un sector con dinámicas de trabajo distintas del ciclo laboral estándar.
- **tópico_1**, también más fuerte de lunes a viernes, correlaciona positivamente con *Hostelería y Turismo* (0.1732), aunque este sector suele tener picos en fin de semana. Esto indica que el tópico captura elementos administrativos y no exclusivamente actividades operativas del sector.


## Discusión

Hay algunos resultados obtenidos previamente que han  sido refutados:

- En relación con el resultado “El tópico 2 aparece con mayor frecuencia en el sector Sanitario y Salud” queda refutada a la luz del modelo SARIMAX estimado, ya que el coeficiente asociado a dicho sector no resulta significativo (p = 0.742) y, en general, la mayoría de sectores presentan p-valores elevados que indican ausencia de dependencia temporal, siendo únicamente el sector de Administración y Finanzas significativo (p = 0.039) con un efecto negativo que además contradice el resultado obtenido inicialmente.

- Por otro lado, el resultado “El tópico 6 predomina en el sector de Administración y Finanzas” tampoco encuentra apoyo en los resultados obtenidos. El análisis confirma que el tópico 6 presenta un comportamiento estable y autónomo, sin influencia sectorial relevante, ya que el sector propuesto en este resultado no muestra significancia estadística y el resto de sectores tampoco aportan dependencia temporal interpretable. El tópico 6 presenta un patrón estable entre semana, pero no dependiente de Administración y Finanzas. La dinámica del tópico 6 es autónoma y con poca influencia externa.

### Hipótesis

El análisis temporal realizado sobre los distintos tópicos y sectores permite evaluar las hipótesis planteadas en la Entrega 2. En conjunto, los resultados muestran patrones coherentes con la dinámica del mercado laboral, aunque también revelan limitaciones importantes derivadas del ruido y la influencia de eventos exógenos.

1. Por otro lado, la hipótesis “Las ofertas del sector logístico presentan mayor actividad a inicios de diciembre”, los resultados la apoyan claramente. El tópico 3, estrechamente vinculado a logística, muestra un pico abrupto en diciembre que coincide con la campaña navideña y el periodo de Black Friday. Tanto la descomposición estacional como los modelos SARIMA y SARIMAX reflejan este comportamiento, indicando que se trata de un shock exógeno significativo y consistente con la dinámica del sector.


2. Respecto a la hipótesis “Hostelería y Turismo muestra mayor dispersión temática”, los resultados la apoyan parcialmente. Aunque el análisis temporal no mide directamente la dispersión, sí se observa que este sector no aparece como exógeno significativo en ningún modelo SARIMAX, lo que sugiere que su actividad no explica la dinámica de ningún tópico concreto. Esto es coherente con una mayor heterogeneidad temática, pero esto sucede con la mayoría de los sectores.

![Distribución de ofertas por día](results/DistribucionPorSector.png)

3. Finalmente, la hipótesis “Los fines de semana presentan un descenso claro en las ofertas laborales” queda respaldada visualmente, ya que la gráfica correspondiente muestra una caída evidente en sábado y domingo.
En el análisis “Entre semana vs fin de semana” confirma que los tópicos 2, 3, 5 y 7, más asociados a ocio o actividades no estrictamente laborales, aumentan en estos días, lo cual refuerza la estructura del comportamiento semanal.

![Distribución de ofertas por día](results/Semanal.png)


## Limitaciones y posibles mejoras

El estudio presenta varias limitaciones que condicionan la solidez de las conclusiones:

- **Cantidad limitada de datos**: El periodo temporal analizado es relativamente corto, lo que dificulta la detección de patrones estacionales complejos y reduce la capacidad predictiva de los modelos. Esto afecta especialmente a los tópicos con alta volatilidad.
- **Presencia de eventos exógenos**: Fenómenos como Black Friday o la campaña navideña introducen picos abruptos que los modelos no pueden anticipar, limitando su capacidad para capturar la dinámica real de las series.
- **Ruido elevado en la mayoría de tópicos**: Muchos tópicos presentan una variabilidad tan alta que incluso modelos avanzados como SARIMA o Holt-Winters no logran capturar la magnitud de los cambios, lo que reduce la interpretabilidad.

Para mejorar el análisis en futuras entregas, se podrían considerar las siguientes acciones:

- **Ampliar el periodo temporal** para capturar ciclos completos y mejorar la robustez de los modelos.
- **Incorporar variables exógenas adicionales**, como indicadores económicos, festivos o campañas comerciales, para explicar mejor los picos abruptos.
- **Analizar la actividad por día de la semana** con estadísticas descriptivas y modelos con variables dummy, reforzando la hipótesis sobre los fines de semana.
- **Realizar análisis de correlación cruzada (CCF)** entre tópicos y sectores para identificar dependencias temporales no capturadas por los modelos actuales.
