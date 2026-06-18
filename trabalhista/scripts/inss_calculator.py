#!/usr/bin/env python3
"""
Calculadora de INSS Progressivo 2026 — Empregado CLT
Autor: Alisson Santos — github.com/AlissonSantos1/brasil-legal-skills
Copyright (c) 2026 Alisson Santos. Licença MIT.
"""
__author__ = "Alisson Santos"
__copyright__ = "Copyright (c) 2026 Alisson Santos"
__license__ = "MIT"
__source__ = "https://github.com/AlissonSantos1/brasil-legal-skills"

import argparse

# Tabela progressiva INSS 2026 — Empregado CLT (faixa, alíquota)
TABELA_CLT = [
    (1_518.00,  0.075),
    (2_793.88,  0.090),
    (4_190.83,  0.120),
    (8_157.41,  0.140),
]

TETO_INSS    = 8_157.41
SALARIO_MIN  = 1_518.00

# Contribuição autônomo (contribuinte individual)
ALIQ_AUTONOMO_PLENO      = 0.20  # 20% — todos os benefícios
ALIQ_AUTONOMO_SIMPLES    = 0.11  # 11% — aposenta só por idade
ALIQ_MEI                 = 0.05  # 5% do salário mínimo
VALOR_MEI_2026           = SALARIO_MIN * ALIQ_MEI  # R$ 75,90


def calcular_inss_clt(salario: float) -> dict:
    """Calcula INSS progressivo para empregado CLT 2026."""
    base = min(salario, TETO_INSS)
    total = 0.0
    detalhes = []
    anterior = 0.0

    for limite, aliquota in TABELA_CLT:
        if base <= anterior:
            break
        faixa_valor = min(base, limite) - anterior
        contribuicao = faixa_valor * aliquota
        total += contribuicao
        detalhes.append({
            "faixa": f"até R$ {limite:,.2f}",
            "aliquota_pct": aliquota * 100,
            "base_faixa": faixa_valor,
            "contribuicao": contribuicao,
        })
        anterior = limite
        if base <= limite:
            break

    return {
        "salario_bruto": salario,
        "base_calculo": base,
        "detalhes": detalhes,
        "total_inss": total,
        "aliquota_efetiva_pct": (total / salario * 100) if salario > 0 else 0,
    }


def calcular_inss_autonomo(salario_contribuicao: float, plano: str = "pleno") -> dict:
    """Calcula INSS para autônomo/contribuinte individual 2026."""
    base = max(SALARIO_MIN, min(salario_contribuicao, TETO_INSS))
    aliquota = ALIQ_AUTONOMO_SIMPLES if plano == "simplificado" else ALIQ_AUTONOMO_PLENO
    total = base * aliquota
    return {
        "salario_contribuicao": base,
        "plano": plano,
        "aliquota_pct": aliquota * 100,
        "total_inss": total,
        "observacao": (
            "Garante todos os benefícios (inclusive aposentadoria por tempo)."
            if plano == "pleno"
            else "Aposenta apenas por idade. Não permite aposentadoria por tempo de contribuição."
        ),
    }


def main():
    parser = argparse.ArgumentParser(
        description=f"Calculadora INSS 2026 | {__author__} | {__source__}"
    )
    parser.add_argument("--salario", type=float, required=True,
                        help="Salário bruto mensal (R$)")
    parser.add_argument("--tipo", choices=["clt", "autonomo-pleno", "autonomo-simplificado", "mei"],
                        default="clt", help="Tipo de contribuição (padrão: clt)")
    args = parser.parse_args()

    print("\n" + "=" * 56)
    print("  CÁLCULO INSS 2026")
    print("=" * 56)

    if args.tipo == "clt":
        r = calcular_inss_clt(args.salario)
        print(f"  Modalidade: Empregado CLT (progressivo)")
        print(f"  Salário bruto:  R$ {r['salario_bruto']:>10,.2f}")
        print(f"  Base de cálculo: R$ {r['base_calculo']:>9,.2f}")
        if r["salario_bruto"] > TETO_INSS:
            print(f"  ⚠️  Salário acima do teto — INSS calculado sobre R$ {TETO_INSS:,.2f}")
        print()
        print("  FAIXAS PROGRESSIVAS:")
        for d in r["detalhes"]:
            print(f"  {d['faixa']:>22}  {d['aliquota_pct']:>4.1f}%"
                  f"  × R$ {d['base_faixa']:>9,.2f}  = R$ {d['contribuicao']:>8,.2f}")
        print("  " + "-" * 52)
        print(f"  INSS TOTAL:           R$ {r['total_inss']:>10,.2f}")
        print(f"  Alíquota efetiva:      {r['aliquota_efetiva_pct']:>9.2f}%")

    elif args.tipo == "mei":
        print(f"  Modalidade: MEI")
        print(f"  Contribuição fixa: 5% × R$ {SALARIO_MIN:,.2f} = R$ {VALOR_MEI_2026:.2f}/mês")
        print(f"  ⚠️  MEI aposenta apenas por IDADE (mín. 60F / 65M + 15 anos contrib.)")
        print(f"  ⚠️  Não garante aposentadoria por TEMPO de contribuição.")

    else:
        plano = "simplificado" if "simplificado" in args.tipo else "pleno"
        r = calcular_inss_autonomo(args.salario, plano)
        print(f"  Modalidade: Autônomo — plano {r['plano']}")
        print(f"  Salário de contribuição: R$ {r['salario_contribuicao']:>8,.2f}")
        print(f"  Alíquota:               {r['aliquota_pct']:>8.1f}%")
        print(f"  INSS MENSAL:            R$ {r['total_inss']:>8,.2f}")
        print(f"\n  📋 {r['observacao']}")

    print("=" * 56)
    print("\n⚠️  Consulte um contador para planejamento previdenciário.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
