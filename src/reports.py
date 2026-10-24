"""
Módulo de geração de relatórios, catálogos, PROGRESSO.md e dashboard estatisticas.html.
"""
from datetime import datetime
import json
from typing import Any, Dict, List

from src.config import (
    CATALOGO_GLOBAL_PATH,
    CATALOGO_IA_PATH,
    ESTATISTICAS_PATH,
    PROGRESSO_PATH,
)


def gerar_catalogos(documentos: List[Dict[str, Any]]):
    # Constrói índice invertido de tags e macro-temas para busca O(1)
    indices_tags: Dict[str, List[str]] = {}
    indices_macro: Dict[str, List[str]] = {}

    for doc in documentos:
        doc_id = doc["id"]
        macro = doc.get("macro_tema", "Outros")
        indices_macro.setdefault(macro, []).append(doc_id)

        for tag in doc.get("tags", []):
            indices_tags.setdefault(tag, []).append(doc_id)

    catalogo_global = {
        "atualizado_em": datetime.now().isoformat(),
        "total_documentos": len(documentos),
        "indices_tags": indices_tags,
        "indices_macro_temas": indices_macro,
        "documentos": documentos,
    }

    with open(CATALOGO_GLOBAL_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogo_global, f, indent=2, ensure_ascii=False)

    # Catálogo filtrado apenas para IA, Telemedicina e Privacidade
    docs_ia = [
        d for d in documentos
        if d.get("destaques", {}).get("tem_ia")
        or d.get("destaques", {}).get("tem_protecao_dados")
        or d.get("destaques", {}).get("tem_telemedicina")
    ]

    catalogo_ia = {
        "atualizado_em": datetime.now().isoformat(),
        "total_documentos_ia_dados": len(docs_ia),
        "documentos": docs_ia,
    }

    with open(CATALOGO_IA_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogo_ia, f, indent=2, ensure_ascii=False)


def gerar_progresso_md(documentos: List[Dict[str, Any]]):
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Contagem por tipo
    resolucoes = [d for d in documentos if d["tipo"] == "Resolucao"]
    pareceres = [d for d in documentos if d["tipo"] == "Parecer"]
    recomendacoes = [d for d in documentos if d["tipo"] == "Recomendacao"]
    despachos = [d for d in documentos if d["tipo"] == "Despacho"]

    # Contagem por ano
    anos_map: Dict[str, Dict[str, int]] = {}
    for d in documentos:
        ano = d.get("ano", "Desconhecido")
        anos_map.setdefault(ano, {"total": 0, "vigente": 0, "revogada": 0, "ia_dados": 0})
        anos_map[ano]["total"] += 1
        if d.get("status") == "Vigente":
            anos_map[ano]["vigente"] += 1
        else:
            anos_map[ano]["revogada"] += 1
        if any(d.get("destaques", {}).values()):
            anos_map[ano]["ia_dados"] += 1

    linhas_anos = []
    for ano in sorted(anos_map.keys(), reverse=True):
        info = anos_map[ano]
        linhas_anos.append(
            f"| {ano} | {info['total']} | {info['vigente']} | {info['revogada']} | {info['ia_dados']} |"
        )

    conteudo = f"""# Progresso do Acervo de Normas do CFM (2020–2026)

> **Última atualização:** {data_atual} (gerado automaticamente)  
> **Total de documentos processados:** {len(documentos)}

---

## 1. Volume por Categoria de Norma

| Categoria | Meta Estimada (Oficial) | Coletados no Acervo | % Concluído | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Resoluções** | 196 | {len(resolucoes)} | {min(100.0, (len(resolucoes)/196)*100):.1f}% | 🟢 Em dia |
| **Pareceres** | 134 | {len(pareceres)} | {min(100.0, (len(pareceres)/134)*100):.1f}% | 🟢 Em dia |
| **Recomendações** | 1 | {len(recomendacoes)} | {min(100.0, (len(recomendacoes)/1)*100):.1f}% | 🟢 Em dia |
| **Despachos Jurídicos** | 801 | {len(despachos)} | {min(100.0, (len(despachos)/801)*100):.1f}% | 🔹 Módulo 1B |
| **Total Global** | **1.132** | **{len(documentos)}** | **{(len(documentos)/1132)*100:.1f}%** | 🟢 |

---

## 2. Distribuição Anual e Destaques Temáticos

| Ano | Total Coletado | Vigentes | Revogadas / Suspensas | Destaque IA / LGPD / Telemedicina |
| :---: | :---: | :---: | :---: | :---: |
{chr(10).join(linhas_anos)}

---

## 3. Fontes e Metodologia
- **Portal Oficial:** [Portal Médico CFM — Buscar Normas](https://portal.cfm.org.br/buscar-normas-cfm-e-crm/)
- **Repositório de Arquivos:** CFM Sistemas / SEDES
- **Processamento:** Extração de metadados em JSON nativo + conversão de stream de PDF para Markdown estruturado.
"""
    with open(PROGRESSO_PATH, "w", encoding="utf-8") as f:
        f.write(conteudo)


def gerar_estatisticas_html(documentos: List[Dict[str, Any]]):
    # Agregações para gráficos
    por_ano: Dict[str, int] = {}
    por_tipo: Dict[str, int] = {}
    por_macro: Dict[str, int] = {}
    por_status: Dict[str, int] = {"Vigente": 0, "Revogada": 0, "Suspensa": 0}

    for d in documentos:
        ano = str(d.get("ano", "Outros"))
        tipo = str(d.get("tipo", "Outros"))
        macro = str(d.get("macro_tema", "Outros"))
        status = str(d.get("status", "Vigente"))

        por_ano[ano] = por_ano.get(ano, 0) + 1
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        por_macro[macro] = por_macro.get(macro, 0) + 1
        por_status[status] = por_status.get(status, 0) + 1

    dados_estatisticas = {
        "atualizado_em": datetime.now().strftime("%d/%m/%Y"),
        "total": len(documentos),
        "por_ano": dict(sorted(por_ano.items())),
        "por_tipo": por_tipo,
        "por_macro": por_macro,
        "por_status": por_status,
    }

    dados_json_inlined = json.dumps(dados_estatisticas, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Dashboard de Estatísticas — Normas do CFM (2020–2026)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      margin: 0;
      padding: 24px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
    }}
    header {{
      margin-bottom: 24px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 16px;
    }}
    h1 {{
      font-size: 24px;
      margin: 0 0 8px 0;
      color: #0369a1;
    }}
    .sub {{
      color: #64748b;
      font-size: 14px;
    }}
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: white;
      padding: 16px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border: 1px solid #e2e8f0;
    }}
    .kpi-val {{
      font-size: 28px;
      font-weight: 700;
      color: #0284c7;
    }}
    .kpi-label {{
      font-size: 12px;
      text-transform: uppercase;
      color: #64748b;
      font-weight: 600;
    }}
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
      gap: 20px;
    }}
    .chart-box {{
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      border: 1px solid #e2e8f0;
    }}
    .chart-title {{
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
      color: #334155;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Acervo Regulatório do CFM — Estatísticas Oficiais (2020–2026)</h1>
      <div class="sub">Inspirado na arquitetura aberta de dados em saúde • Atualizado em: <span id="data-atualizacao"></span></div>
    </header>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total de Normas</div>
        <div class="kpi-val" id="kpi-total">0</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Normas Vigentes</div>
        <div class="kpi-val" id="kpi-vigentes" style="color: #16a34a;">0</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Revogadas / Alteradas</div>
        <div class="kpi-val" id="kpi-revogadas" style="color: #dc2626;">0</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Macro-Temas Mapeados</div>
        <div class="kpi-val" id="kpi-temas" style="color: #9333ea;">5</div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-box">
        <div class="chart-title">Publicações por Ano</div>
        <canvas id="chartAno"></canvas>
      </div>
      <div class="chart-box">
        <div class="chart-title">Distribuição por Categoria</div>
        <canvas id="chartTipo"></canvas>
      </div>
      <div class="chart-box">
        <div class="chart-title">Macro-Temas Regulatórios</div>
        <canvas id="chartMacro"></canvas>
      </div>
      <div class="chart-box">
        <div class="chart-title">Status de Vigência</div>
        <canvas id="chartStatus"></canvas>
      </div>
    </div>
  </div>

  <script id="metricas-data" type="application/json">
{dados_json_inlined}
  </script>

  <script>
    const data = JSON.parse(document.getElementById('metricas-data').textContent);
    document.getElementById('data-atualizacao').textContent = data.atualizado_em;
    document.getElementById('kpi-total').textContent = data.total;
    document.getElementById('kpi-vigentes').textContent = data.por_status['Vigente'] || 0;
    document.getElementById('kpi-revogadas').textContent = (data.por_status['Revogada'] || 0) + (data.por_status['Suspensa'] || 0);

    new Chart(document.getElementById('chartAno'), {{
      type: 'bar',
      data: {{
        labels: Object.keys(data.por_ano),
        datasets: [{{ label: 'Normas', data: Object.values(data.por_ano), backgroundColor: '#0284c7' }}]
      }},
      options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
    }});

    new Chart(document.getElementById('chartTipo'), {{
      type: 'doughnut',
      data: {{
        labels: Object.keys(data.por_tipo),
        datasets: [{{ data: Object.values(data.por_tipo), backgroundColor: ['#0284c7', '#38bdf8', '#818cf8', '#c084fc'] }}]
      }}
    }});

    new Chart(document.getElementById('chartMacro'), {{
      type: 'bar',
      data: {{
        labels: Object.keys(data.por_macro),
        datasets: [{{ label: 'Documentos', data: Object.values(data.por_macro), backgroundColor: '#10b981' }}]
      }},
      options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ display: false }} }} }}
    }});

    new Chart(document.getElementById('chartStatus'), {{
      type: 'pie',
      data: {{
        labels: Object.keys(data.por_status),
        datasets: [{{ data: Object.values(data.por_status), backgroundColor: ['#16a34a', '#dc2626', '#f59e0b'] }}]
      }}
    }});
  </script>
</body>
</html>
"""
    with open(ESTATISTICAS_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
