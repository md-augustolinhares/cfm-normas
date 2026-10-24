"""
Módulo de classificação temática em dois níveis: Macro-temas e Micro-tags.
"""
import re
from typing import Dict, List, Tuple
from src.config import TAXONOMIA_TEMATICA


def classificar_norma(ementa: str, corpo_texto: str) -> Tuple[str, List[str], Dict[str, bool]]:
    """
    Avalia a ementa e o corpo da norma contra a taxonomia de termos.
    Retorna o macro-tema prioritário, a lista de micro-tags encontradas
    e o dicionário de destaques (IA, Dados, Telemedicina).
    """
    texto_combinado = f"{ementa}\n\n{corpo_texto}".lower()

    tags_encontradas: List[str] = []
    pontuacao_macro: Dict[str, int] = {macro: 0 for macro in TAXONOMIA_TEMATICA}

    for macro, dados in TAXONOMIA_TEMATICA.items():
        for micro_tag, padroes in dados["micro_tags"].items():
            for padrao in padroes:
                ocorrencias = len(re.findall(padrao, texto_combinado, re.IGNORECASE))
                if ocorrencias > 0:
                    if micro_tag not in tags_encontradas:
                        tags_encontradas.append(micro_tag)
                    pontuacao_macro[macro] += ocorrencias

    # Define o Macro-Tema com maior pontuação
    macro_vencedor = max(pontuacao_macro.items(), key=lambda item: item[1])
    if macro_vencedor[1] > 0:
        macro_tema = macro_vencedor[0]
    else:
        macro_tema = "Ética Médica & Deontologia"

    # Destaques específicos para filtros prioritários
    destaques = {
        "tem_ia": "inteligencia-artificial" in tags_encontradas,
        "tem_protecao_dados": "lgpd-e-privacidade" in tags_encontradas or "prontuario-eletronico" in tags_encontradas,
        "tem_telemedicina": "telemedicina" in tags_encontradas,
    }

    return macro_tema, sorted(tags_encontradas), destaques
