"""
Configurações, constantes e taxonomia temática do repositório CFM Normas.
"""
from pathlib import Path
import re

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent.parent
NORMAS_DIR = BASE_DIR / "normas"
TRILHAS_DIR = BASE_DIR / "trilhas_tematicas"
MANIFESTO_PATH = BASE_DIR / "manifesto.json"
CATALOGO_GLOBAL_PATH = BASE_DIR / "catalogo.json"
CATALOGO_IA_PATH = BASE_DIR / "catalogo_ia_privacidade.json"
PROGRESSO_PATH = BASE_DIR / "PROGRESSO.md"
ESTATISTICAS_PATH = BASE_DIR / "estatisticas.html"

# Endpoints do CFM
URL_BUSCA_PORTAL = "https://portal.cfm.org.br/buscar-normas-cfm-e-crm/"
URL_PDF_BASE = "https://sistemas.cfm.org.br/normas/arquivos/{sname}/BR/{ano}/{numero}_{ano}.pdf"
URL_VISUALIZAR_BASE = "https://sistemas.cfm.org.br/normas/visualizar/{sname}/BR/{ano}/{numero}"

# Mapeamento de Códigos para Tipos e Pastas
TIPOS_MAP = {
    "R": {"nome": "Resolucao", "pasta": "resolucoes", "sname": "resolucoes"},
    "P": {"nome": "Parecer", "pasta": "pareceres", "sname": "pareceres"},
    "E": {"nome": "Recomendacao", "pasta": "recomendacoes", "sname": "recomendacoes"},
    "D": {"nome": "Despacho", "pasta": "despachos", "sname": "despachos"},
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 (CFM-Normas-OpenSourceBot)"
)

# Macro-Temas e Termos-Chave para Classificação
TAXONOMIA_TEMATICA = {
    "Saúde Digital & Tecnologia": {
        "micro_tags": {
            "inteligencia-artificial": [
                r"\bintelig[êe]ncia artificial\b",
                r"\bmachine learning\b",
                r"\baprendizado de m[áa]quina\b",
                r"\balgoritmo[s]? cl[íi]nico[s]?\b",
                r"\bsuporte [àa] decis[ãa]o cl[íi]nica\b",
                r"\bsoftware m[ée]dico\b",
                r"\bsamd\b",
            ],
            "lgpd-e-privacidade": [
                r"\blgpd\b",
                r"\bprote[çc][ãa]o de dados\b",
                r"\bdado[s]? sens[íi]ve[li]s?\b",
                r"\banonimiza[çc][ãa]o\b",
                r"\bsigilo m[ée]dico\b",
                r"\bseguran[çc]a da informa[çc][ãa]o\b",
                r"\bcriptografia\b",
            ],
            "telemedicina": [
                r"\btelemedicina\b",
                r"\btelessa[úu]de\b",
                r"\bteleconsulta\b",
                r"\bteleinterconsulta\b",
                r"\btelediagn[óo]stico\b",
                r"\btelemonitoramento\b",
            ],
            "prontuario-eletronico": [
                r"\bprontu[áa]rio eletr[ôo]nico\b",
                r"\bpep\b",
                r"\bregistro eletr[ôo]nico em sa[úu]de\b",
                r"\bprescri[çc][ãa]o digital\b",
                r"\breceita digital\b",
                r"\bcertifica[çc][ãa]o digital\b",
                r"\bicp-brasil\b",
            ],
        }
    },
    "Ética Médica & Deontologia": {
        "micro_tags": {
            "publicidade-medica": [
                r"\bpublicidade m[ée]dica\b",
                r"\bpropaganda m[ée]dica\b",
                r"\ban[úu]ncio[s]?\b",
                r"\bredes sociais\b",
            ],
            "sigilo-profissional": [
                r"\bsegredo m[ée]dico\b",
                r"\bconfidencialidade\b",
                r"\bquebra de sigilo\b",
            ],
            "consentimento-tcle": [
                r"\btermo de consentimento\b",
                r"\btcle\b",
                r"\bconsentimento esclarecido\b",
                r"\bautonomia do paciente\b",
            ],
            "conflito-de-interesses": [
                r"\bconflito de interesse\b",
                r"\bind[úu]stria farmac[êe]utica\b",
                r"\bopme\b",
            ],
        }
    },
    "Prática Clínica & Procedimentos": {
        "micro_tags": {
            "cirurgia-robotica": [
                r"\bcirurgia rob[óo]tica\b",
                r"\brob[ôo] cir[úu]rgico\b",
            ],
            "reproducao-assistida": [
                r"\breprodu[çc][ãa]o assistida\b",
                r"\bfertiliza[çc][ãa]o\b",
                r"\bembi[ãa]o\b",
            ],
            "cuidados-paliativos": [
                r"\bcuidados paliativos\b",
                r"\bdiretivas antecipadas\b",
                r"\bterminalidade\b",
                r"\bortotan[áa]sia\b",
            ],
            "urgencia-e-emergencia": [
                r"\bpronto atendimento\b",
                r"\bupa\b",
                r"\bsamu\b",
                r"\b plant[ãa]o\b",
            ],
        }
    },
    "Gestão, Infraestrutura & Perícia": {
        "micro_tags": {
            "normas-uti-uci": [
                r"\buti\b",
                r"\buci\b",
                r"\bterapia intensiva\b",
                r"\bleito[s]? de uti\b",
            ],
            "responsabilidade-tecnica": [
                r"\bdiretor t[ée]cnico\b",
                r"\bdiretor cl[íi]nico\b",
                r"\brespons[áa]vel t[ée]cnico\b",
            ],
            "pericia-medica": [
                r"\bper[íi]cia m[ée]dica\b",
                r"\bperito m[ée]dico\b",
                r"\bassistente t[ée]cnico\b",
            ],
        }
    },
    "Formação & Registro Profissional": {
        "micro_tags": {
            "rqe-especialidades": [
                r"\brqe\b",
                r"\bt[íi]tulo de especialista\b",
                r"\bespecialidade m[ée]dica\b",
                r"\bresid[êe]ncia m[ée]dica\b",
            ],
            "revalidacao-diplomas": [
                r"\brevalida\b",
                r"\bdiploma estrangeiro\b",
            ],
        }
    },
}
