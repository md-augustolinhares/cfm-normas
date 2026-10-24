"""
Gera o card de métricas e estatísticas em formato SVG vetorial
para exibição direta no README.md do GitHub.
"""
from datetime import datetime
import json
from pathlib import Path
import sys

# Suporte a execução direta
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import BASE_DIR, CATALOGO_GLOBAL_PATH, CATALOGO_IA_PATH

SVG_PATH = BASE_DIR / "docs" / "assets" / "dashboard.svg"


def gerar_dashboard_svg():
    with open(CATALOGO_GLOBAL_PATH, "r", encoding="utf-8") as f:
        catalogo = json.load(f)

    with open(CATALOGO_IA_PATH, "r", encoding="utf-8") as f:
        catalogo_ia = json.load(f)

    docs = catalogo["documentos"]
    total = len(docs)
    total_ia = catalogo_ia.get("total_documentos_ia_dados", 0)

    # Contagens por ano
    por_ano = {}
    for ano in range(2020, 2027):
        por_ano[str(ano)] = 0
    for d in docs:
        ano = str(d.get("ano", "Outros"))
        por_ano[ano] = por_ano.get(ano, 0) + 1

    # Contagens por status
    vigentes = sum(1 for d in docs if d.get("status") == "Vigente")
    revogadas = sum(1 for d in docs if d.get("status") in ["Revogada", "Suspensa"])

    # Contagens por Macro-tema
    por_macro = {}
    for d in docs:
        m = d.get("macro_tema", "Outros")
        por_macro[m] = por_macro.get(m, 0) + 1

    data_str = datetime.now().strftime("%d/%m/%Y")

    # Dimensões do SVG
    w, h = 880, 430

    # Dados do gráfico de barras por ano
    anos_chaves = list(por_ano.keys())
    anos_valores = list(por_ano.values())
    max_ano = max(anos_valores) if anos_valores else 1

    # Construção das barras por ano
    bars_ano_svg = []
    x_start = 55
    bar_width = 32
    spacing = 52
    chart_y_bottom = 360
    chart_h = 130

    for i, (ano, val) in enumerate(zip(anos_chaves, anos_valores)):
        b_h = int((val / max_ano) * chart_h) if max_ano else 0
        b_y = chart_y_bottom - b_h
        bx = x_start + (i * spacing)
        # Barra
        bars_ano_svg.append(f'<rect x="{bx}" y="{b_y}" width="{bar_width}" height="{b_h}" rx="4" fill="url(#blueGrad)" />')
        # Valor acima da barra
        bars_ano_svg.append(f'<text x="{bx + bar_width/2}" y="{b_y - 6}" text-anchor="middle" font-size="11" font-weight="600" fill="#38bdf8">{val}</text>')
        # Rótulo do ano
        bars_ano_svg.append(f'<text x="{bx + bar_width/2}" y="{chart_y_bottom + 18}" text-anchor="middle" font-size="11" fill="#94a3b8">{ano}</text>')

    # Dados do gráfico horizontal de Macro-temas
    macros_ordenados = sorted(por_macro.items(), key=lambda x: x[1], reverse=True)[:5]
    max_macro = max(x[1] for x in macros_ordenados) if macros_ordenados else 1
    macro_bars_svg = []
    my_start = 228
    m_bar_max_w = 210

    for i, (macro_nome, m_val) in enumerate(macros_ordenados):
        bw = int((m_val / max_macro) * m_bar_max_w)
        cy = my_start + (i * 26)
        pct = (m_val / total) * 100 if total else 0
        # Nome do macro tema (abreviado se longo)
        nome_curto = macro_nome.replace(" & ", "/").replace("Profissional", "Prof.")
        macro_bars_svg.append(f'<text x="490" y="{cy + 13}" font-size="11" fill="#cbd5e1" font-weight="500">{nome_curto}</text>')
        # Barra de fundo
        macro_bars_svg.append(f'<rect x="650" y="{cy + 3}" width="{m_bar_max_w}" height="12" rx="3" fill="#1e293b" />')
        # Barra preenchida
        macro_bars_svg.append(f'<rect x="650" y="{cy + 3}" width="{bw}" height="12" rx="3" fill="url(#emeraldGrad)" />')
        # Valor / Porcentagem
        macro_bars_svg.append(f'<text x="{650 + m_bar_max_w + 10}" y="{cy + 13}" font-size="11" fill="#10b981" font-weight="600">{m_val}</text>')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="max-width: {w}px;">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0b1120" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <linearGradient id="cardGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e293b" />
      <stop offset="100%" stop-color="#141f33" />
    </linearGradient>
    <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#0284c7" />
    </linearGradient>
    <linearGradient id="emeraldGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#10b981" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
  </defs>

  <style>
    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    .title {{ font-size: 16px; font-weight: 700; fill: #f8fafc; letter-spacing: 0.5px; }}
    .subtitle {{ font-size: 12px; fill: #94a3b8; }}
    .card-label {{ font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; fill: #94a3b8; }}
    .card-val {{ font-size: 24px; font-weight: 800; }}
    .card-sub {{ font-size: 10px; fill: #64748b; font-weight: 500; }}
    .section-title {{ font-size: 12px; font-weight: 700; fill: #e2e8f0; text-transform: uppercase; letter-spacing: 0.6px; }}
  </style>

  <!-- Fundo Principal -->
  <rect width="{w}" height="{h}" rx="14" fill="url(#bgGrad)" stroke="#1e293b" stroke-width="1.5" />

  <!-- Cabeçalho -->
  <g transform="translate(30, 24)">
    <circle cx="10" cy="10" r="10" fill="#0284c7" />
    <path d="M7 10L9 12L13 8" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    <text x="28" y="14" class="title">CFM NORMAS — ACERVO REGULATÓRIO OFICIAL (2020–2026)</text>
    <text x="28" y="32" class="subtitle">Acervo público em Markdown com status de vigência e tags para agentes de IA • Atualizado em: {data_str}</text>
  </g>

  <!-- 4 Cartões KPI -->
  <g transform="translate(30, 78)">
    <!-- KPI 1: Total -->
    <rect x="0" y="0" width="195" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="16" y="22" class="card-label">Total de Normas</text>
    <text x="16" y="52" class="card-val" fill="#38bdf8">{total}</text>
    <text x="16" y="66" class="card-sub">100% da meta oficial (2020-2026)</text>

    <!-- KPI 2: Vigentes -->
    <rect x="208" y="0" width="195" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="224" y="22" class="card-label">Normas Vigentes</text>
    <text x="224" y="52" class="card-val" fill="#10b981">{vigentes}</text>
    <text x="224" y="66" class="card-sub">{((vigentes/total)*100):.1f}% do acervo total</text>

    <!-- KPI 3: Revogadas / Suspensas -->
    <rect x="416" y="0" width="195" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="432" y="22" class="card-label">Revogadas / Alteradas</text>
    <text x="432" y="52" class="card-val" fill="#f87171">{revogadas}</text>
    <text x="432" y="66" class="card-sub">Com IDs canônicos de rastreio</text>

    <!-- KPI 4: IA & LGPD -->
    <rect x="624" y="0" width="195" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="640" y="22" class="card-label">IA, LGPD &amp; Telemedicina</text>
    <text x="640" y="52" class="card-val" fill="#c084fc">{total_ia}</text>
    <text x="640" y="66" class="card-sub">Catálogo curado para LLMs</text>
  </g>

  <!-- Painel Esquerdo: Publicações por Ano -->
  <g transform="translate(30, 172)">
    <rect x="0" y="0" width="418" height="218" rx="8" fill="#111c30" stroke="#1e293b" stroke-width="1" />
    <text x="18" y="26" class="section-title">Publicações por Ano (2020–2026)</text>
    <line x1="18" y1="188" x2="400" y2="188" stroke="#334155" stroke-width="1" stroke-dasharray="3 3" />
  </g>
  {' '.join(bars_ano_svg)}

  <!-- Painel Direito: Macro-Temas -->
  <g transform="translate(470, 172)">
    <rect x="0" y="0" width="380" height="218" rx="8" fill="#111c30" stroke="#1e293b" stroke-width="1" />
    <text x="18" y="26" class="section-title">Distribuição por Macro-Tema</text>
  </g>
  {' '.join(macro_bars_svg)}

  <!-- Rodapé -->
  <g transform="translate(30, 412)">
    <text x="0" y="0" font-size="10" fill="#64748b">⚡ Automação semanal contínua via GitHub Actions • Licença Pública CC-BY 4.0 • md-augustolinhares/cfm-normas</text>
  </g>
</svg>'''

    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Dashboard SVG gerado com sucesso em: {SVG_PATH}")


if __name__ == "__main__":
    gerar_dashboard_svg()
