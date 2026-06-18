#!/usr/bin/env python3
"""
Calculadora de IRPF 2026 — Tabela Progressiva
Autor: AlissonSantos1
"""
import argparse


# Tabela progressiva IRPF 2026 (anual)
TABELA_PROGRESSIVA = [
    (27_108.00, 0.0, 0.0),
    (33_919.80, 0.075, 2_033.10),
    (45_012.60, 0.15, 4_576.95),
    (55_976.16, 0.225, 7_953.46),
    (float("inf"), 0.275, 10_750.00),
]

DEDUCAO_DEPENDENTE = 2_275.08
DEDUCAO_SIMPLIFICADO_PERC = 0.20
LIMITE_SIMPLIFICADO = 16_754.34


def calcular_imposto_anual(renda_bruta: float, dependentes: int = 0,
                            deducoes_saude: float = 0, deducoes_educacao: float = 0,
                            inss: float = 0, previdencia_privada: float = 0) -> dict:
    """Calcula IRPF pelo modelo completo."""
    limite_educacao = 3_561.50 * (1 + dependentes)
    educacao_dedutivel = min(deducoes_educacao, limite_educacao)

    deducao_dependentes = dependentes * DEDUCAO_DEPENDENTE
    total_deducoes_completo = (
        inss + previdencia_privada + deducao_dependentes +
        deducoes_saude + educacao_dedutivel
    )

    # Modelo completo
    base_completo = max(0, renda_bruta - total_deducoes_completo)
    imposto_completo = _calcular_imposto_tabela(base_completo)

    # Modelo simplificado
    deducao_simplificado = min(renda_bruta * DEDUCAO_SIMPLIFICADO_PERC, LIMITE_SIMPLIFICADO)
    base_simplificado = max(0, renda_bruta - deducao_simplificado)
    imposto_simplificado = _calcular_imposto_tabela(base_simplificado)

    melhor = "completo" if imposto_completo <= imposto_simplificado else "simplificado"

    return {
        "renda_bruta": renda_bruta,
        "modelo_completo": {
            "deducoes_totais": total_deducoes_completo,
            "base_calculo": base_completo,
            "imposto_devido": imposto_completo,
        },
        "modelo_simplificado": {
            "deducao_padrao": deducao_simplificado,
            "base_calculo": base_simplificado,
            "imposto_devido": imposto_simplificado,
        },
        "melhor_modelo": melhor,
        "economia": abs(imposto_completo - imposto_simplificado),
    }


def _calcular_imposto_tabela(base: float) -> float:
    """Aplica tabela progressiva."""
    for limite, aliquota, deducao in TABELA_PROGRESSIVA:
        if base <= limite:
            return max(0, base * aliquota - deducao)
    return 0.0


def main():
    parser = argparse.ArgumentParser(description="Calculadora IRPF 2026")
    parser.add_argument("--renda", type=float, required=True, help="Renda bruta anual (R$)")
    parser.add_argument("--dependentes", type=int, default=0, help="Número de dependentes")
    parser.add_argument("--saude", type=float, default=0, help="Despesas médicas (R$)")
    parser.add_argument("--educacao", type=float, default=0, help="Despesas com educação (R$)")
    parser.add_argument("--inss", type=float, default=0, help="INSS pago (R$)")
    parser.add_argument("--previdencia", type=float, default=0, help="Previdência privada PGBL (R$)")
    args = parser.parse_args()

    resultado = calcular_imposto_anual(
        args.renda, args.dependentes, args.saude,
        args.educacao, args.inss, args.previdencia
    )

    print("\n" + "=" * 50)
    print("  CÁLCULO IRPF 2026 — TABELA PROGRESSIVA")
    print("=" * 50)
    print(f"  Renda bruta anual: R$ {resultado['renda_bruta']:,.2f}")
    print()
    print("  📋 MODELO COMPLETO")
    m = resultado["modelo_completo"]
    print(f"    Deduções totais:  R$ {m['deducoes_totais']:,.2f}")
    print(f"    Base de cálculo: R$ {m['base_calculo']:,.2f}")
    print(f"    Imposto devido:  R$ {m['imposto_devido']:,.2f}")
    print()
    print("  📋 MODELO SIMPLIFICADO")
    s = resultado["modelo_simplificado"]
    print(f"    Dedução padrão:  R$ {s['deducao_padrao']:,.2f}")
    print(f"    Base de cálculo: R$ {s['base_calculo']:,.2f}")
    print(f"    Imposto devido:  R$ {s['imposto_devido']:,.2f}")
    print()
    print(f"  ✅ MELHOR MODELO: {resultado['melhor_modelo'].upper()}")
    print(f"  💰 Economia: R$ {resultado['economia']:,.2f}")
    print("=" * 50)
    print("\n⚠️  Consulte um contador para sua situação específica.")


if __name__ == "__main__":
    main()
