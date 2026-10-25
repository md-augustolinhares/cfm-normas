"""
CLI Principal de Execução da Coleta de Normas do CFM (2020–2026).
"""
import argparse
from pathlib import Path
import sys
from typing import List
import yaml

# Garante suporte a UTF-8 no terminal Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.classifier import classificar_norma
from src.config import NORMAS_DIR, TIPOS_MAP, URL_PDF_BASE
from src.crawler import baixar_pdf_em_memoria, buscar_metadados_ano
from src.exporter import (
    carregar_manifesto,
    construir_id_canonico,
    exportar_norma_markdown,
    salvar_manifesto,
)
from src.parser import extrair_texto_pdf, formatar_artigos_markdown
from src.reports import gerar_catalogos, gerar_estatisticas_html, gerar_progresso_md
from src.sanitizer import sanitizar_texto_norma


def processar_norma(meta: dict, manifesto: dict, force: bool = False) -> dict:
    tipo_cod = meta.get("IN_TIPO", "R")
    tipo_info = TIPOS_MAP.get(tipo_cod, TIPOS_MAP["R"])
    sname = tipo_info["sname"]
    pasta_tipo = tipo_info["pasta"]
    numero = str(meta.get("NUMERO", "0")).strip()
    ano = str(meta.get("ANO", "0")).strip()
    id_canonico = construir_id_canonico(tipo_cod, numero, ano)

    caminho_md = NORMAS_DIR / pasta_tipo / ano / f"{id_canonico}.md"
    id_norma_cfm = str(meta.get("ID_NORMA", ""))

    # Normaliza status
    is_revogada = str(meta.get("IS_REVOGADA", "")).strip().lower()
    if "revogada" in is_revogada:
        status_atual = "Revogada"
    elif "suspensa" in is_revogada:
        status_atual = "Suspensa"
    else:
        status_atual = "Vigente"

    # Se já existe no manifesto e o arquivo físico existe, verifica se houve alteração de status
    if not force and id_norma_cfm in manifesto and caminho_md.exists():
        try:
            content = caminho_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                fm_text = content.split("---", 2)[1]
                fm = yaml.safe_load(fm_text)
                if fm.get("status") == status_atual:
                    # Não mudou nada, pula download
                    return fm
        except Exception:
            pass

    ementa = meta.get("RESUMO", "")
    url_pdf = URL_PDF_BASE.format(sname=sname, ano=ano, numero=numero)

    print(f"  -> Baixando PDF em memória: {id_canonico} ({url_pdf})...")
    pdf_bytes = baixar_pdf_em_memoria(url_pdf)

    if pdf_bytes:
        raw_text, _ = extrair_texto_pdf(pdf_bytes)
        texto_limpo = sanitizar_texto_norma(raw_text)
        corpo_formatado = formatar_artigos_markdown(texto_limpo)
    else:
        print(f"     [AVISO] PDF não localizado para {id_canonico}. Usando ementa oficial.")
        corpo_formatado = f"*(Texto integral não disponível em PDF pelo portal do CFM no momento da coleta)*\n\n## Ementa Oficial\n{ementa}"

    macro_tema, tags, destaques = classificar_norma(ementa, corpo_formatado)

    doc_exportado = exportar_norma_markdown(
        metadados_cfm=meta,
        texto_corpo=corpo_formatado,
        macro_tema=macro_tema,
        tags=tags,
        destaques=destaques,
    )

    manifesto[id_norma_cfm] = doc_exportado["sha256_conteudo"]
    return doc_exportado


def executar_piloto():
    print("\n=== Executando Piloto (3 Normas Reais Selecionadas) ===")
    manifesto = carregar_manifesto()
    
    # 1. Resolução 2314/2022 (Telemedicina)
    # 2. Resolução 2271/2020 (UTI/UCI)
    # 3. Resolução 2416/2024 (Autonomia e Atos Médicos)
    pilotos = [
        {
            "ID_NORMA": "42200",
            "IN_TIPO": "R",
            "TIPO": "Resolução",
            "SNAME": "resolucoes",
            "NUMERO": "2314",
            "ANO": "2022",
            "DATA": "05-MAY-22",
            "RESUMO": "Define e regulamenta a telemedicina, como forma de serviços médicos mediados por tecnologias de comunicação.",
            "REVOGADA": "N",
            "IS_REVOGADA": "em vigor",
            "NUMERO_REVOGADA": "1643",
            "ANO_REVOGADA": "2002",
        },
        {
            "ID_NORMA": "40100",
            "IN_TIPO": "R",
            "TIPO": "Resolução",
            "SNAME": "resolucoes",
            "NUMERO": "2271",
            "ANO": "2020",
            "DATA": "14-FEB-20",
            "RESUMO": "Fixa as normas para funcionamento e infraestrutura das Unidades de Terapia Intensiva (UTI) e de Cuidados Intermediários (UCI).",
            "REVOGADA": "N",
            "IS_REVOGADA": "em vigor",
            "NUMERO_REVOGADA": None,
            "ANO_REVOGADA": None,
        },
        {
            "ID_NORMA": "44995",
            "IN_TIPO": "R",
            "TIPO": "Resolução",
            "SNAME": "resolucoes",
            "NUMERO": "2416",
            "ANO": "2024",
            "DATA": "10-OCT-24",
            "RESUMO": "Dispõe sobre os atos próprios dos médicos, sua autonomia, limites, responsabilidade e juridicidade.",
            "REVOGADA": "N",
            "IS_REVOGADA": "em vigor",
            "NUMERO_REVOGADA": None,
            "ANO_REVOGADA": None,
        },
    ]

    docs_processados = []
    for meta in pilotos:
        doc = processar_norma(meta, manifesto)
        docs_processados.append(doc)

    salvar_manifesto(manifesto)
    gerar_catalogos(docs_processados)
    gerar_progresso_md(docs_processados)
    gerar_estatisticas_html(docs_processados)
    print("\n✅ Piloto concluído com sucesso!")


def executar_coleta(anos: List[int], tipos: List[str]):
    print(f"\n=== Iniciando Coleta de Normas do CFM: Anos {anos} | Tipos {tipos} ===")
    manifesto = carregar_manifesto()
    todos_documentos = []

    for ano in anos:
        print(f"\n[Ano {ano}] Consultando metadados no portal do CFM...")
        metas = buscar_metadados_ano(ano=ano, tipos=tipos)
        print(f"[Ano {ano}] {len(metas)} registros identificados.")

        for i, meta in enumerate(metas, start=1):
            num = meta.get("NUMERO")
            tipo = meta.get("TIPO")
            print(f"[{i}/{len(metas)}] Processando {tipo} nº {num}/{ano}...")
            try:
                doc = processar_norma(meta, manifesto)
                todos_documentos.append(doc)
            except Exception as e:
                print(f"     [ERRO] Falha ao processar {tipo} {num}/{ano}: {e}")

        # Salva o manifesto ao final de cada ano para garantir checkpoint
        salvar_manifesto(manifesto)

    print("\nAtualizando Catálogos, PROGRESSO.md e estatisticas.html...")
    gerar_catalogos(todos_documentos)
    gerar_progresso_md(todos_documentos)
    gerar_estatisticas_html(todos_documentos)
    print(f"\n✅ Concluído! Total de {len(todos_documentos)} normas processadas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coletor de Normas CFM para Markdown")
    parser.add_argument("--piloto", action="store_true", help="Executa o teste piloto com 3 normas representativas")
    parser.add_argument("--ano", type=int, help="Executa a coleta para um único ano")
    parser.add_argument("--intervalo", nargs=2, type=int, metavar=("INICIO", "FIM"), help="Executa a coleta para um intervalo de anos (ex: --intervalo 2010 2019)")
    parser.add_argument("--todos", action="store_true", help="Executa a coleta completa de 2020 a 2026")
    parser.add_argument("--relatorios", action="store_true", help="Regenera todos os catálogos e relatórios a partir dos arquivos .md em disco")
    parser.add_argument("--tipos", nargs="+", default=["R", "P", "E"], help="Lista de tipos: R (Resoluções), P (Pareceres), E (Recomendações), D (Despachos)")

    args = parser.parse_args()

    if args.piloto:
        executar_piloto()
    elif args.relatorios:
        print("\nRegenerando catálogos e estatísticas a partir do disco...")
        gerar_catalogos()
        gerar_progresso_md()
        gerar_estatisticas_html()
        print("✅ Relatórios regenerados com sucesso!")
    elif args.ano:
        executar_coleta(anos=[args.ano], tipos=args.tipos)
    elif args.intervalo:
        anos = list(range(args.intervalo[0], args.intervalo[1] + 1))
        executar_coleta(anos=anos, tipos=args.tipos)
    elif args.todos:
        executar_coleta(anos=list(range(2020, 2027)), tipos=args.tipos)
    else:
        parser.print_help()
