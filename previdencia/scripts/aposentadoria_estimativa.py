#!/usr/bin/env python3
"""
Estimativa de Aposentadoria INSS 2026 — Regras de Transição e Permanentes
Autor: Alisson Santos — github.com/AlissonSantos1/brasil-legal-skills
Copyright (c) 2026 Alisson Santos. Licença MIT.
"""
__author__ = "Alisson Santos"
__copyright__ = "Copyright (c) 2026 Alisson Santos"
__license__ = "MIT"
__source__ = "https://github.com/AlissonSantos1/brasil-legal-skills"

import argparse

ANO_REFORMA   = 2019   # nov/2019 — EC 103/2019
ANO_ATUAL     = 2026
TETO_INSS     = 8_157.41
SALARIO_MIN   = 1_518.00

# Pontos de transição 2026 (somam +1/ano até o teto)
PONTOS_2026   = {"M": 103, "F": 93}
PONTOS_TETO   = {"M": 105, "F": 100}

# Idade mínima progressiva 2026
IDADE_PROG_2026 = {"M": 64, "F": 59}
IDADE_PROG_TETO = {"M": 65, "F": 62}

# Tempo mínimo de contribuição
CONTRIB_MIN_TEMPO = {"M": 35, "F": 30}
CONTRIB_MIN_IDADE = {"M": 15, "F": 15}

# Idade mínima permanente (pós-reforma)
IDADE_PERM    = {"M": 65, "F": 62}


def estimar_beneficio(salario_medio: float, anos_contrib_na_apos: int, sexo: str) -> dict:
    """Estima o valor da aposentadoria com base no salário médio e contribuições."""
    base = min(salario_medio, TETO_INSS)
    anos_acima = max(0, anos_contrib_na_apos - (20 if sexo == "M" else 15))
    taxa = min(0.60 + anos_acima * 0.02, 1.0)
    beneficio = base * taxa
    return {
        "salario_medio": salario_medio,
        "base_calculo": base,
        "anos_contrib_apos": anos_contrib_na_apos,
        "taxa_pct": taxa * 100,
        "beneficio_estimado": beneficio,
    }


def regras_transicao(idade: int, anos_contrib: int, sexo: str, salario_medio: float) -> list:
    """Calcula as 4 regras de transição para quem contribuía antes de nov/2019."""
    resultados = []
    anos_restantes_2019 = max(0, CONTRIB_MIN_TEMPO[sexo] - anos_contrib)
    anos_contrib_2019 = anos_contrib - max(0, ANO_ATUAL - ANO_REFORMA)

    # --- Regra 1: Pontos ---
    pontos_atuais = idade + anos_contrib
    pontos_necessarios = PONTOS_2026[sexo]
    contrib_minima = CONTRIB_MIN_TEMPO[sexo]
    if anos_contrib >= contrib_minima:
        falta_pontos = max(0, pontos_necessarios - pontos_atuais)
        ano_elegivel = ANO_ATUAL + falta_pontos  # cada ano ganha 1 ponto e +1 no teto
        anos_espera = max(0, ano_elegivel - ANO_ATUAL)
        anos_contrib_apos = anos_contrib + anos_espera
        ben = estimar_beneficio(salario_medio, anos_contrib_apos, sexo)
        resultados.append({
            "regra": "Regra de Pontos",
            "desc": f"{PONTOS_2026[sexo]} pontos em 2026 (idade + contribuição)",
            "elegivel_agora": falta_pontos == 0,
            "pontos_atuais": pontos_atuais,
            "pontos_necessarios": pontos_necessarios,
            "anos_restantes": anos_espera,
            "ano_estimado": ano_elegivel,
            "beneficio": ben,
        })
    else:
        falta_contrib = contrib_minima - anos_contrib
        resultados.append({
            "regra": "Regra de Pontos",
            "desc": f"Exige {contrib_minima} anos de contribuição (faltam {falta_contrib} anos)",
            "elegivel_agora": False,
            "anos_restantes": falta_contrib,
            "ano_estimado": ANO_ATUAL + falta_contrib,
            "beneficio": estimar_beneficio(salario_medio, anos_contrib + falta_contrib, sexo),
        })

    # --- Regra 2: Idade Progressiva ---
    idade_necessaria = IDADE_PROG_2026[sexo]
    contrib_min_r2 = CONTRIB_MIN_TEMPO[sexo]
    falta_contrib_r2 = max(0, contrib_min_r2 - anos_contrib)
    falta_idade_r2 = max(0, idade_necessaria - idade)
    anos_espera_r2 = max(falta_contrib_r2, falta_idade_r2)
    resultados.append({
        "regra": "Idade Progressiva",
        "desc": f"{idade_necessaria} anos em 2026 + {contrib_min_r2} anos contrib. (mín.)",
        "elegivel_agora": falta_idade_r2 == 0 and falta_contrib_r2 == 0,
        "anos_restantes": anos_espera_r2,
        "ano_estimado": ANO_ATUAL + anos_espera_r2,
        "beneficio": estimar_beneficio(salario_medio, anos_contrib + anos_espera_r2, sexo),
    })

    # --- Regra 3: Pedágio 50% (para quem faltava ≤ 2 anos em nov/2019) ---
    if 0 < anos_restantes_2019 <= 2:
        pedagio = anos_restantes_2019 * 0.5
        anos_espera_r3 = anos_restantes_2019 + pedagio
        resultados.append({
            "regra": "Pedágio de 50%",
            "desc": f"Faltavam ≤2 anos em nov/2019 — cumprir 50% extra do período restante",
            "elegivel_agora": False,
            "anos_restantes": anos_espera_r3,
            "ano_estimado": ANO_ATUAL + anos_espera_r3,
            "beneficio": estimar_beneficio(salario_medio, anos_contrib + anos_espera_r3, sexo),
        })

    # --- Regra 4: Pedágio 100% ---
    if anos_restantes_2019 > 2:
        pedagio_100 = anos_restantes_2019
        idade_min_r4 = 57 if sexo == "F" else 60
        anos_contrib_espera = anos_restantes_2019 * 2
        falta_idade_r4 = max(0, idade_min_r4 - (idade + anos_contrib_espera))
        anos_espera_r4 = anos_contrib_espera + falta_idade_r4
        resultados.append({
            "regra": "Pedágio de 100%",
            "desc": f"Cumprir 100% do tempo restante + idade mín. {idade_min_r4} anos",
            "elegivel_agora": False,
            "anos_restantes": anos_espera_r4,
            "ano_estimado": ANO_ATUAL + anos_espera_r4,
            "beneficio": estimar_beneficio(salario_medio, anos_contrib + anos_espera_r4, sexo),
        })

    return resultados


def regra_permanente(idade: int, anos_contrib: int, sexo: str, salario_medio: float) -> list:
    """Regras permanentes para quem entrou após nov/2019 ou como alternativa."""
    resultados = []

    # Por idade
    falta_idade = max(0, IDADE_PERM[sexo] - idade)
    falta_contrib = max(0, CONTRIB_MIN_IDADE[sexo] - anos_contrib)
    espera = max(falta_idade, falta_contrib)
    resultados.append({
        "regra": "Aposentadoria por Idade",
        "desc": f"{IDADE_PERM[sexo]} anos + {CONTRIB_MIN_IDADE[sexo]} anos de contribuição",
        "elegivel_agora": espera == 0,
        "anos_restantes": espera,
        "ano_estimado": ANO_ATUAL + espera,
        "beneficio": estimar_beneficio(salario_medio, anos_contrib + espera, sexo),
    })

    # Por tempo
    falta_contrib_t = max(0, CONTRIB_MIN_TEMPO[sexo] - anos_contrib)
    falta_idade_t = max(0, (62 if sexo == "M" else 57) - idade)
    espera_t = max(falta_contrib_t, falta_idade_t)
    resultados.append({
        "regra": "Aposentadoria por Tempo",
        "desc": f"{CONTRIB_MIN_TEMPO[sexo]} anos contrib. + {62 if sexo == 'M' else 57} anos de idade",
        "elegivel_agora": espera_t == 0,
        "anos_restantes": espera_t,
        "ano_estimado": ANO_ATUAL + espera_t,
        "beneficio": estimar_beneficio(salario_medio, anos_contrib + espera_t, sexo),
    })

    return resultados


def main():
    parser = argparse.ArgumentParser(
        description=f"Estimativa de Aposentadoria INSS 2026 | {__author__} | {__source__}"
    )
    parser.add_argument("--idade", type=int, required=True,
                        help="Idade atual (anos)")
    parser.add_argument("--contribuicoes", type=int, required=True,
                        help="Anos de contribuição ao INSS já realizados")
    parser.add_argument("--salario-medio", type=float, required=True,
                        help="Salário médio de contribuição (R$) — estimativa do benefício")
    parser.add_argument("--sexo", choices=["M", "F"], required=True,
                        help="Sexo: M (masculino) ou F (feminino)")
    parser.add_argument("--pre-reforma", action="store_true",
                        help="Contribuía antes de nov/2019? (habilita regras de transição)")
    args = parser.parse_args()

    w = 70
    print("\n" + "=" * w)
    print("  ESTIMATIVA DE APOSENTADORIA — INSS 2026")
    print("=" * w)
    print(f"  Dados informados:")
    print(f"  Idade: {args.idade} anos  |  Contribuição: {args.contribuicoes} anos"
          f"  |  Sexo: {'Masculino' if args.sexo == 'M' else 'Feminino'}")
    print(f"  Salário médio de contribuição: R$ {args.salario_medio:,.2f}")
    print(f"  Pontuação atual: {args.idade + args.contribuicoes} pontos (idade + anos contrib.)")
    print()

    if args.pre_reforma:
        print("  📋 REGRAS DE TRANSIÇÃO (contribuía antes de nov/2019)")
        print("  " + "─" * (w - 2))
        regras = regras_transicao(args.idade, args.contribuicoes, args.sexo, args.salario_medio)
    else:
        print("  📋 REGRAS PERMANENTES (entrou após nov/2019)")
        print("  " + "─" * (w - 2))
        regras = regra_permanente(args.idade, args.contribuicoes, args.sexo, args.salario_medio)

    melhor = None
    for r in regras:
        status = "✅ ELEGÍVEL AGORA" if r["elegivel_agora"] else f"⏳ Faltam ~{r['anos_restantes']:.1f} anos (est. {r['ano_estimado']:.0f})"
        print(f"\n  🔹 {r['regra']}")
        print(f"     {r['desc']}")
        print(f"     Status: {status}")
        b = r["beneficio"]
        print(f"     Benefício estimado: R$ {b['beneficio_estimado']:,.2f}/mês ({b['taxa_pct']:.0f}% do salário de benefício)")
        if melhor is None or r["anos_restantes"] < melhor["anos_restantes"]:
            melhor = r

    if melhor:
        print()
        print("  " + "=" * (w - 2))
        print(f"  🏆 REGRA MAIS VANTAJOSA: {melhor['regra']}")
        b = melhor["beneficio"]
        print(f"     Aposentadoria estimada em: {melhor['ano_estimado']:.0f}")
        print(f"     Benefício estimado:         R$ {b['beneficio_estimado']:,.2f}/mês")
        if args.salario_medio > TETO_INSS:
            print(f"     ⚠️  Teto INSS: R$ {TETO_INSS:,.2f}/mês — valores acima não contam para o benefício")

    print("\n" + "=" * w)
    print("\n⚠️  Estimativa educativa. O INSS calcula com base em TODOS os salários desde 07/1994.")
    print("    Para planejamento personalizado, consulte advogado previdenciarista.")
    print(f"\n  brasil-legal-skills · {__author__} · {__source__}")


if __name__ == "__main__":
    main()
