#!/usr/bin/env python3
"""
Calculadora CLT vs PJ — Qual realmente compensa mais? (2026)
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

# Tabela progressiva IRRF mensal 2026
TABELA_IRRF = [
    (2_259.00,   0.000,   0.00),
    (2_826.65,   0.075, 169.43),
    (3_751.05,   0.150, 381.44),
    (4_664.68,   0.225, 662.77),
    (float("inf"), 0.275, 895.83),
]

TETO_INSS    = 8_157.41
SALARIO_MIN  = 1_518.00
FGTS_PERC   = 0.08    # 8% depositado pelo empregador
DECIMO_PERC = 1/12    # 13° proporcional mensal
FERIAS_PERC = 1/12 * (4/3)  # férias + 1/3 proporcionais


def calcular_inss(salario: float) -> float:
    base = min(salario, TETO_INSS)
    total, anterior = 0.0, 0.0
    for limite, aliq in TABELA_INSS:
        if base <= anterior:
            break
        total += (min(base, limite) - anterior) * aliq
        anterior = limite
        if base <= limite:
            break
    return total


def calcular_irrf(base: float) -> float:
    for limite, aliq, ded in TABELA_IRRF:
        if base <= limite:
            return max(0.0, base * aliq - ded)
    return 0.0


def calcular_clt(salario: float, beneficios_mensais: float = 0.0) -> dict:
    """
    Calcula o valor real mensal de um pacote CLT.
    Considera: salário líquido + 13° mensal + férias mensais + FGTS + benefícios.
    """
    inss = calcular_inss(salario)
    irrf = calcular_irrf(max(0, salario - inss))
    liquido_base = salario - inss - irrf

    # Direitos trabalhistas rateados mensalmente
    fgts_mensal = salario * FGTS_PERC
    decimo_mensal = salario * DECIMO_PERC
    ferias_mensal = salario * FERIAS_PERC

    valor_total_mensal = liquido_base + fgts_mensal + decimo_mensal + ferias_mensal + beneficios_mensais

    # Custo total para empresa (referência)
    custo_empresa = salario * (1 + FGTS_PERC + DECIMO_PERC + FERIAS_PERC)

    return {
        "salario_bruto": salario,
        "inss": inss,
        "irrf": irrf,
        "liquido_base": liquido_base,
        "fgts_mensal": fgts_mensal,
        "decimo_mensal": decimo_mensal,
        "ferias_mensal": ferias_mensal,
        "beneficios_mensais": beneficios_mensais,
        "valor_real_mensal": valor_total_mensal,
        "custo_empresa_mensal": custo_empresa,
    }


def calcular_pj(contrato: float, regime: str = "mei",
                custos_operacionais: float = 500.0) -> dict:
    """
    Calcula o valor líquido real de um contrato PJ.
    Regimes: mei, simples3, simples5, autonomo_simples, autonomo_pleno
    """
    impostos = 0.0
    inss_pj = 0.0
    descricao_regime = ""

    if regime == "mei":
        # DAS fixo + sem IRPF sobre distribuição de lucros (até limite)
        das = SALARIO_MIN * 0.05 + 1.00 + 5.00  # INSS 5% + ICMS R$1 + ISS R$5
        impostos = das
        descricao_regime = "MEI (DAS fixo ~R$ 82/mês)"
        # MEI tem limite de R$ 81.000/ano = R$ 6.750/mês
        if contrato > 6_750:
            descricao_regime += " ⚠️ ATENÇÃO: acima do limite MEI (R$ 6.750/mês)"

    elif regime == "simples3":
        # Simples Nacional Anexo III — serviços (maioria dos devs/consultores)
        # Faixa 1: até R$ 180k/ano → alíquota efetiva ~6%
        aliquota = 0.06
        impostos = contrato * aliquota
        descricao_regime = f"Simples Nacional Anexo III (~{aliquota*100:.0f}% eff. faixa 1)"

    elif regime == "simples5":
        # Simples Nacional Anexo V — profissões regulamentadas
        aliquota = 0.155
        impostos = contrato * aliquota
        descricao_regime = f"Simples Nacional Anexo V (~{aliquota*100:.1f}% nominal faixa 1)"

    elif regime == "autonomo_simples":
        # Contribuinte individual — INSS 11% (plano simplificado) + IR carnê-leão
        inss_pj = min(contrato * 0.11, TETO_INSS * 0.11)
        base_ir = max(0, contrato - inss_pj)
        ir = calcular_irrf(base_ir)
        impostos = inss_pj + ir
        descricao_regime = "Autônomo — INSS 11% + IR carnê-leão (aposenta só por idade)"

    elif regime == "autonomo_pleno":
        # Contribuinte individual — INSS 20% + IR carnê-leão
        inss_pj = min(contrato * 0.20, TETO_INSS * 0.20)
        base_ir = max(0, contrato - inss_pj)
        ir = calcular_irrf(base_ir)
        impostos = inss_pj + ir
        descricao_regime = "Autônomo — INSS 20% + IR carnê-leão (todos os benefícios)"

    liquido = contrato - impostos - custos_operacionais

    return {
        "contrato_bruto": contrato,
        "regime": descricao_regime,
        "impostos_total": impostos,
        "custos_operacionais": custos_operacionais,
        "liquido_mensal": liquido,
        "aliquota_efetiva_pct": (impostos / contrato * 100) if contrato > 0 else 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description=f"CLT vs PJ — Qual compensa mais? 2026 | {__author__} | {__source__}"
    )
    parser.add_argument("--clt", type=float, required=True,
                        help="Salário CLT bruto mensal (R$)")
    parser.add_argument("--pj", type=float, required=True,
                        help="Valor do contrato PJ mensal (R$)")
    parser.add_argument("--beneficios", type=float, default=0,
                        help="Benefícios CLT mensais: VR + plano saúde + outros (R$)")
    parser.add_argument("--regime-pj", choices=["mei", "simples3", "simples5",
                        "autonomo_simples", "autonomo_pleno"],
                        default="simples3",
                        help="Regime tributário PJ (padrão: simples3)")
    parser.add_argument("--custos-pj", type=float, default=500,
                        help="Custos operacionais PJ mensais: contador, saúde, etc. (padrão: R$ 500)")
    args = parser.parse_args()

    clt = calcular_clt(args.clt, args.beneficios)
    pj  = calcular_pj(args.pj, args.regime_pj, args.custos_pj)

    diferenca = pj["liquido_mensal"] - clt["valor_real_mensal"]
    vantagem = "PJ" if diferenca > 0 else "CLT"
    w = 62

    print("\n" + "=" * w)
    print("  CLT vs PJ — COMPARATIVO REAL 2026")
    print("=" * w)

    print(f"\n  📋 CENÁRIO CLT — R$ {clt['salario_bruto']:,.2f} bruto")
    print(f"  (-) INSS:                    R$ {clt['inss']:>10,.2f}")
    print(f"  (-) IRRF:                    R$ {clt['irrf']:>10,.2f}")
    print(f"  = Líquido base:              R$ {clt['liquido_base']:>10,.2f}")
    print(f"  (+) FGTS (8%):               R$ {clt['fgts_mensal']:>10,.2f}")
    print(f"  (+) 13° (1/12 mensal):       R$ {clt['decimo_mensal']:>10,.2f}")
    print(f"  (+) Férias+1/3 (1/12):       R$ {clt['ferias_mensal']:>10,.2f}")
    if clt["beneficios_mensais"] > 0:
        print(f"  (+) Benefícios (VR, saúde): R$ {clt['beneficios_mensais']:>10,.2f}")
    print(f"  {'─'*(w-2)}")
    print(f"  ✅ VALOR REAL CLT/mês:        R$ {clt['valor_real_mensal']:>10,.2f}")

    print(f"\n  📋 CENÁRIO PJ — R$ {pj['contrato_bruto']:,.2f}/mês")
    print(f"  Regime: {pj['regime']}")
    print(f"  (-) Impostos:                R$ {pj['impostos_total']:>10,.2f}")
    print(f"      (alíquota efetiva:         {pj['aliquota_efetiva_pct']:>8.2f}%)")
    print(f"  (-) Custos operacionais:     R$ {pj['custos_operacionais']:>10,.2f}")
    print(f"      (contador, saúde, etc.)")
    print(f"  {'─'*(w-2)}")
    print(f"  ✅ VALOR REAL PJ/mês:         R$ {pj['liquido_mensal']:>10,.2f}")

    print(f"\n  {'='*(w-2)}")
    print(f"  RESULTADO: {vantagem} é mais vantajoso por R$ {abs(diferenca):,.2f}/mês")
    print(f"             (R$ {abs(diferenca)*12:,.2f}/ano  |  {abs(diferenca)/min(clt['valor_real_mensal'], pj['liquido_mensal'])*100:.1f}% a mais)")

    # Ponto de equilíbrio
    print(f"\n  💡 Para o PJ de R$ {args.pj:,.2f} ser equivalente ao CLT de R$ {args.clt:,.2f}:")
    print(f"     O PJ mínimo necessário seria: R$ {clt['valor_real_mensal'] + pj['impostos_total'] + pj['custos_operacionais']:,.2f}/mês")

    print(f"\n  ⚠️  ATENÇÃO — PJ não inclui por padrão:")
    print(f"  • FGTS (reserva de emergência)  • 13° salário  • Férias remuneradas")
    print(f"  • Seguro-desemprego             • Estabilidade • Aviso prévio")
    print("=" * w)
    print("\n⚠️  Simulação estimada. Consulte contador para planejamento tributário pessoal.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
