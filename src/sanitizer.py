"""
Módulo de higienização de texto e sanitização contra injeções.
"""
import html
import re


def sanitizar_texto_norma(texto: str) -> str:
    """
    Remove tags potencialmente perigosas, cabeçalhos repetidos de carimbo e
    normaliza caracteres estranhos de OCR/PDF.
    """
    if not texto:
        return ""

    # Desescapa entidades HTML se existirem
    texto = html.unescape(texto)

    # Remove tags perigosas (scripts, iframes, styles)
    texto = re.sub(r"<\s*(script|iframe|style|object|embed)[^>]*>.*?<\s*/\s*\1\s*>", "", texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r"<\s*(script|iframe|style|object|embed)[^>]*>", "", texto, flags=re.IGNORECASE)

    # Remove carimbos repetidos de rodapé/cabeçalho de página típicos do CFM
    padroes_rodape = [
        r"SGAS\s+915\s+Lote\s+72\s+CEP.*Bras[íi]lia.*DF",
        r"Telefone:\s*\(\d+\)\s*\d+-\d+",
        r"www\.portalmedico\.org\.br",
        r"P[áa]gina\s+\d+\s+de\s+\d+",
        r"^\s*\d+\s*$",  # número de página isolado
    ]
    for padrao in padroes_rodape:
        texto = re.sub(padrao, "", texto, flags=re.MULTILINE | re.IGNORECASE)

    # Normaliza quebras de hífens no final de linha (ex: telemedi-\ncina -> telemedicina)
    texto = re.sub(r"(\w+)-\n(\w+)", r"\1\2", texto)

    # Normaliza espaços múltiplos
    texto = re.sub(r"[ \t]+", " ", texto)

    return texto.strip()
