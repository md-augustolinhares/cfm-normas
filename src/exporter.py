"""
Módulo de gravação dos arquivos Markdown com YAML Frontmatter e gestão do manifesto.
"""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict
import yaml

from src.config import MANIFESTO_PATH, NORMAS_DIR, TIPOS_MAP, URL_PDF_BASE, URL_VISUALIZAR_BASE


def carregar_manifesto() -> Dict[str, str]:
    if MANIFESTO_PATH.exists():
        try:
            with open(MANIFESTO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_manifesto(manifesto: Dict[str, str]):
    with open(MANIFESTO_PATH, "w", encoding="utf-8") as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)


def construir_id_canonico(tipo_cod: str, numero: str, ano: str) -> str:
    tipo_prefix = {
        "R": "RES",
        "P": "PAR",
        "E": "REC",
        "D": "DESP",
    }.get(tipo_cod, "NORM")
    return f"CFM-{tipo_prefix}-{numero}-{ano}"


def exportar_norma_markdown(
    metadados_cfm: Dict[str, Any],
    texto_corpo: str,
    macro_tema: str,
    tags: list,
    destaques: dict,
) -> Dict[str, Any]:
    tipo_cod = metadados_cfm.get("IN_TIPO", "R")
    tipo_info = TIPOS_MAP.get(tipo_cod, TIPOS_MAP["R"])
    tipo_nome = tipo_info["nome"]
    pasta_tipo = tipo_info["pasta"]
    sname = tipo_info["sname"]

    numero = str(metadados_cfm.get("NUMERO", "0")).strip()
    ano = str(metadados_cfm.get("ANO", "0")).strip()
    id_canonico = construir_id_canonico(tipo_cod, numero, ano)

    # Trata revogação de forma canônica
    is_revogada = str(metadados_cfm.get("IS_REVOGADA", "")).strip().lower()
    if "revogada" in is_revogada:
        status = "Revogada"
    elif "suspensa" in is_revogada:
        status = "Suspensa"
    else:
        status = "Vigente"

    revoga_ids = []
    num_rev = metadados_cfm.get("NUMERO_REVOGADA")
    ano_rev = metadados_cfm.get("ANO_REVOGADA")
    if num_rev and ano_rev:
        revoga_ids.append(construir_id_canonico(tipo_cod, str(num_rev), str(ano_rev)))

    url_pdf = URL_PDF_BASE.format(sname=sname, ano=ano, numero=numero)
    url_visualizar = URL_VISUALIZAR_BASE.format(sname=sname, ano=ano, numero=numero)

    # Checksum de conteúdo do corpo
    sha256_hash = hashlib.sha256(texto_corpo.encode("utf-8")).hexdigest()

    frontmatter_dict = {
        "id": id_canonico,
        "id_norma_cfm": str(metadados_cfm.get("ID_NORMA", "")),
        "orgao": "CFM",
        "tipo": tipo_nome,
        "numero": numero,
        "ano": ano,
        "data_publicacao": str(metadados_cfm.get("DATA", "")),
        "status": status,
        "revoga_ids": revoga_ids,
        "alterada_por_ids": [],
        "ementa": str(metadados_cfm.get("RESUMO", "")).strip(),
        "macro_tema": macro_tema,
        "tags": tags,
        "destaques": destaques,
        "url_original": url_visualizar,
        "url_pdf_original": url_pdf,
        "sha256_conteudo": sha256_hash,
    }

    # Gera conteúdo completo do Markdown
    yaml_header = yaml.dump(frontmatter_dict, sort_keys=False, allow_unicode=True)
    titulo_doc = f"# {tipo_nome.upper()} CFM Nº {numero}/{ano}\n\n"
    conteudo_final = f"---\n{yaml_header}---\n\n{titulo_doc}{texto_corpo}\n"

    # Salva na pasta do ano
    pasta_destino = NORMAS_DIR / pasta_tipo / ano
    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivo_destino = pasta_destino / f"{id_canonico}.md"

    with open(arquivo_destino, "w", encoding="utf-8") as f:
        f.write(conteudo_final)

    # Retorna o registro para o catálogo
    rel_path = f"normas/{pasta_tipo}/{ano}/{id_canonico}.md"
    frontmatter_dict["caminho_relativo"] = rel_path
    frontmatter_dict["url_raw"] = f"https://raw.githubusercontent.com/md-augustolinhares/cfm-normas/main/{rel_path}"

    return frontmatter_dict
