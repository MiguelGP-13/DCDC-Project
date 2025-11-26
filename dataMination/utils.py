# utils.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf
import numpy as np
from statsmodels.tsa.stattools import adfuller

def cargar_dataset(path="../empleos-espanoles-eures-2025-numerico.csv", acotar= False, fecha=None):
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="%d/%m/%Y")
    if acotar:
        if not fecha:
            fecha = "2026-01-15"
        df = df[df["timestamp"] < pd.Timestamp(fecha)]
    return df

def agrupar(df, indicador, freq="D"):
    """
    Agrupa el dataset por frecuencia temporal y asegura que no haya huecos.
    freq="D" -> diario
    freq="W" -> semanal
    """
    # Agrupar solo la columna numérica que nos interesa
    series = df.groupby(pd.Grouper(key="timestamp", freq=freq))[indicador].mean()

    # Asegurar que el índice tenga todas las fechas en la frecuencia indicada
    series = series.asfreq(freq)

    # Rellenar huecos con 0
    series = series.fillna(0)

    return series



def graficar_evolucion(series, indicador, freq_label):
    plt.figure(figsize=(12,6))
    sns.lineplot(x=series.index, y=series.values)
    plt.title(f"Evolución {freq_label} del indicador: {indicador}")
    plt.xlabel("Tiempo")
    plt.ylabel("Valor promedio")
    plt.grid(True)
    plt.show()

def entrenar_modelo(series, indicador, freq_label):
    train_size = int(len(series) * 0.8)
    train, test = series.iloc[:train_size], series.iloc[train_size:]

    model = ExponentialSmoothing(train, trend="add", seasonal=None)
    fit = model.fit()
    pred = fit.forecast(len(test))

    rmse = np.sqrt(mean_squared_error(test, pred))
    mae = mean_absolute_error(test, pred)

    print(f"[{freq_label}] {indicador} -> RMSE: {rmse:.2f}, MAE: {mae:.2f}")

    plt.figure(figsize=(12,6))
    plt.plot(train.index, train, label="Entrenamiento")
    plt.plot(test.index, test, label="Real")
    plt.plot(test.index, pred, label="Predicción", linestyle="--")
    plt.title(f"Predicción vs Real ({freq_label}) - {indicador}")
    plt.xlabel("Tiempo")
    plt.ylabel("Valor")
    plt.legend()
    plt.grid(True)
    plt.show()

def graficar_autocorrelacion(series, indicador, freq_label):
    plot_acf(series.dropna(), lags=20)
    plt.title(f"Autocorrelación ({freq_label}) - {indicador}")
    plt.show()


def generar_random_walk(step_n=200, dims=1, step_set=[-1, 0, 1], plot=False):
    """
    Genera un random walk.
    
    Parámetros:
    - step_n: número de pasos
    - dims: dimensiones (normalmente 1)
    - step_set: posibles valores de cada paso
    - plot: si True, dibuja el random walk
    
    Retorna:
    - path: array con la trayectoria del random walk
    """

    # Generamos step_n pasos directamente
    steps = np.random.choice(a=step_set, size=(step_n, dims))
    # Acumulamos desde cero
    path = steps.cumsum(0).ravel()

    if plot:
        plt.figure(figsize=(12,5), dpi=200)
        plt.plot(path)
        plt.title("Random Walk")
        plt.grid(True)
        plt.show()

    return path



def generar_ruido_blanco(n=200, loc=0, scale=1, plot=False):
    """
    Genera una serie de ruido blanco.
    
    Parámetros:
    - n: número de observaciones
    - loc: media de la distribución normal
    - scale: desviación estándar de la distribución normal
    - plot: si True, dibuja la serie
    
    Retorna:
    - wn: array con la serie de ruido blanco
    """
    wn = np.random.normal(loc=loc, scale=scale, size=n)

    if plot:
        plt.figure(figsize=(12,5), dpi=200)
        plt.plot(wn)
        plt.title("Ruido Blanco")
        plt.grid(True)
        plt.show()

    return wn
