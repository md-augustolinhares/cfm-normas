"""
Módulo de extração do portal do CFM: metadados JSON e stream de PDF em memória.
"""
import json
import re
import time
from typing import Dict, List, Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import URL_BUSCA_PORTAL, USER_AGENT

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _requisicao_html(url: str, params: dict) -> str:
    response = requests.get(url, params=params, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def extrair_json_busca(html: str) -> Dict[str, dict]:
    """Extrai a variável resultadoBuscaJson embutida no HTML do portal do CFM."""
    match = re.search(r"resultadoBuscaJson\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not match or match.group(1).strip() == "{}":
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def buscar_metadados_ano(ano: int, tipos: List[str] = ["R", "P", "E"]) -> List[dict]:
    """
    Varre todas as páginas de busca de normas do CFM para um determinado ano e tipos.
    Retorna uma lista consolidada de metadados de normas.
    """
    documentos: Dict[str, dict] = {}
    pagina = 1

    while True:
        params = [
            ("uf", "BR"),
            ("ano", str(ano)),
            ("numero", ""),
            ("assunto", ""),
            ("texto", ""),
            ("pagina", str(pagina)),
        ]
        for t in tipos:
            params.append(("tipo[]", t))

        time.sleep(0.4)  # Intervalo de cortesia para não sobrecarregar o portal
        html = _requisicao_html(URL_BUSCA_PORTAL, params)
        lote = extrair_json_busca(html)

        if not lote:
            break

        novos_nesta_pagina = 0
        for id_norma, dados in lote.items():
            if id_norma not in documentos:
                documentos[id_norma] = dados
                novos_nesta_pagina += 1

        if novos_nesta_pagina == 0:
            break

        # Verifica se há mais páginas
        total_registros = int(next(iter(lote.values())).get("COUNT", 0))
        if len(documentos) >= total_registros:
            break

        pagina += 1

    return list(documentos.values())


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=6))
def baixar_pdf_em_memoria(url_pdf: str) -> Optional[bytes]:
    """
    Baixa os bytes do PDF diretamente em memória RAM (sem salvar em disco).
    Retorna None se o arquivo não existir (404).
    """
    time.sleep(0.3)
    try:
        res = requests.get(url_pdf, headers=HEADERS, timeout=25)
        if res.status_code == 200 and "application/pdf" in res.headers.get("Content-Type", ""):
            return res.content
        return None
    except requests.RequestException:
        return None
