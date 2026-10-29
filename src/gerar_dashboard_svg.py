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

    # Identifica menor e maior ano dos documentos existentes
    anos_presentes = [int(d["ano"]) for d in docs if str(d.get("ano", "")).isdigit()]
    min_ano = min(anos_presentes) if anos_presentes else 2020
    max_ano_coletado = max(anos_presentes) if anos_presentes else 2026
    faixa_anos = f"{min_ano}–{max_ano_coletado}"

    # Contagens por ano
    por_ano = {}
    for a in range(min_ano, max_ano_coletado + 1):
        por_ano[str(a)] = 0
    for d in docs:
        ano = str(d.get("ano", "Outros"))
        if ano in por_ano:
            por_ano[ano] += 1
        else:
            por_ano[ano] = 1

    # Contagens por status
    vigentes = sum(1 for d in docs if d.get("status") == "Vigente")
    revogadas = sum(1 for d in docs if d.get("status") in ["Revogada", "Suspensa"])

    # Contagens por Macro-tema
    por_macro = {}
    for d in docs:
        m = d.get("macro_tema", "Outros")
        por_macro[m] = por_macro.get(m, 0) + 1

    data_str = datetime.now().strftime("%d/%m/%Y")

    # Dimensões do SVG (900 x 440)
    w, h = 900, 440

    # Dados do gráfico de barras por ano
    anos_chaves = list(por_ano.keys())
    anos_valores = list(por_ano.values())
    max_ano_val = max(anos_valores) if anos_valores else 1

    # Construção dinâmica das barras por ano (painel esquerdo de x=30 até x=445 -> largura útil ~384)
    bars_ano_svg = []
    num_barras = len(anos_chaves)
    area_util_w = 384
    x_offset_base = 43
    spacing = area_util_w / max(num_barras, 1)
    bar_width = max(6, int(spacing * 0.68))
    chart_y_bottom = 370
    chart_h = 135

    # Se forem muitos anos, ajusta o tamanho da fonte
    if num_barras > 18:
        font_ano = "7.5"
        font_val = "7.5"
    elif num_barras > 10:
        font_ano = "9"
        font_val = "9"
    else:
        font_ano = "11"
        font_val = "11"

    for i, (ano, val) in enumerate(zip(anos_chaves, anos_valores)):
        b_h = int((val / max_ano_val) * chart_h) if max_ano_val else 0
        b_y = chart_y_bottom - b_h
        bx = int(x_offset_base + (i * spacing) + (spacing - bar_width) / 2)
        # Barra
        bars_ano_svg.append(f'<rect x="{bx}" y="{b_y}" width="{bar_width}" height="{b_h}" rx="3" fill="url(#blueGrad)" />')
        # Valor acima da barra
        bars_ano_svg.append(f'<text x="{bx + bar_width/2}" y="{b_y - 4}" text-anchor="middle" font-size="{font_val}" font-weight="600" fill="#38bdf8">{val}</text>')
        # Rótulo do ano (mostra 2 dígitos se forem muitos anos ou 4 dígitos)
        rotulo_ano = ano[2:] if num_barras > 12 else ano
        bars_ano_svg.append(f'<text x="{bx + bar_width/2}" y="{chart_y_bottom + 16}" text-anchor="middle" font-size="{font_ano}" fill="#94a3b8">{rotulo_ano}</text>')

    # Dados do gráfico horizontal de Macro-temas (painel direito)
    macros_ordenados = sorted(por_macro.items(), key=lambda x: x[1], reverse=True)[:5]
    max_macro = max(x[1] for x in macros_ordenados) if macros_ordenados else 1
    macro_bars_svg = []
    my_start = 232
    # Painel direito vai de x=465 a x=870 (largura 405)
    # Rótulo em 485, Barra de 640 a 790 (largura 150), Valor em 805 text-anchor start
    m_bar_max_w = 150

    for i, (macro_nome, m_val) in enumerate(macros_ordenados):
        bw = int((m_val / max_macro) * m_bar_max_w)
        cy = my_start + (i * 28)
        # Nome do macro tema
        nome_curto = macro_nome.replace(" & ", "/").replace("Profissional", "Prof.")
        macro_bars_svg.append(f'<text x="485" y="{cy + 13}" font-size="11" fill="#cbd5e1" font-weight="500">{nome_curto}</text>')
        # Barra de fundo
        macro_bars_svg.append(f'<rect x="640" y="{cy + 3}" width="{m_bar_max_w}" height="12" rx="3" fill="#1e293b" />')
        # Barra preenchida
        macro_bars_svg.append(f'<rect x="640" y="{cy + 3}" width="{bw}" height="12" rx="3" fill="url(#emeraldGrad)" />')
        # Valor do número
        macro_bars_svg.append(f'<text x="802" y="{cy + 13}" font-size="11" fill="#10b981" font-weight="600">{m_val}</text>')

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
    <text x="28" y="14" class="title">CFM NORMAS — ACERVO REGULATÓRIO OFICIAL ({faixa_anos})</text>
    <text x="28" y="32" class="subtitle">Acervo público em Markdown com status de vigência e tags para agentes de IA • Atualizado em: {data_str}</text>
  </g>

  <!-- 4 Cartões KPI -->
  <g transform="translate(30, 78)">
    <!-- KPI 1: Total -->
    <rect x="0" y="0" width="200" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="16" y="22" class="card-label">Total de Normas</text>
    <text x="16" y="52" class="card-val" fill="#38bdf8">{total}</text>
    <text x="16" y="66" class="card-sub">100% da meta oficial ({faixa_anos})</text>

    <!-- KPI 2: Vigentes -->
    <rect x="213" y="0" width="200" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="229" y="22" class="card-label">Normas Vigentes</text>
    <text x="229" y="52" class="card-val" fill="#10b981">{vigentes}</text>
    <text x="229" y="66" class="card-sub">{((vigentes/total)*100):.1f}% do acervo total</text>

    <!-- KPI 3: Revogadas / Suspensas -->
    <rect x="426" y="0" width="200" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="442" y="22" class="card-label">Revogadas / Alteradas</text>
    <text x="442" y="52" class="card-val" fill="#f87171">{revogadas}</text>
    <text x="442" y="66" class="card-sub">Com IDs canônicos de rastreio</text>

    <!-- KPI 4: IA & LGPD -->
    <rect x="639" y="0" width="201" height="74" rx="8" fill="url(#cardGrad)" stroke="#334155" stroke-width="1" />
    <text x="655" y="22" class="card-label">IA, LGPD &amp; Telemedicina</text>
    <text x="655" y="52" class="card-val" fill="#c084fc">{total_ia}</text>
    <text x="655" y="66" class="card-sub">Catálogo curado para LLMs</text>
  </g>

  <!-- Painel Esquerdo: Publicações por Ano -->
  <g transform="translate(30, 172)">
    <rect x="0" y="0" width="415" height="228" rx="8" fill="#111c30" stroke="#1e293b" stroke-width="1" />
    <text x="18" y="26" class="section-title">Publicações por Ano ({faixa_anos})</text>
    <line x1="18" y1="198" x2="397" y2="198" stroke="#334155" stroke-width="1" stroke-dasharray="3 3" />
  </g>
  {' '.join(bars_ano_svg)}

  <!-- Painel Direito: Macro-Temas -->
  <g transform="translate(465, 172)">
    <rect x="0" y="0" width="405" height="228" rx="8" fill="#111c30" stroke="#1e293b" stroke-width="1" />
    <text x="18" y="26" class="section-title">Distribuição por Macro-Tema</text>
  </g>
  {' '.join(macro_bars_svg)}

  <!-- Rodapé -->
  <g transform="translate(30, 422)">
    <text x="0" y="0" font-size="10" fill="#64748b">⚡ Automação semanal contínua via GitHub Actions • Licença Pública CC-BY 4.0 • md-augustolinhares/cfm-normas</text>
  </g>
</svg>'''

    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Dashboard SVG gerado com sucesso em: {SVG_PATH}")


if __name__ == "__main__":
    gerar_dashboard_svg()
