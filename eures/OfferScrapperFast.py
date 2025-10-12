import asyncio
import csv
import glob
import os
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# -------------------------------
# Utilidades
# -------------------------------

def parse_fecha_limite(dia, mes_texto, anio):
    meses = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    mes_num = meses.get(mes_texto.lower(), "01")
    return f"{dia}/{mes_num}/{anio}"

def log_fallida(url):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "ofertasFast", "fallidas.txt"), "a", encoding="utf-8") as f:
        f.write(url + "\n")

def append_to_csv(data, archivo_csv):
    campos = [
        "url","fecha_publicacion","fecha_limite","titulo","empresa","ocupacion",
        "educacion","descripcion","pais","region","duracion_jornada","tipo_contrato"
    ]
    archivo_nuevo = not os.path.exists(archivo_csv)
    with open(archivo_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        if archivo_nuevo:
            writer.writeheader()
        writer.writerow(data)

def clean_language(url):
    return url[:-2] + "es" if url.endswith("en") else url

def cargar_urls_por_bloques(directorio="links", bloque=1000, archivo= False):
    if archivo:
        archivos = glob.glob(directorio)
    else:
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
        yield buffer

# -------------------------------
# Scraper asíncrono
# -------------------------------

async def scrape_offer(context, url, sem):
    data = {"url": url}
    async with sem:  # limitar concurrencia
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)

            async def safe_text(selector, by="id"):
                try:
                    if by == "id":
                        return (await page.locator(f"#{selector}").first.inner_text()).strip()
                    elif by == "class":
                        return (await page.locator(f".{selector}").first.inner_text()).strip()
                except:
                    return None

            # Campos
            fecha = await safe_text("jv-lastModificationDate") or await safe_text("jv-lastModificationDate-no-title")
            data["fecha_publicacion"] = fecha
            data["titulo"] = await safe_text("jv-title")
            data["empresa"] = await safe_text("jv-details-employer-name")
            data["descripcion"] = await safe_text("jv-details-job-description")
            data["pais"] = await safe_text("jv-address-country", by="class")
            data["region"] = await safe_text("jv-address-region", by="class")
            data["duracion_jornada"] = await safe_text("jv-position-schedule-result-0")
            data["tipo_contrato"] = await safe_text("jv-position-type-code-result")
            data["ocupacion"] = await safe_text("jv-job-categories-codes-result-0")
            data["educacion"] = await safe_text("ecl-description-list__definition", by="class")

            try:
                dia = (await page.locator(".ecl-date-block__day").first.inner_text()).strip()
                mes = (await page.locator(".ecl-date-block__month").first.get_attribute("title")).strip()
                anio = (await page.locator(".ecl-date-block__year").first.inner_text()).strip()
                data["fecha_limite"] = parse_fecha_limite(dia, mes, anio)
            except:
                data["fecha_limite"] = None

        except PlaywrightTimeoutError:
            print(f"[✗] Timeout: {url}")
            log_fallida(url)
        except Exception as e:
            print(f"[✗] Falló: {url} → {e}")
            log_fallida(url)
        finally:
            await page.close()

    return data

# -------------------------------
# Main
# -------------------------------

async def main():
    inicio = datetime.now()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%d_%H%M%S")
    links_path = os.path.join(script_dir, "ofertasFast/pendientes.txt")
    file_path = os.path.join(script_dir, "ofertasFast", f"ofertas{timestamp}.csv")
    leidos_path = os.path.join(script_dir, "ofertasFast", "leidas.txt")

    sem = asyncio.Semaphore(20)  # controla nº de páginas simultáneas

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        await context.route("**/*", lambda route: route.abort()
                        if route.request.resource_type in ["image","stylesheet","font"]
                        else route.continue_())

        for i, urls in enumerate(cargar_urls_por_bloques(links_path, 100, True)):
            print(f"Procesando bloque {i+1} con {len(urls)} URLs")

            tasks = [scrape_offer(context, clean_language(url), sem) for url in urls]
            resultados = await asyncio.gather(*tasks)

            for data in resultados:
                if data:  # puede ser None si falló
                    append_to_csv(data, file_path)

            with open(leidos_path, "a") as f:
                f.writelines([url + "\n" for url in urls])

        await browser.close()

    fin = datetime.now()
    print("Finalizado!")
    print(f"Duración en segundos: {(fin - inicio).total_seconds()}")

if __name__ == "__main__":
    asyncio.run(main())
