#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scraper del portal SEPE - Empléate (modo legal y reproducible)
- Modo 1 (preferente): usa el endpoint JSON público de búsqueda.
- Modo 2 (fallback): parsea HTML de resultados y fichas si el JSON cambia.

Campos extraídos:
id, timestamp, text, province, sector, occupation, contract_type, salary, education, source, url

Uso:
  python scrape_empleate.py --start 2025-06-01 --end 2025-08-31 --out empleate.parquet --limit 0

Notas:
- Respeta la web: rate limit, user-agent, y reconoce licencia y fuente al publicar.
- Este script está preparado para cambios menores; si el endpoint cambia, activa --html-fallback.
"""
import certifi, requests
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings
import hashlib
import json
import logging
import math
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from tqdm import tqdm
import argparse

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import SSLError, ConnectionError, ReadTimeout



# ---------------------------
# Configuración general
# ---------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.1",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.empleate.gob.es/empleo/#/ofertas",
    "Origin": "https://www.empleate.gob.es",
    "X-Requested-With": "XMLHttpRequest",
}


BASE = "https://www.empleate.gob.es"
SEARCH_JSON = f"{BASE}/empleoPortalEmpleate/OfertaEmpleo/consultaOfertas.do"  # endpoint JSON (históricamente usado)
SEARCH_HTML = f"{BASE}/empleo/#/ofertas"  # ruta SPA; usamos endpoints que llama
DETAIL_PREFIX = f"{BASE}/empleoPortalEmpleate/OfertaEmpleo/verOferta.do?id="  # detalle tradicional
SOURCE = "empleate.gob.es"

PAGE_SIZE = 50          # tamaño de página para JSON
REQUESTS_SLEEP = 0.7    # segundos entre peticiones (respeto)
TIMEOUT = 20


# ---------------------------
# Estructura de datos
# ---------------------------
@dataclass
class Offer:
    id: str
    timestamp: str
    text: str
    province: Optional[str]
    sector: Optional[str]
    occupation: Optional[str]
    contract_type: Optional[str]
    salary: Optional[str]
    education: Optional[str]
    source: str
    url: str


# ---------------------------
# Utilidades
# ---------------------------
def sha1_16(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]


def to_iso8601(dt) -> str:
    if isinstance(dt, str):
        try:
            d = dateparser.parse(dt)
        except Exception:
            return None
    else:
        d = dt
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).isoformat()


def clean_html(s: str) -> str:
    if not s:
        return ""
    return BeautifulSoup(s, "html.parser").get_text(" ", strip=True)


def clamp_date(date_str: str) -> str:
    # fuerza a YYYY-MM-DD
    return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import SSLError, ConnectionError, ReadTimeout

def make_session(verify: bool = True) -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=5, connect=5, read=5,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.verify = verify
    return s



# ---------------------------
# MODO 1: JSON (preferente)
# ---------------------------
def build_search_payload(page: int, start: str, end: str) -> Dict:
    """
    El portal históricamente acepta POST con filtros en consultaOfertas.do.
    Este payload es genérico: rango de fechas + paginación.
    Si tu instancia requiere otros nombres de campo, ajusta aquí.
    """
    payload = {
        "fechaPublicacionDesde": start,
        "fechaPublicacionHasta": end,
        "tamanoPagina": PAGE_SIZE,
        "numeroPagina": page,
        # Puedes añadir filtros si quieres: provincia, sector, etc.
        # "provincia": "",
        # "sector": "",
        # "texto": "",
        # "modalidad": "",
    }
    return payload


def search_json(session: requests.Session, start: str, end: str, limit: int = 0) -> Iterable[Dict]:
    """
    Itera resultados del endpoint JSON. Devuelve items crudos.
    limit=0 => sin límite (todos); si >0, corta tras ese número.
    """
    page = 1
    total_seen = 0

    while True:
        payload = build_search_payload(page, start, end)
        try:
            r = session.post(SEARCH_JSON, headers=HEADERS, data=payload, timeout=TIMEOUT, verify=session.verify)
        except SSLError as e:
            logging.error("Fallo TLS/SSL con el endpoint JSON. Prueba --insecure, --html-fallback o actualiza certifi.")
            raise
        except (ConnectionError, ReadTimeout) as e:
            logging.warning(f"Conexión/timeout en page {page}: {e}; reintento via Retry del adapter.")
            continue


        # Estructuras comunes: data["resultados"] y data["totalResultados"] (ajusta si varía)
        items = data.get("resultados") or data.get("ofertas") or []
        if not items:
            if page == 1:
                logging.warning("Sin items en JSON. ¿Endpoint cambiado? Prueba --html-fallback.")
            break

        for it in items:
            yield it
            total_seen += 1
            if limit > 0 and total_seen >= limit:
                return

        # Paginación
        total = data.get("totalResultados") or data.get("total") or None
        if total is None:
            # seguimos hasta que no haya items
            if len(items) < PAGE_SIZE:
                break
            page += 1
        else:
            last_page = math.ceil(total / PAGE_SIZE)
            if page >= last_page:
                break
            page += 1

        time.sleep(REQUESTS_SLEEP)


def map_json_item_to_offer(session: requests.Session, it: Dict) -> Offer:
    """
    Mapea un item JSON a la estructura Offer.
    Si falta algo, intenta completar con una visita a la ficha de detalle (opcional).
    """
    # Los nombres de campos pueden variar ligeramente; cubrimos varios alias.
    offer_id = str(it.get("id") or it.get("idOferta") or it.get("identificador") or sha1_16(json.dumps(it, ensure_ascii=False)))
    title = it.get("titulo") or it.get("tituloOferta") or it.get("puesto") or ""
    desc = it.get("descripcion") or it.get("descripcionPuesto") or it.get("detalle") or ""
    text = clean_html(f"{title}. {desc}").strip()

    # Fecha de publicación
    ts = it.get("fechaPublicacion") or it.get("fechaAlta") or it.get("fecha") or it.get("datePosted") or ""
    timestamp = to_iso8601(ts) or to_iso8601(datetime.utcnow())

    province = (it.get("provincia") or it.get("ubicacion") or it.get("localidad") or "") or None
    sector = it.get("sector") or it.get("familiaProfesional") or None
    occupation = it.get("ocupacion") or it.get("categoriaProfesional") or it.get("puesto") or None
    contract_type = it.get("tipoContrato") or it.get("contrato") or None
    salary = it.get("salario") or it.get("retribucion") or None
    education = it.get("nivelEstudios") or it.get("estudiosMinimos") or None

    # URL de detalle si viene
    url = it.get("url") or it.get("enlace") or f"{DETAIL_PREFIX}{offer_id}"

    # Si el texto es muy corto o faltan campos clave, intenta enriquecer con el detalle HTML
    if (not desc or len(text) < 25) or (not contract_type or not education):
        try:
            extra = fetch_detail_html(session, url)
            if extra:
                text = extra.get("text") or text
                province = extra.get("province") or province
                sector = extra.get("sector") or sector
                occupation = extra.get("occupation") or occupation
                contract_type = extra.get("contract_type") or contract_type
                salary = extra.get("salary") or salary
                education = extra.get("education") or education
        except Exception:
            pass

    return Offer(
        id=offer_id,
        timestamp=timestamp,
        text=text,
        province=province,
        sector=sector,
        occupation=occupation,
        contract_type=contract_type,
        salary=salary,
        education=education,
        source=SOURCE,
        url=url
    )


# ---------------------------
# MODO 2: HTML (fallback)
# ---------------------------
def fetch_detail_html(session: requests.Session, url: str) -> Optional[Dict]:
    """
    Descarga la ficha de oferta y rasca campos desde el HTML.
    Se intenta ser tolerante a cambios (busca por etiquetas comunes).
    """
    if not url.startswith("http"):
        url = f"{DETAIL_PREFIX}{url}"

    r = session.get(url, headers=HEADERS, timeout=TIMEOUT, verify=session.verify)

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # Texto principal (descripción)
    parts = []
    for sel in [
        ".descripcion", ".cuerpo", ".detalle", ".texto", ".oferta-descripcion",
        "div#descripcion", "section.descripcion", "article"
    ]:
        block = soup.select_one(sel)
        if block:
            parts.append(clean_html(block.get_text(" ")))
    # Si no se encuentra, coge párrafos
    if not parts:
        ps = [clean_html(p.get_text(" ")) for p in soup.select("p")]
        parts.append(" ".join([p for p in ps if p]))

    text = ". ".join([p for p in parts if p]).strip()
    if not text:
        # fallback muy laxo
        text = clean_html(soup.get_text(" "))

    # Campos comunes en tablas/dl
    def find_field(labels: List[str]) -> Optional[str]:
        txt = soup.get_text(" ").lower()
        for lab in labels:
            # busca label: valor
            m = re.search(rf"{lab}\s*[:\-]\s*([^\n\r]+)", txt, re.IGNORECASE)
            if m:
                val = m.group(1).strip()
                # corta hasta separador razonable
                val = re.split(r"\s{2,}|\|", val)[0].strip()
                return val
        return None

    province = find_field(["provincia", "lugar de trabajo", "localidad"]) or None
    sector = find_field(["sector", "familia profesional", "área profesional"]) or None
    occupation = find_field(["ocupación", "categoría profesional", "puesto"]) or None
    contract_type = find_field(["tipo de contrato", "contrato"]) or None
    salary = find_field(["salario", "retribución"]) or None
    education = find_field(["nivel de estudios", "estudios mínimos", "formación"]) or None

    return {
        "text": text,
        "province": province,
        "sector": sector,
        "occupation": occupation,
        "contract_type": contract_type,
        "salary": salary,
        "education": education,
    }


def search_html_fallback(session: requests.Session, start: str, end: str, limit: int = 0) -> Iterable[Offer]:
    """
    Fallback: si no hay JSON utilizable, podrías usar listados HTML (si el portal los expone sin JS duro)
    o una lista preconstruida de URLs de ofertas (por sitemap/archivo).
    Aquí damos un esqueleto básico (deberás adaptar selectores de la lista de resultados).
    """
    logging.warning("Usando fallback HTML: puede ser más lento y frágil.")
    # Este bloque es un ejemplo genérico; ajusta a la estructura real de listados si es necesario.
    # Idea: si existe un buscador con parámetros GET (fechaDesde/fechaHasta & page), itera páginas.
    page = 1
    seen = 0
    while True:
        # URL de ejemplo (ajusta si el portal ofrece una lista tradicional)
        url = f"{BASE}/empleoPortalEmpleate/OfertaEmpleo/busquedaAvanzada.do?desde={start}&hasta={end}&page={page}"
        r = session.get(url, headers=HEADERS, timeout=TIMEOUT, verify=session.verify)

        if r.status_code != 200:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("a.oferta, .oferta a, a[href*='verOferta.do?id=']")
        if not cards:
            if page == 1:
                logging.warning("No se encontraron listados en HTML (estructura distinta).")
            break

        for a in cards:
            href = a.get("href") or ""
            if href.startswith("/"):
                href = BASE + href
            m = re.search(r"id=(\d+)", href)
            off_id = m.group(1) if m else sha1_16(href)
            detail_data = fetch_detail_html(session, href) or {}

            # timestamp no siempre está en la ficha -> usa fecha del listado si aparece
            # (opcional: intentar leer una fecha dentro de la ficha)
            timestamp = to_iso8601(datetime.utcnow())

            offer = Offer(
                id=off_id,
                timestamp=timestamp,
                text=detail_data.get("text", ""),
                province=detail_data.get("province"),
                sector=detail_data.get("sector"),
                occupation=detail_data.get("occupation"),
                contract_type=detail_data.get("contract_type"),
                salary=detail_data.get("salary"),
                education=detail_data.get("education"),
                source=SOURCE,
                url=href,
            )
            yield offer
            seen += 1
            if limit > 0 and seen >= limit:
                return

            time.sleep(REQUESTS_SLEEP)

        # criterio de fin: si no hay paginación clara, rompe cuando no salen más enlaces
        page += 1


# ---------------------------
# Orquestación
# ---------------------------

def run(start: str, end: str, out_path: str, limit: int = 0, html_fallback: bool = False, insecure: bool = False):
    start = clamp_date(start); end = clamp_date(end)
    logging.info(f"Rango: {start} .. {end}")
    logging.info(f"DEBUG: bandera --insecure = {insecure}")
    session = make_session(verify=not insecure)
    if insecure:
        disable_warnings(InsecureRequestWarning)
        logging.warning("TLS VERIFY DESACTIVADO (modo diagnóstico)")

    session.verify = certifi.where()


    rows: List[Dict] = []

    if not html_fallback:
        # Modo JSON → recoge items y mapea
        raw_iter = search_json(session, start, end, limit=limit)
        for it in tqdm(raw_iter, desc="Descargando (JSON)"):
            try:
                offer = map_json_item_to_offer(session, it)
                rows.append(asdict(offer))
            except Exception as ex:
                logging.exception(f"Error mapeando item JSON: {ex}")
            time.sleep(REQUESTS_SLEEP)
    else:
        # Fallback HTML
        for offer in tqdm(search_html_fallback(session, start, end, limit=limit), desc="Descargando (HTML)"):
            rows.append(asdict(offer))

    if not rows:
        logging.warning("No se obtuvieron resultados. Revisa el rango o prueba --html-fallback.")
        return

    # DataFrame + limpieza básica y deduplicado por URL+timestamp o por id
    df = pd.DataFrame(rows)
    # normaliza texto
    df["text"] = (df["text"] or "").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    # dedup por (url) principalmente
    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"]).copy()
    df = df.drop_duplicates(subset=["id"]).copy()

    # Orden y tipos
    cols = [
        "id", "timestamp", "text", "province", "sector", "occupation",
        "contract_type", "salary", "education", "source", "url"
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    df = df[cols].copy()

    # Guardado
    if out_path.lower().endswith(".parquet"):
        df.to_parquet(out_path, index=False)
    else:
        df.to_csv(out_path, index=False, encoding="utf-8")

    logging.info(f"Guardado {len(df):,} filas en {out_path}")


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="Fecha inicio (YYYY-MM-DD)")
    ap.add_argument("--end", required=True, help="Fecha fin (YYYY-MM-DD)")
    ap.add_argument("--out", default="empleate.parquet", help="Ruta de salida (.parquet o .csv)")
    ap.add_argument("--limit", type=int, default=0, help="Límite de ofertas (0 = todas)")
    ap.add_argument("--html-fallback", action="store_true", help="Usar parseo HTML (si falla JSON)")
    ap.add_argument("--log", default="INFO", help="Nivel de log: DEBUG/INFO/WARNING/ERROR")
    ap.add_argument("--insecure", action="store_true", help="No verificar certificados TLS (solo diagnóstico)")

    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper(), logging.INFO),
                        format="%(levelname)s %(message)s")
    run(args.start, args.end, args.out, limit=args.limit, html_fallback=args.html_fallback, insecure=args.insecure)

