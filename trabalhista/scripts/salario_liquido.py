#!/usr/bin/env python3
"""
Calculadora de Salário Líquido CLT 2026
INSS progressivo + IRRF mensal + benefícios
Autor: Alisson Santos — github.com/AlissonSantos1/brasil-legal-skills
Copyright (c) 2026 Alisson Santos. Licença MIT.
"""
__author__ = "Alisson Santos"
__copyright__ = "Copyright (c) 2026 Alisson Santos"
__license__ = "MIT"
__source__ = "https://github.com/AlissonSantos1/brasil-legal-skills"

import argparse

# Tabela progressiva INSS 2026
TABELA_INSS = [
    (1_518.00,  0.075),
    (2_793.88,  0.090),
    (4_190.83,  0.120),
    (8_157.41,  0.140),
]

# Tabela progressiva IRRF mensal 2026 (base mensal)
TABELA_IRRF = [
    (2_259.00,   0.000,   0.00),
    (2_826.65,   0.075, 169.43),
    (3_751.05,   0.150, 381.44),
    (4_664.68,   0.225, 662.77),
    (float("inf"), 0.275, 895.83),
]

DEDUCAO_DEPENDENTE_MENSAL = 189.59  # R$ 2.275,08 / 12
TETO_INSS = 8_157.41
PERCENTUAL_MAX_VT = 0.06  # 6% do salário bruto


def calcular_inss(salario: float) -> float:
    base = min(salario, TETO_INSS)
    total = 0.0
    anterior = 0.0
    for limite, aliquota in TABELA_INSS:
        if base <= anterior:
            break
        total += (min(base, limite) - anterior) * aliquota
        anterior = limite
        if base <= limite:
            break
    return total


def calcular_irrf(base_calculo: float) -> float:
    for limite, aliquota, deducao in TABELA_IRRF:
        if base_calculo <= limite:
            return max(0.0, base_calculo * aliquota - deducao)
    return 0.0


def calcular_salario_liquido(
    salario_bruto: float,
    dependentes: int = 0,
    vt_mensal: float = 0.0,
    vr_mensal: float = 0.0,
    plano_saude: float = 0.0,
    outros_descontos: float = 0.0,
) -> dict:
    inss = calcular_inss(salario_bruto)

    deducao_dependentes = dependentes * DEDUCAO_DEPENDENTE_MENSAL
    base_irrf = max(0.0, salario_bruto - inss - deducao_dependentes - plano_saude)
    irrf = calcular_irrf(base_irrf)

    desconto_vt = min(vt_mensal, salario_bruto * PERCENTUAL_MAX_VT)

    total_descontos = inss + irrf + desconto_vt + outros_descontos
    salario_liquido = salario_bruto - total_descontos

    return {
        "salario_bruto": salario_bruto,
        "inss": inss,
        "base_irrf": base_irrf,
        "irrf": irrf,
        "desconto_vt": desconto_vt,
        "outros_descontos": outros_descontos,
        "total_descontos": total_descontos,
        "salario_liquido": salario_liquido,
        "aliquota_efetiva_total_pct": (total_descontos / salario_bruto * 100) if salario_bruto > 0 else 0,
        "beneficios_recebidos": {
            "vale_transporte": vt_mensal,
            "vale_refeicao": vr_mensal,
            "plano_saude_empresa": plano_saude,
        },
        "valor_total_pacote": salario_liquido + vr_mensal,
    }


def main():
    parser = argparse.ArgumentParser(
        description=f"Calculadora de Salário Líquido CLT 2026 | {__author__} | {__source__}"
    )
    parser.add_argument("--bruto", type=float, required=True,
                        help="Salário bruto mensal (R$)")
    parser.add_argument("--dependentes", type=int, default=0,
                        help="Número de dependentes (reduz base do IRRF)")
    parser.add_argument("--vt", type=float, default=0,
                        help="Vale-transporte mensal recebido (R$) — desconto máx. 6%%")
    parser.add_argument("--vr", type=float, default=0,
                        help="Vale-refeição/alimentação mensal (R$) — sem desconto")
    parser.add_argument("--plano-saude", type=float, default=0,
                        help="Desconto plano de saúde no holerite (R$) — reduz base IRRF")
    parser.add_argument("--outros", type=float, default=0,
                        help="Outros descontos mensais (R$)")
    args = parser.parse_args()

    r = calcular_salario_liquido(
        args.bruto, args.dependentes, args.vt,
        args.vr, args.plano_saude, args.outros
    )

    w = 58
    print("\n" + "=" * w)
    print("  SALÁRIO LÍQUIDO CLT 2026")
    print("=" * w)
    print(f"  Salário bruto:               R$ {r['salario_bruto']:>10,.2f}")
    print()
    print("  DESCONTOS:")
    print(f"  (-) INSS progressivo:        R$ {r['inss']:>10,.2f}")
    if args.dependentes:
        print(f"      ({args.dependentes} dependente(s) — reduz base IRRF em R$ {args.dependentes * DEDUCAO_DEPENDENTE_MENSAL:,.2f})")
    print(f"  (-) IRRF (base R$ {r['base_irrf']:,.2f}):  R$ {r['irrf']:>10,.2f}")
    if r["desconto_vt"] > 0:
        print(f"  (-) Vale-transporte (6%):    R$ {r['desconto_vt']:>10,.2f}")
    if r["outros_descontos"] > 0:
        print(f"  (-) Outros descontos:        R$ {r['outros_descontos']:>10,.2f}")
    print("  " + "-" * (w - 2))
    print(f"  Total de descontos:          R$ {r['total_descontos']:>10,.2f}")
    print(f"  Alíquota efetiva total:       {r['aliquota_efetiva_total_pct']:>9.2f}%")
    print()
    print(f"  ✅ SALÁRIO LÍQUIDO:           R$ {r['salario_liquido']:>10,.2f}")

    b = r["beneficios_recebidos"]
    if any(v > 0 for v in b.values()):
        print()
        print("  BENEFÍCIOS (não descontados no líquido):")
        if b["vale_refeicao"] > 0:
            print(f"  (+) Vale-refeição/alimentação: R$ {b['vale_refeicao']:>8,.2f}")
        if b["plano_saude_empresa"] > 0:
            print(f"  (+) Plano de saúde empresa:    R$ {b['plano_saude_empresa']:>8,.2f}")
        print(f"\n  💼 PACOTE TOTAL ESTIMADO:     R$ {r['valor_total_pacote']:>10,.2f}")

    print("=" * w)
    print("\n⚠️  Sujeito a variações por convenção coletiva e benefícios específicos.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
