#!/usr/bin/env python3
"""
Parser de arquivo .DBK / .REC do Programa IRPF da Receita Federal
Extrai dados da declaração para análise pela skill brasil-legal-skills.
Autor: Alisson Santos — github.com/AlissonSantos1/brasil-legal-skills
Copyright (c) 2026 Alisson Santos. Licença MIT.
"""
__author__ = "Alisson Santos"
__copyright__ = "Copyright (c) 2026 Alisson Santos"
__license__ = "MIT"
__source__ = "https://github.com/AlissonSantos1/brasil-legal-skills"

import zipfile
import xml.etree.ElementTree as ET
import argparse
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mascarar_cpf(cpf: str) -> str:
    digits = "".join(c for c in cpf if c.isdigit())
    if len(digits) == 11:
        return f"***.{digits[3:6]}.{digits[6:9]}-**"
    return "***.***.***-**"


def _mascarar_nome(nome: str) -> str:
    partes = nome.strip().split()
    if len(partes) == 1:
        n = partes[0]
        return n[0] + "*" * (len(n) - 1) if len(n) > 1 else n
    primeiro = partes[0]
    ultimo = partes[-1]
    return f"{primeiro} {'* ' * (len(partes) - 2)}{ultimo}".strip()


def _fmt_brl(valor_str: str) -> str:
    if not valor_str:
        return "R$ 0,00"
    try:
        v = valor_str.replace(".", "").replace(",", ".")
        return f"R$ {float(v):,.2f}"
    except Exception:
        return valor_str


def _tag(elemento) -> str:
    """Remove namespace de uma tag XML."""
    return elemento.tag.split("}")[-1] if "}" in elemento.tag else elemento.tag


def _buscar(raiz, *chaves) -> str | None:
    """Busca recursiva case-insensitive por tag ou atributo."""
    chaves_lower = {c.lower() for c in chaves}
    for elem in raiz.iter():
        if _tag(elem).lower() in chaves_lower:
            if elem.text and elem.text.strip():
                return elem.text.strip()
        for attr, val in elem.attrib.items():
            if attr.lower() in chaves_lower and val.strip():
                return val.strip()
    return None


def _contar_dependentes(raiz) -> int:
    count = 0
    for elem in raiz.iter():
        t = _tag(elem).lower()
        if "dependente" in t and len(list(elem)) > 0:
            count += 1
    return count


def _listar_bens(raiz) -> list[dict]:
    bens = []
    for elem in raiz.iter():
        if _tag(elem).lower() in ("bem", "bememdireito", "bemdireito"):
            descr = _buscar(elem, "descricao", "discriminacao", "nmBem") or "—"
            valor = _buscar(elem, "situacaoAtual", "vlrBemAtual", "valor")
            bens.append({"descricao": descr[:60], "valor": _fmt_brl(valor) if valor else "—"})
    return bens[:10]  # Limita a 10 para não poluir output


# ---------------------------------------------------------------------------
# Leitura do arquivo
# ---------------------------------------------------------------------------

def _abrir_zip(caminho: Path) -> dict[str, bytes] | None:
    try:
        with zipfile.ZipFile(caminho, "r") as zf:
            return {n: zf.read(n) for n in zf.namelist()}
    except zipfile.BadZipFile:
        return None


def _parse_xml(conteudo: bytes) -> ET.Element | None:
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            texto = conteudo.decode(enc, errors="replace")
            # Remove prólogo XML mal formado se necessário
            if "<?" in texto and "?>" in texto:
                pass
            return ET.fromstring(texto)
        except ET.ParseError:
            continue
    return None


# ---------------------------------------------------------------------------
# Análise da declaração
# ---------------------------------------------------------------------------

def analisar(raiz: ET.Element) -> dict:
    d = {}

    # Identificação
    cpf = _buscar(raiz, "CPF", "NrCpf", "numeroCpf", "cpfContribuinte")
    nome = _buscar(raiz, "NOME", "NmContribuinte", "nomeContribuinte", "nmDeclarante")
    ano = _buscar(raiz, "anoCalendario", "AnoCalendario", "anoExercicio", "ANO")
    tipo = _buscar(raiz, "tipoDeclaracao", "TipoDeclaracao", "tpDeclaracao")

    if cpf:
        d["cpf"] = _mascarar_cpf(cpf)
    if nome:
        d["nome"] = _mascarar_nome(nome)
    if ano:
        d["ano_calendario"] = ano
    if tipo:
        d["tipo_declaracao"] = tipo

    # Rendimentos
    rend_trib = _buscar(raiz, "totalRendTrib", "vlrRendTributavel", "rendTributavelTotal")
    rend_isen = _buscar(raiz, "totalRendIsen", "vlrRendIsentos", "rendIsento")
    rend_excl = _buscar(raiz, "totalRendExcl", "vlrRendExclusivo")

    if rend_trib:
        d["rendimentos_tributaveis"] = _fmt_brl(rend_trib)
    if rend_isen:
        d["rendimentos_isentos"] = _fmt_brl(rend_isen)
    if rend_excl:
        d["rendimentos_exclusivos"] = _fmt_brl(rend_excl)

    # Deduções
    ded_total = _buscar(raiz, "totalDeducoes", "vlrDeducoes", "deducaoTotal")
    ded_saude = _buscar(raiz, "totalDespMedica", "vlrDespMedica", "despMedica")
    ded_educ = _buscar(raiz, "totalDespInstr", "vlrDespInstr", "despEducacao")
    ded_inss = _buscar(raiz, "contribuicaoPrevidOficial", "vlrPrevidOficial", "inss")
    ded_pgbl = _buscar(raiz, "contribuicaoPrevidCompl", "vlrPrevidCompl", "pgbl")

    if ded_total:
        d["deducoes_totais"] = _fmt_brl(ded_total)
    if ded_saude:
        d["deducao_saude"] = _fmt_brl(ded_saude)
    if ded_educ:
        d["deducao_educacao"] = _fmt_brl(ded_educ)
    if ded_inss:
        d["deducao_inss"] = _fmt_brl(ded_inss)
    if ded_pgbl:
        d["deducao_pgbl_previdencia_privada"] = _fmt_brl(ded_pgbl)

    # Imposto
    base = _buscar(raiz, "baseCalculo", "vlrBaseCalculo", "baseIR")
    devido = _buscar(raiz, "impostoDev", "vlrImpostoDev", "impostoDevido", "impDevido")
    retido = _buscar(raiz, "impostoRet", "vlrImpostoRet", "impostoRetidoFonte")
    saldo = _buscar(raiz, "saldoIR", "vlrSaldoIR", "saldoRestituir", "saldoPagar")

    if base:
        d["base_calculo"] = _fmt_brl(base)
    if devido:
        d["imposto_devido"] = _fmt_brl(devido)
    if retido:
        d["imposto_retido_na_fonte"] = _fmt_brl(retido)
    if saldo:
        saldo_num = float(saldo.replace(".", "").replace(",", ".")) if saldo else 0
        prefixo = "a restituir" if saldo_num > 0 else "a pagar"
        d[f"saldo_ir ({prefixo})"] = _fmt_brl(saldo)

    # Dependentes
    n_dep = _contar_dependentes(raiz)
    if n_dep > 0:
        d["dependentes_declarados"] = str(n_dep)

    # Bens
    total_bens = _buscar(raiz, "totalBens", "vlrBens", "patrimonioTotal")
    if total_bens:
        d["total_bens_e_direitos"] = _fmt_brl(total_bens)

    return d


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=f"Parser .DBK/.REC da Receita Federal | {__author__} | {__source__}"
    )
    parser.add_argument("--arquivo", required=True,
                        help="Caminho para o arquivo .DBK ou .REC do programa IRPF")
    parser.add_argument("--json", action="store_true",
                        help="Saída em JSON (para integração com outros scripts)")
    parser.add_argument("--estrutura", action="store_true",
                        help="Exibir estrutura XML (tags de primeiro nível)")
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    w = 62

    if not caminho.exists():
        print(f"\n❌ Arquivo não encontrado: {caminho}")
        return

    print(f"\n{'='*w}")
    print(f"  PARSER IRPF — {caminho.suffix.upper()}")
    print(f"  Arquivo : {caminho.name}")
    print(f"  Tamanho : {caminho.stat().st_size / 1024:.1f} KB")
    print(f"{'='*w}")

    # Tenta ZIP
    arquivos = _abrir_zip(caminho)
    if arquivos is None:
        print("\n⚠️  O arquivo não é um ZIP válido.")
        print("   Os formatos .DBK e .REC do Programa IRPF são arquivos ZIP internamente.")
        print("   Verifique se o arquivo não está corrompido ou se é de outra versão do programa.")
        return

    print(f"\n  📦 Conteúdo interno ({len(arquivos)} arquivo(s)):")
    for nome, conteudo in arquivos.items():
        print(f"     • {nome}  ({len(conteudo):,} bytes)")

    # Processa cada arquivo interno
    encontrados = []
    for nome, conteudo in arquivos.items():
        raiz = _parse_xml(conteudo)
        if raiz is not None:
            encontrados.append((nome, raiz))

    if not encontrados:
        print("\n⚠️  Nenhum XML reconhecível encontrado dentro do arquivo.")
        print("   O arquivo pode usar formato binário proprietário de versão mais antiga.")
        print("   Abra o arquivo no programa IRPF oficial e use a função 'Exportar Dados'.")
        return

    todos_dados = {}

    for nome, raiz in encontrados:
        print(f"\n  📄 {nome}  (tag raiz: <{_tag(raiz)}>)")

        dados = analisar(raiz)
        todos_dados[nome] = dados

        if dados:
            print(f"\n  DADOS EXTRAÍDOS:")
            for campo, valor in dados.items():
                label = campo.replace("_", " ").title()
                print(f"    {label:<38} {valor}")
        else:
            print("  (nenhum campo mapeado encontrado — use --estrutura para inspecionar)")

        if args.estrutura:
            print(f"\n  ESTRUTURA XML (nível 1):")
            for filho in raiz:
                n = len(list(filho))
                print(f"    <{_tag(filho)}> — {n} sub-elemento(s)")

        # Lista bens se encontrados
        bens = _listar_bens(raiz)
        if bens:
            print(f"\n  BENS E DIREITOS (primeiros {len(bens)}):")
            for b in bens:
                print(f"    • {b['descricao']:<50} {b['valor']}")

    if args.json:
        print(f"\n  JSON:")
        print(json.dumps(todos_dados, ensure_ascii=False, indent=2))

    print(f"\n{'='*w}")
    print("  ⚠️  Dados pessoais mascarados (CPF e nome parciais).")
    print("  ⚠️  Valores são estimativas extraídas do arquivo — confirme no programa oficial.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
