# Metodologia e Cobertura do Acervo

> Este documento detalha os critérios de inclusão, exclusão, fontes e metodologia adotados no repositório **CFM Normas**.

---

## 1. Escopo Temporal e Geográfico

* **Período Coberto:** 01 de janeiro de 2020 a 31 de dezembro de 2026.
* **Esfera:** Federal (`uf = BR` / Conselho Federal de Medicina).
* **Alcance:** Nacional (atos que vinculam a prática médica em todo o território brasileiro).

---

## 2. Tipologia de Documentos Coberta

### Incluídos no Escopo Central:
1. **Resoluções (`R`):** Atos normativos emanados do Plenário do CFM que disciplinam privativamente o exercício profissional, com poder coercitivo sobre os médicos inscritos.
2. **Pareceres (`P`):** Relatórios conclusivos aprovados pelo Plenário em resposta a consultas formuladas por médicos ou instituições sobre dilemas ético-profissionais.
3. **Recomendações (`E`):** Orientações e boas práticas recomendadas pelo Plenário aos médicos e serviços de saúde, sem poder punitivo direto.

### Excluídos do Escopo Central (Justificativa):
1. **Portarias de Gestão Interna de Pessoal:** Atos administrativos de férias, exoneração, nomeação de assessores internos ou concessão de diárias no âmbito da administração do CFM.
2. **Normas Regionais de CRMs Locais (Fase Atual):** Os 27 CRMs publicam pareceres de jurisdição local. Para manter o acervo estável, confiável e de alcance unificado nacional, o repositório foca 100% no Conselho Federal.

---

## 3. Metodologia de Coleta e Integridade

* **Fonte Oficial Primária:** [Portal Médico — Buscar Normas CFM e CRMs](https://portal.cfm.org.br/buscar-normas-cfm-e-crm/) e Diário Oficial da União (Seção 1).
* **Processamento Zero-Disco:** Os arquivos PDF oficiais são requisitados em memória RAM (`io.BytesIO`), parseados e higienizados para Markdown, descartando os binários brutos.
* **Controle de Idempotência:** Cada documento é registrado no arquivo `manifesto.json` com seu `id_norma_cfm` e o `sha256` do conteúdo.
* **Contrato de Dados:** A estrutura dos arquivos é estritamente validada pelo esquema `schemas/norma.schema.json`.
