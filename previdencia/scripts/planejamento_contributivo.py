#!/usr/bin/env python3
"""
Planejamento de Carreira Contributiva — INSS 2026
Simula estratégias de contribuição para maximizar benefício e antecipar aposentadoria.
Autor: Alisson Santos — github.com/AlissonSantos1/brasil-legal-skills
Copyright (c) 2026 Alisson Santos. Licença MIT.
"""
__author__ = "Alisson Santos"
__copyright__ = "Copyright (c) 2026 Alisson Santos"
__license__ = "MIT"
__source__ = "https://github.com/AlissonSantos1/brasil-legal-skills"

import argparse

ANO_ATUAL    = 2026
TETO_INSS    = 8_157.41
SALARIO_MIN  = 1_518.00

# Alíquotas de contribuição (contribuinte individual)
ALIQ = {
    "mei":          (SALARIO_MIN * 0.05,      "MEI — valor fixo (aposenta só por idade)"),
    "simplificado": (None,                    "11% do sal. contribuição (aposenta só por idade)"),
    "pleno":        (None,                    "20% do sal. contribuição (todos os benefícios)"),
}

# Regras permanentes (pós-reforma)
IDADE_TEMPO  = {"M": 62, "F": 57}
CONTRIB_TEMPO = {"M": 35, "F": 30}
IDADE_IDADE  = {"M": 65, "F": 62}
CONTRIB_IDADE = {"M": 15, "F": 15}

# Transição 2026
PONTOS_2026  = {"M": 103, "F": 93}


def _beneficio(salario_medio: float, anos_contrib: int, sexo: str) -> float:
    base_linha = 15 if sexo == "F" else 20
    taxa = min(0.60 + max(0, anos_contrib - base_linha) * 0.02, 1.0)
    return min(salario_medio, TETO_INSS) * taxa


def _anos_para_aposentar(idade: int, anos_contrib: int, sexo: str,
                         pre_reforma: bool) -> list[dict]:
    """Retorna lista de {regra, anos_restantes, idade_apos, contrib_apos, beneficio_estimado}."""
    cenarios = []

    def _add(regra, anos_esp, sal):
        idade_apos = idade + anos_esp
        contrib_apos = anos_contrib + anos_esp
        ben = _beneficio(sal, contrib_apos, sexo)
        cenarios.append({
            "regra": regra,
            "anos_restantes": round(anos_esp, 1),
            "idade_aposentadoria": round(idade_apos, 1),
            "contribuicoes_totais": round(contrib_apos, 1),
            "beneficio_estimado": ben,
        })

    return cenarios  # preenchido pelos chamadores


def calcular_cenarios(
    idade: int,
    anos_contrib: int,
    salario_atual: float,
    sexo: str,
    pre_reforma: bool,
    sal_contrib_historico: float | None = None,
) -> list[dict]:
    sal = sal_contrib_historico or salario_atual
    cenarios = []

    def _add(regra, anos_esp):
        a_apos = idade + anos_esp
        c_apos = anos_contrib + anos_esp
        ben = _beneficio(sal, c_apos, sexo)
        cenarios.append({
            "regra": regra,
            "anos_restantes": round(anos_esp, 1),
            "idade_aposentadoria": round(a_apos, 1),
            "contribuicoes_totais": round(c_apos, 1),
            "beneficio_estimado": round(ben, 2),
        })

    # --- Regras permanentes ---
    # Por tempo
    falta_c = max(0, CONTRIB_TEMPO[sexo] - anos_contrib)
    falta_i = max(0, IDADE_TEMPO[sexo] - idade)
    _add(f"Permanente — Por Tempo ({CONTRIB_TEMPO[sexo]} anos + {IDADE_TEMPO[sexo]} anos)", max(falta_c, falta_i))

    # Por idade
    falta_c2 = max(0, CONTRIB_IDADE[sexo] - anos_contrib)
    falta_i2 = max(0, IDADE_IDADE[sexo] - idade)
    _add(f"Permanente — Por Idade ({IDADE_IDADE[sexo]} anos + {CONTRIB_IDADE[sexo]} anos contrib.)", max(falta_c2, falta_i2))

    # --- Regras de transição (quem contribuía antes de nov/2019) ---
    if pre_reforma:
        # Pontos
        pontos_atuais = idade + anos_contrib
        pontos_alvo = PONTOS_2026[sexo]
        contrib_min = CONTRIB_TEMPO[sexo]
        if anos_contrib >= contrib_min:
            falta_p = max(0, pontos_alvo - pontos_atuais)
            _add(f"Transição — Pontos ({pontos_alvo} pts em 2026)", falta_p)
        else:
            falta_p = max(0, contrib_min - anos_contrib)
            _add(f"Transição — Pontos (falta {falta_p:.0f} anos de contribuição mín.)", falta_p)

        # Idade progressiva
        idade_prog = {"M": 64, "F": 59}[sexo]
        falta_ip = max(max(0, contrib_min - anos_contrib), max(0, idade_prog - idade))
        _add(f"Transição — Idade Progressiva ({idade_prog} anos em 2026 + {contrib_min} anos contrib.)", falta_ip)

    return sorted(cenarios, key=lambda x: x["anos_restantes"])


def calcular_contribuicao_mensal(
    salario: float,
    plano: str,
    anos_faltando: float,
) -> dict:
    """Quanto vai pagar por mês e no total em cada plano."""
    sal_contrib = max(SALARIO_MIN, min(salario, TETO_INSS))

    if plano == "mei":
        mensal = SALARIO_MIN * 0.05 + 6.0  # INSS + ISS estimado
        obs = "Valor fixo MEI (DAS inclui INSS 5%)"
    elif plano == "simplificado":
        mensal = sal_contrib * 0.11
        obs = "11% — aposenta apenas por idade"
    else:
        mensal = sal_contrib * 0.20
        obs = "20% — todos os benefícios (inclusive por tempo)"

    total = mensal * 12 * anos_faltando
    return {
        "plano": plano,
        "contribuicao_mensal": round(mensal, 2),
        "total_periodo": round(total, 2),
        "observacao": obs,
    }


def pgbl_analise(
    renda_anual: float,
    aliquota_irpf: float,
    aporte_anual: float,
    anos_acumulacao: int,
    rentabilidade_aa: float = 0.07,
) -> dict:
    """
    Compara PGBL (deduz no IR agora, tributa no resgate) vs.
    aplicação sem dedução (CDB/Tesouro equivalente).
    """
    limite_pgbl = renda_anual * 0.12
    aporte_efetivo = min(aporte_anual, limite_pgbl)
    economia_ir_anual = aporte_efetivo * aliquota_irpf

    # Montante PGBL após acumulação (juros compostos)
    montante_pgbl = aporte_efetivo * (((1 + rentabilidade_aa) ** anos_acumulacao - 1) / rentabilidade_aa)
    # Tributo no resgate (tabela progressiva regressiva — assume alíquota menor na apos.)
    aliquota_resgate = max(0.10, aliquota_irpf - 0.10)
    pgbl_liquido = montante_pgbl * (1 - aliquota_resgate)

    # Aplicação sem PGBL (sem dedução, sem tributação no resgate para LCI/LCA)
    montante_sem = aporte_efetivo * (((1 + rentabilidade_aa) ** anos_acumulacao - 1) / rentabilidade_aa)
    sem_pgbl_liquido = montante_sem  # isento (LCI/LCA) como referência

    return {
        "aporte_anual_efetivo": round(aporte_efetivo, 2),
        "limite_12pct_renda": round(limite_pgbl, 2),
        "economia_ir_anual": round(economia_ir_anual, 2),
        "economia_ir_total": round(economia_ir_anual * anos_acumulacao, 2),
        "montante_bruto_pgbl": round(montante_pgbl, 2),
        "montante_liquido_pgbl": round(pgbl_liquido, 2),
        "montante_referencia_sem_pgbl": round(sem_pgbl_liquido, 2),
        "vantagem_pgbl": round(pgbl_liquido - sem_pgbl_liquido + economia_ir_anual * anos_acumulacao, 2),
        "anos_acumulacao": anos_acumulacao,
        "rentabilidade_aa_pct": rentabilidade_aa * 100,
    }


def main():
    parser = argparse.ArgumentParser(
        description=f"Planejamento Previdenciário INSS 2026 | {__author__} | {__source__}"
    )
    parser.add_argument("--idade",       type=int,   required=True, help="Idade atual")
    parser.add_argument("--contribuicoes", type=float, required=True,
                        help="Anos de contribuição ao INSS (pode ser decimal, ex: 12.5)")
    parser.add_argument("--salario",     type=float, required=True,
                        help="Salário atual de contribuição (R$)")
    parser.add_argument("--sexo",        choices=["M","F"], required=True)
    parser.add_argument("--pre-reforma", action="store_true",
                        help="Contribuía antes de nov/2019 (habilita transições)")
    parser.add_argument("--plano",       choices=["mei","simplificado","pleno"],
                        default="pleno",
                        help="Plano de contribuição atual/futuro (padrão: pleno)")
    parser.add_argument("--renda-anual", type=float, default=0,
                        help="Renda anual tributável (R$) — para análise PGBL")
    parser.add_argument("--aliquota-ir", type=float, default=0.275,
                        help="Alíquota IRPF atual (padrão: 27.5%%)")
    parser.add_argument("--aporte-pgbl", type=float, default=0,
                        help="Aporte anual em PGBL (R$) — ativa análise PGBL")
    args = parser.parse_args()

    w = 68
    print(f"\n{'='*w}")
    print(f"  PLANEJAMENTO PREVIDENCIÁRIO — INSS 2026")
    print(f"{'='*w}")
    print(f"  Idade: {args.idade} anos  |  Contribuição: {args.contribuicoes} anos"
          f"  |  Sexo: {'Masculino' if args.sexo == 'M' else 'Feminino'}")
    print(f"  Salário: R$ {args.salario:,.2f}"
          f"  |  Plano: {args.plano}"
          f"  |  Pré-reforma: {'Sim' if args.pre_reforma else 'Não'}")

    # Cenários de aposentadoria
    cenarios = calcular_cenarios(
        args.idade, args.contribuicoes, args.salario,
        args.sexo, args.pre_reforma
    )

    print(f"\n  📋 CENÁRIOS DE APOSENTADORIA (do mais rápido ao mais demorado)")
    print(f"  {'─'*66}")
    for i, c in enumerate(cenarios, 1):
        status = "✅ ELEGÍVEL AGORA" if c["anos_restantes"] == 0 else f"⏳ {c['anos_restantes']:.1f} anos ({ANO_ATUAL + int(c['anos_restantes'])})"
        print(f"\n  {i}. {c['regra']}")
        print(f"     {status}")
        print(f"     Idade na aposentadoria: {c['idade_aposentadoria']:.0f} anos"
              f"  |  Contribuições totais: {c['contribuicoes_totais']:.0f} anos")
        print(f"     Benefício estimado: R$ {c['beneficio_estimado']:,.2f}/mês")

    # Melhor cenário
    melhor = cenarios[0]
    print(f"\n  {'='*66}")
    print(f"  🏆 ESTRATÉGIA MAIS RÁPIDA: {melhor['regra']}")
    print(f"     Faltam: {melhor['anos_restantes']:.1f} anos  |  Benefício est.: R$ {melhor['beneficio_estimado']:,.2f}/mês")

    # Custo de contribuição até lá
    if melhor["anos_restantes"] > 0:
        custo = calcular_contribuicao_mensal(args.salario, args.plano, melhor["anos_restantes"])
        print(f"\n  💰 CUSTO PARA CHEGAR LÁ (plano {args.plano}):")
        print(f"     Contribuição mensal: R$ {custo['contribuicao_mensal']:,.2f}")
        print(f"     Total no período:    R$ {custo['total_periodo']:,.2f}")
        print(f"     Obs: {custo['observacao']}")

        # ROI da contribuição vs. benefício
        if custo["total_periodo"] > 0 and melhor["beneficio_estimado"] > 0:
            meses_payback = custo["total_periodo"] / melhor["beneficio_estimado"]
            print(f"     Payback estimado:    {meses_payback:.0f} meses ({meses_payback/12:.1f} anos) após aposentadoria")

    # Comparativo de planos
    if args.pre_reforma or melhor["anos_restantes"] > 0:
        print(f"\n  📊 COMPARATIVO DE PLANOS DE CONTRIBUIÇÃO:")
        print(f"  {'Plano':<20} {'Mensal':>10}  {'Total período':>14}  Obs")
        print(f"  {'─'*64}")
        for plano in ["mei", "simplificado", "pleno"]:
            c = calcular_contribuicao_mensal(args.salario, plano, max(melhor["anos_restantes"], 1))
            print(f"  {plano:<20} R$ {c['contribuicao_mensal']:>8,.2f}  R$ {c['total_periodo']:>12,.2f}  {c['observacao'][:30]}")

    # Análise PGBL
    if args.aporte_pgbl > 0 and args.renda_anual > 0:
        anos_restantes = max(1, int(melhor["anos_restantes"]))
        pgbl = pgbl_analise(
            args.renda_anual, args.aliquota_ir,
            args.aporte_pgbl, anos_restantes
        )
        print(f"\n  📈 ANÁLISE PGBL:")
        print(f"  {'─'*64}")
        print(f"  Aporte anual efetivo:        R$ {pgbl['aporte_anual_efetivo']:>10,.2f}")
        print(f"  Limite 12% da renda:         R$ {pgbl['limite_12pct_renda']:>10,.2f}")
        print(f"  Economia IR anual:           R$ {pgbl['economia_ir_anual']:>10,.2f}")
        print(f"  Economia IR total ({anos_restantes} anos):  R$ {pgbl['economia_ir_total']:>10,.2f}")
        print(f"  Montante bruto no resgate:   R$ {pgbl['montante_bruto_pgbl']:>10,.2f}")
        print(f"  Montante líquido (PGBL):     R$ {pgbl['montante_liquido_pgbl']:>10,.2f}")
        print(f"  Referência sem PGBL (LCI):   R$ {pgbl['montante_referencia_sem_pgbl']:>10,.2f}")
        vant = pgbl["vantagem_pgbl"]
        sinal = "✅ VANTAJOSO" if vant > 0 else "⚠️  DESVANTAGEM"
        print(f"  {sinal}: diferença de R$ {abs(vant):,.2f} a favor do {'PGBL' if vant > 0 else 'LCI/LCA'}")
        print(f"  (Rentabilidade {pgbl['rentabilidade_aa_pct']:.0f}% a.a., alíquota resgate estimada {max(0.10, args.aliquota_ir - 0.10)*100:.0f}%)")

    print(f"\n{'='*w}")
    print("\n⚠️  Projeções educativas. Consulte advogado previdenciarista para planejamento real.")
    print("    O INSS calcula com base em TODOS os salários de contribuição desde julho/1994.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
