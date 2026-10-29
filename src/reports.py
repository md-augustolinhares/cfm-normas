"""
Módulo de geração de relatórios, catálogos, PROGRESSO.md e dashboard estatisticas.html.
"""
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List
import yaml

from src.config import (
    BASE_DIR,
    CATALOGO_GLOBAL_PATH,
    CATALOGO_IA_PATH,
    ESTATISTICAS_PATH,
    NORMAS_DIR,
    PROGRESSO_PATH,
    README_PATH,
)
from src.gerar_dashboard_svg import gerar_dashboard_svg


def carregar_todos_documentos_disco() -> List[Dict[str, Any]]:
    """
    Varre a pasta normas/ e carrega os frontmatters de todos os arquivos .md existentes.
    Garante que execuções parciais nunca apaguem normas de outros anos.
    """
    documentos = []
    if not NORMAS_DIR.exists():
        return documentos

    for p in NORMAS_DIR.rglob("*.md"):
        try:
            content = p.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if isinstance(fm, dict) and "id" in fm:
                        # Assegura caminhos
                        rel_path = p.relative_to(BASE_DIR).as_posix()
                        fm["caminho_relativo"] = rel_path
                        fm["url_raw"] = f"https://raw.githubusercontent.com/md-augustolinhares/cfm-normas/main/{rel_path}"
                        documentos.append(fm)
        except Exception as e:
            print(f"Aviso ao ler {p}: {e}")

    # Ordena por ano (desc), tipo e número
    documentos.sort(key=lambda d: (str(d.get("ano", "")), str(d.get("tipo", "")), str(d.get("numero", "")).zfill(6)), reverse=True)
    return documentos


def gerar_catalogos(documentos: List[Dict[str, Any]] = None):
    # Se não fornecido ou parcial, mescla com tudo o que existe no disco
    documentos_disco = carregar_todos_documentos_disco()
    if documentos:
        docs_map = {d["id"]: d for d in documentos_disco}
        for d in documentos:
            docs_map[d["id"]] = d
        documentos = list(docs_map.values())
    else:
        documentos = documentos_disco

    # Ordena documentos
    documentos.sort(key=lambda d: (str(d.get("ano", "")), str(d.get("tipo", "")), str(d.get("numero", "")).zfill(6)), reverse=True)
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

    # Atualiza o dashboard SVG automaticamente
    try:
        gerar_dashboard_svg()
    except Exception as e:
        print(f"Erro ao gerar dashboard SVG: {e}")

    # Atualiza o README.md automaticamente com as métricas do acervo
    try:
        atualizar_readme_metricas(documentos, len(docs_ia))
    except Exception as e:
        print(f"Erro ao atualizar métricas do README: {e}")


def gerar_progresso_md(documentos: List[Dict[str, Any]] = None):
    # Se não fornecido ou parcial, mescla com o que existe no disco
    documentos_disco = carregar_todos_documentos_disco()
    if documentos:
        docs_map = {d["id"]: d for d in documentos_disco}
        for d in documentos:
            docs_map[d["id"]] = d
        documentos = list(docs_map.values())
    else:
        documentos = documentos_disco

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

    anos_presentes = [int(d["ano"]) for d in documentos if str(d.get("ano", "")).isdigit()]
    min_ano = min(anos_presentes) if anos_presentes else 2010
    max_ano = max(anos_presentes) if anos_presentes else 2026
    faixa_anos = f"{min_ano}–{max_ano}"

    conteudo = f"""# Progresso do Acervo de Normas do CFM ({faixa_anos})

> **Última atualização:** {data_atual} (gerado automaticamente)  
> **Total de documentos processados:** {len(documentos)}

---

## 1. Volume por Categoria de Norma ({faixa_anos})

| Categoria | Coletados no Acervo | Status |
| :--- | :---: | :---: |
| **Resoluções** | {len(resolucoes)} | 🟢 Concluído |
| **Pareceres** | {len(pareceres)} | 🟢 Concluído |
| **Recomendações** | {len(recomendacoes)} | 🟢 Concluído |
| **Despachos Jurídicos** | {len(despachos)} | 🔹 Módulo Retroativo |
| **Total Global** | **{len(documentos)}** | 🟢 100% das Fases Concluídas ({faixa_anos}) |

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


def gerar_estatisticas_html(documentos: List[Dict[str, Any]] = None):
    # Se não fornecido ou parcial, mescla com o que existe no disco
    documentos_disco = carregar_todos_documentos_disco()
    if documentos:
        docs_map = {d["id"]: d for d in documentos_disco}
        for d in documentos:
            docs_map[d["id"]] = d
        documentos = list(docs_map.values())
    else:
        documentos = documentos_disco

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


def atualizar_readme_metricas(documentos: List[Dict[str, Any]], total_ia: int):
    """
    Mantém o título, badges e textos do README.md 100% sincronizados com o acervo real.
    """
    if not README_PATH.exists():
        return

    readme_content = README_PATH.read_text(encoding="utf-8")

    total = len(documentos)
    anos_presentes = [int(d["ano"]) for d in documentos if str(d.get("ano", "")).isdigit()]
    min_ano = min(anos_presentes) if anos_presentes else 2010
    max_ano = max(anos_presentes) if anos_presentes else 2026
    faixa_anos = f"{min_ano}–{max_ano}"

    # 1. Atualiza cabeçalho principal: # CFM Normas (2010–2026)
    readme_content = re.sub(
        r"^# CFM Normas \(\d{4}–\d{4}\)",
        f"# CFM Normas ({faixa_anos})",
        readme_content,
        flags=re.MULTILINE,
    )

    # 2. Atualiza badge do Acervo Oficial: Acervo_Oficial-{total}_Normas
    readme_content = re.sub(
        r"Acervo_Oficial-\d+_Normas",
        f"Acervo_Oficial-{total}_Normas",
        readme_content,
    )
    readme_content = re.sub(
        r'alt="\d+ Normas"',
        f'alt="{total} Normas"',
        readme_content,
    )

    # 3. Atualiza badge da Trilha IA & LGPD: Trilha_IA_&_LGPD-{total_ia}_Normas
    readme_content = re.sub(
        r"Trilha_IA_&_LGPD-\d+_Normas",
        f"Trilha_IA_&_LGPD-{total_ia}_Normas",
        readme_content,
    )

    # 4. Atualiza menção no texto de normas-chave
    readme_content = re.sub(
        r"Dentre as \*\*\d+ normas\*\* mapeadas na nossa trilha",
        f"Dentre as **{total_ia} normas** mapeadas na nossa trilha",
        readme_content,
    )

    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"README.md atualizado automaticamente com as métricas: {faixa_anos} | {total} normas | {total_ia} IA/LGPD.")
