"""
Módulo de parseamento de PDF em memória para texto limpo e estruturado.
"""
import io
import re
from typing import Tuple
from pypdf import PdfReader


def extrair_texto_pdf(pdf_bytes: bytes) -> Tuple[str, int]:
    """
    Lê o PDF a partir de um buffer em memória e retorna o texto completo
    unificado e o número total de páginas.
    """
    stream = io.BytesIO(pdf_bytes)
    reader = PdfReader(stream)
    num_paginas = len(reader.pages)
    
    paginas_texto = []
    for idx, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        paginas_texto.append(raw_text)

    texto_completo = "\n\n".join(paginas_texto)
    return texto_completo, num_paginas


def formatar_artigos_markdown(texto: str) -> str:
    """
    Aplica formatação Markdown semântica em artigos, parágrafos e incisos.
    """
    linhas = texto.splitlines()
    linhas_formatadas = []

    for linha in linhas:
        l = linha.strip()
        if not l:
            linhas_formatadas.append("")
            continue

        # Formata Artigos como cabeçalhos Markdown ## Art. X
        if re.match(r"^Art(igo|\.)\s*\d+([º°o]|\.|\-)?", l, re.IGNORECASE):
            linhas_formatadas.append(f"\n## {l}")
        # Formata Parágrafos únicos ou numerados
        elif re.match(r"^(§\s*\d+|Parágrafo\s+[Uu]único)", l, re.IGNORECASE):
            linhas_formatadas.append(f"\n**{l}**")
        # Formata Capítulos e Seções
        elif re.match(r"^(CAP[ÍI]TULO|SE[ÇC][ÃA]O|T[ÍI]TULO)\s+[IVXLCDM\d]+", l, re.IGNORECASE):
            linhas_formatadas.append(f"\n# {l}\n")
        else:
            linhas_formatadas.append(l)

    resultado = "\n".join(linhas_formatadas)
    # Remove excesso de linhas vazias
    resultado = re.sub(r"\n{3,}", "\n\n", resultado)
    return resultado.strip()
