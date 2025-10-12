from playwright.sync_api import sync_playwright
import threading
import time
from langdetect import detect
import glob
import csv
import os

from datetime import datetime

def parse_fecha_limite(dia, mes_texto, anio):
    # Construimos un string tipo "24 octubre 2025"
    fecha_str = f"{dia} {mes_texto} {anio}"
    # Parseamos con strptime (en español funciona si tu locale está en es_ES)
    try:
        fecha = datetime.strptime(fecha_str, "%d %B %Y")
        return fecha.strftime("%d/%m/%Y")
    except ValueError:
        # Si falla porque el locale no reconoce el mes, puedes mapearlo manualmente
        meses = {
            "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
            "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
            "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
        }
        mes_num = meses.get(mes_texto.lower(), "01")
        return f"{dia}/{mes_num}/{anio}"


def log_fallida(url):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ofertas", f"fallidas.txt"), "a", encoding="utf-8") as f:
        f.write(url + "\n")

def append_to_csv(data, archivo_csv):
    campos = [
        "url",
        "fecha_publicacion",
        "fecha_limite",
        "titulo",
        "empresa",
        "ocupacion",
        "educacion",
        "descripcion",
        "pais",
        "region",
        "duracion_jornada",
        "tipo_contrato"
    ]

    # Crear el archivo con cabecera si no existe
    archivo_nuevo = not os.path.exists(archivo_csv)
    with open(archivo_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if archivo_nuevo:
            writer.writeheader()
        writer.writerow(data)

def clean_language(url):
    if url[-2:] == "en":
        url = url[:-2] + "es"
    # print(url)
    return url

def cargar_urls_por_bloques(directorio="links", bloque=1000):
    archivos = sorted(glob.glob(os.path.join(directorio, "*.txt")))
    buffer = []

    for archivo in archivos:
        with open(archivo, "r") as f:
            for linea in f:
                url = linea.strip()
                if url:
                    buffer.append(url)
                    if len(buffer) == bloque:
                        yield buffer
                        buffer = []
    if buffer:
        yield buffer  # Último bloque, aunque tenga menos de 1000

def scrape_offer(url):
    """
    Extrae campos clave de una oferta EURES usando Playwright.
    """
    data = {"url": url}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        time.sleep(1.5)

        def safe_text(selector, by="id"):
            try:
                if by == "id":
                    return page.locator(f"#{selector}").first.inner_text().strip()
                elif by == "class":
                    return page.locator(f".{selector}").first.inner_text().strip()
            except:
                return None

        # Fecha: primero intenta el id normal, si no, prueba el alternativo
        fecha = safe_text("jv-lastModificationDate")
        if not fecha:
            fecha = safe_text("jv-lastModificationDate-no-title")

        data["fecha_publicacion"] = fecha
        data["titulo"] = safe_text("jv-title")
        data["empresa"] = safe_text("jv-details-employer-name")
        data["descripcion"] = safe_text("jv-details-job-description")
        data["pais"] = safe_text("jv-address-country", by="class")
        data["region"] = safe_text("jv-address-region", by="class")
        data["duracion_jornada"] = safe_text("jv-position-schedule-result-0")
        data["tipo_contrato"] = safe_text("jv-position-type-code-result")
        data["ocupacion"] = safe_text("jv-job-categories-codes-result-0")
        data["educacion"] = safe_text("ecl-description-list__definition", by="class")

        try:
            dia = page.locator(".ecl-date-block__day").first.inner_text().strip()
            mes = page.locator(".ecl-date-block__month").first.get_attribute("title").strip()
            anio = page.locator(".ecl-date-block__year").first.inner_text().strip()
            data["fecha_limite"] = parse_fecha_limite(dia, mes, anio)
        except:
            data["fecha_limite"] = None


        browser.close()

    return data


def scrape_batch(urls, batch_size=3, sleep_time=2.5):
    """
    Procesa las URLs en grupos de `batch_size` en paralelo.
    """
    results = []

    def worker(url):
        try:
            result = scrape_offer(url)
            results.append(result)
        except Exception as e:
            print(f"[✗] Falló: {url} → {e}")
            log_fallida(url)


    for i in range(0, len(urls), batch_size):
        threads = []
        for url in urls[i:i+batch_size]:
            t = threading.Thread(target=worker, args=(url,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        time.sleep(sleep_time)  # pausa entre lotes para evitar bloqueo

    return results


if __name__ == "__main__":

    inicio = datetime.now()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%d_%H%M%S")
    links_path = os.path.join(script_dir, "links")
    file_path = os.path.join(script_dir, "ofertas", f"ofertas{timestamp}.csv")
    leidos_path = os.path.join(script_dir, "ofertas", f"leidas.txt")
    print("Starting")
    for i, urls in enumerate(cargar_urls_por_bloques(links_path, 100)):
        print(f"Procesando bloque {i + 1} con {len(urls)} URLs", end="")

        resultados = scrape_batch([clean_language(url) for url in urls], batch_size=50, sleep_time=0.25)
        for data in resultados:
            append_to_csv(data, file_path)
        
        with open(leidos_path, "a") as f:
            f.writelines([url + "\n" for url in urls])
    
    fin = datetime.now()
    duracion = fin - inicio
    print("Finalizado!")
    print(f"Duración en segundos: {duracion.total_seconds()}")
