from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time, sys

BASE_URL = "https://europa.eu/eures/portal/jv-se/search"
DEFAULT_PARAMS = {
    "page": "1",
    "resultsPerPage": "50",
    "orderBy": "BEST_MATCH",
    "locationCodes": "es",
    "lang": "en",
}

def build_search_url(params=None):
    params = params or DEFAULT_PARAMS
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{BASE_URL}?{query}"


def get_offer_links(max_pages=3, wait_ms=1500, headless=True, params=None, start_page=1):
    all_links = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()

            for page_num in range(start_page, max_pages + 1):
                try:
                    local_params = dict(params or DEFAULT_PARAMS)
                    local_params["page"] = str(page_num)
                    url = build_search_url(local_params)

                    page.goto(url, wait_until="networkidle", timeout=15000)
                    time.sleep(wait_ms / 1000.0)

                    anchors = page.locator("a[id^='jv-result-summary-title-']").all()
                    if not anchors:
                        print(f"\n[!] Página {page_num} sin resultados, deteniendo.")
                        break

                    for a in anchors:
                        href = a.get_attribute("href")
                        if href:
                            full_url = urljoin("https://europa.eu", href)
                            all_links.append(full_url)

                    # Progreso en vivo
                    progress = (page_num / max_pages) * 100
                    sys.stdout.write(
                        f"\rProgreso: {progress:.1f}% | URLs recogidas: {len(all_links)}"
                    )
                    sys.stdout.flush()

                except Exception as e:
                    print(f"\n[!] Error en página {page_num}: {e}")
                    break

            browser.close()

    except Exception as e:
        print(f"\n[!] Error general: {e}")

    # Deduplicar
    seen, deduped = set(), []
    for link in all_links:
        if link not in seen:
            seen.add(link)
            deduped.append(link)

    print("\n[✓] Scraping completado.")
    return deduped


if __name__ == "__main__":
    from datetime import datetime
    import os

    inicio = datetime.now()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = datetime.now().strftime("%d_%H%M%S")

    # Obtenemos los links
    urls = get_offer_links(100000, 500, start_page=202)

    print(len(urls))
    print(timestamp)
    print()

    fin = datetime.now()
    duracion = fin - inicio
    print(f"Duración en segundos: {duracion.total_seconds()}")

    file_path = os.path.join(script_dir, "links", f"links{timestamp}.txt")
    with open(file_path, "w") as f:
        f.writelines([url + "\n" for url in urls])
    print()
    print("URL guardadas en: "+ file_path)