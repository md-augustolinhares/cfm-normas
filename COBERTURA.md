# Metodologia, Fontes e Cobertura do Acervo

> Este documento detalha a metodologia de extração, as fontes oficiais primárias, as regras de integridade e o plano de cobertura histórica progressiva do repositório **CFM Normas**.

---

## 1. Fontes Oficiais Primárias do Conselho Federal de Medicina

O acervo não utiliza intermediários ou bancos de dados de terceiros. Todos os registros são extraídos e conferidos a partir das fontes oficiais do CFM:

1. **Portal Médico do CFM — Busca Oficial de Normas:**  
   👉 [https://portal.cfm.org.br/buscar-normas-cfm-e-crm/](https://portal.cfm.org.br/buscar-normas-cfm-e-crm/)  
   *Canal público oficial para consulta de resoluções, pareceres, recomendações e despachos.*
2. **Sistema de Gerenciamento de Normas (SEDES / CFM Sistemas):**  
   👉 [https://sistemas.cfm.org.br/normas/](https://sistemas.cfm.org.br/normas/)  
   *Servidor oficial onde residem os acervos digitais em PDF e as tramitações administrativas.*
3. **Diário Oficial da União (Imprensa Nacional — Seção 1):**  
   *Veículo oficial em que as resoluções com força de lei são promulgadas para vigência nacional.*

---

## 2. Escopo e Metas Históricas (Roadmap rumo a 100%)

Inspirado na arquitetura do projeto `ctresb/leis`, o repositório avança em fases retrospectivas por décadas até cobrir **100% do acervo desde a fundação do CFM pela Lei nº 3.268/1957**:

| Fase | Período | Descrição do Bloco | Meta Estimada | Status |
| :---: | :---: | :--- | :---: | :---: |
| **Fase 1** | **2020–2026** | **Acervo Contemporâneo:** Resoluções, pareceres e recomendações modernas (incluindo o marco de IA Res. 2.454/2026 e Telemedicina Res. 2.314/2022). | **331 normas** | **100% Concluído ✅** |
| **Fase 2** | **2010–2019** | **A Década Digital:** Transição do papel para prontuários eletrônicos, consolidação das especialidades médicas (RQE) e Código de Ética de 2018. | **783 normas** | *Em planejamento* ⏳ |
| **Fase 3** | **2000–2009** | **Telemedicina 1.0 & Biotecnologia:** Primeira resolução histórica de telemedicina (Res. 1.643/2002), reprodução assistida inicial e transplantes. | **672 normas** | *Backlog* 📅 |
| **Fase 4** | **1990–1999** | **Estruturação do SUS:** Normatização pós-Constituição de 1988 e Lei 8.080/1990, e primeiros critérios de UTI e hemoterapia. | **612 normas** | *Backlog* 📅 |
| **Fase 5** | **1957–1989** | **Origens Fundacionais do CFM:** Atos desde a promulgação da Lei nº 3.268/1957, regimentos históricos e decisões deontológicas fundacionais (com OCR). | **~800 normas** | *Backlog* 🏛️ |
| **Meta Global** | **1957–Hoje** | **100% do Acervo Histórico da Medicina Brasileira mapeado em texto puro aberto.** | **~3.500 normas** | 🎯 **Alvo Final** |

---

## 3. Tipologia de Documentos Coberta

### Incluídos no Escopo Central:
1. **Resoluções (`R`):** Atos normativos emanados do Plenário do CFM que disciplinam privativamente o exercício profissional, com poder coercitivo sobre os médicos inscritos.
2. **Pareceres (`P`):** Relatórios conclusivos aprovados pelo Plenário em resposta a consultas formuladas por médicos ou instituições sobre dilemas ético-profissionais.
3. **Recomendações (`E`):** Orientações e boas práticas recomendadas pelo Plenário aos médicos e serviços de saúde, sem poder punitivo direto.

### Excluídos do Escopo Central (Justificativa):
1. **Portarias de Gestão Interna de Pessoal:** Atos administrativos de férias, exoneração, nomeação de assessores internos ou concessão de diárias no âmbito da administração do CFM.
2. **Normas Regionais de CRMs Locais (Fase Atual):** Os 27 CRMs publicam pareceres de jurisdição local. Para manter o acervo estável, confiável e de alcance unificado nacional, o repositório foca 100% no Conselho Federal.

---

## 4. Metodologia de Coleta e Integridade

* **Processamento Zero-Disco:** Os arquivos PDF oficiais são requisitados em memória RAM (`io.BytesIO`), parseados e higienizados para Markdown, descartando os binários brutos.
* **Controle de Idempotência:** Cada documento é registrado no arquivo `manifesto.json` com seu `id_norma_cfm` e o `sha256` do conteúdo.
* **Contrato de Dados:** A estrutura dos arquivos é estritamente validada pelo esquema `schemas/norma.schema.json`.
