# CFM Normas (2020–2026)

> Acervo aberto, versionado e estruturado das normativas oficiais do **Conselho Federal de Medicina (CFM)** em Markdown, enriquecidas com metadados relacionais, taxonomia temática e otimização nativa para agentes de Inteligência Artificial e sistemas de apoio à decisão clínica.

[![Status](https://img.shields.io/badge/status-ativo-brightgreen.svg)]()
[![Normas](https://img.shields.io/badge/CFM-2020--2026-blue.svg)]()
[![Formato](https://img.shields.io/badge/formato-Markdown%20%2B%20YAML-orange.svg)]()
[![Licença](https://img.shields.io/badge/license-CC--BY--4.0-lightgrey.svg)](LICENSE)

---

## 1. Manifesto do Projeto

> *"Historicamente, a classe médica enfrenta uma grande dispersão de fontes de informação, o que muitas vezes dificulta o alinhamento e o compartilhamento ágil de conhecimento regulatório entre profissionais da saúde.  
> Pensando em compartilhar conhecimento e aproximar a comunidade médica, pesquisadores, desenvolvedores e juristas em torno de uma base acessível e confiável, este repositório disponibiliza as normativas mais recentes do CFM em formato aberto (Markdown).  
> A estrutura foi projetada nativamente para ser consumida tanto por profissionais de saúde quanto por agentes de Inteligência Artificial encarregados de conferir conformidade ética, regulatória e técnica no exercício da medicina."*

---

## 2. Visão Rápida do Acervo

* **Abrangência Temporal:** 2020 a 2026 (atualizado periodicamente).
* **Tipos de Normas Cobertos:**
  * **Resoluções (`R`):** Atos normativos de alcance nacional com poder coercitivo.
  * **Pareceres (`P`):** Respostas a consultas ético-profissionais de relevância clínica e jurídica.
  * **Recomendações (`E`):** Diretrizes orientativas do Plenário do CFM.
* **Curadoria Especial:** Trilha dedicada a **Inteligência Artificial, Software Médico (SaMD), Telemedicina e Proteção de Dados (LGPD)**.
* **Sem Erros de CORS:** O painel interativo [`estatisticas.html`](estatisticas.html) pode ser aberto diretamente no seu navegador (`file:///...`).

Consulte o status detalhado em **[`PROGRESSO.md`](PROGRESSO.md)** e os critérios de escopo em **[`COBERTURA.md`](COBERTURA.md)**.

---

## 3. Como Utilizar este Repositório com Agentes de IA

### Modo 1: Consulta Direta por Agentes (Sem Banco Vetorial / Zero Infraestrutura)
Um agente de IA (via Function Calling, LangChain, AutoGen ou CrewAI) pode consultar o acervo remotamente em dois passos:

1. **Localizar via Índice Invertido $O(1)$:** Faz uma requisição ao [`catalogo.json`](catalogo.json) (ou [`catalogo_ia_privacidade.json`](catalogo_ia_privacidade.json)) e consulta `indices_tags["telemedicina"]`.
2. **Leitura Direta:** Faz o download HTTP do arquivo bruto via GitHub Raw:

```python
import requests

def consultar_norma_cfm(norma_id: str) -> str:
    """Busca o texto completo de uma norma no repositório GitHub sem baixar o repositório."""
    catalogo_url = "https://raw.githubusercontent.com/md-augustolinhares/cfm-normas/main/catalogo.json"
    catalogo = requests.get(catalogo_url).json()
    
    item = next((doc for doc in catalogo["documentos"] if doc["id"] == norma_id), None)
    if not item:
        return "Norma não encontrada."
    
    return requests.get(item["url_raw"]).text
```

### Modo 2: Pipelines de RAG (Vector Stores)
Cada arquivo Markdown contém um cabeçalho YAML padronizado que é herdado automaticamente como metadados de busca semântica:

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    "./normas",
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
docs = loader.load()
# Cada chunk mantém metadados: id, status, macro_tema, tags e sha256_conteudo
```

---

## 4. Estrutura do Repositório

```
cfm-normas/
├── .github/workflows/
│   └── atualizar-normas.yml          # Atualização incremental semanal via GitHub Actions
├── src/                              # Código-fonte modular de extração e classificação
├── normas/
│   ├── resolucoes/                   # Resoluções organizadas por ano (2020-2026)
│   ├── pareceres/                    # Pareceres organizados por ano
│   └── recomendacoes/                # Recomendações organizadas por ano
├── trilhas_tematicas/                # Destaques curados de IA e Privacidade
├── catalogo.json                     # Índice global com índices invertidos O(1)
├── catalogo_ia_privacidade.json      # Índice filtrado em IA e Proteção de Dados
├── estatisticas.html                 # Dashboard interativo com gráficos (Chart.js)
├── PROGRESSO.md                      # Tabela comparativa de metas vs. coletado
├── COBERTURA.md                      # Metodologia e critérios de inclusão/exclusão
├── manifesto.json                    # Checkpoints e integridade de hashes SHA-256
└── schemas/norma.schema.json         # Contrato rígido de dados do frontmatter
```

---

## 5. Taxonomia Temática

Os documentos são classificados em **Macro-Temas** e **Micro-Tags**:
* **Saúde Digital & Tecnologia:** `inteligencia-artificial`, `lgpd-e-privacidade`, `telemedicina`, `prontuario-eletronico`, `prescricao-digital`.
* **Ética Médica & Deontologia:** `publicidade-medica`, `sigilo-profissional`, `consentimento-tcle`, `conflito-de-interesses`.
* **Prática Clínica & Procedimentos:** `cirurgia-robotica`, `reproducao-assistida`, `cuidados-paliativos`, `urgencia-e-emergencia`.
* **Gestão, Infraestrutura & Perícia:** `normas-uti-uci`, `responsabilidade-tecnica`, `pericia-medica`.
* **Formação & Registro Profissional:** `rqe-especialidades`, `revalidacao-diplomas`.

---

## 6. Agradecimentos e Inspiração

Este projeto foi concebido a partir da inspiradora iniciativa do repositório [`ctresb/leis`](https://github.com/ctresb/leis), adotando seus padrões abertos de catalogação e transparência em Markdown.
