#!/usr/bin/env python3
"""
Calculadora de Rescisão Trabalhista — CLT
Autor: AlissonSantos1
"""
import argparse


TIPOS_RESCISAO = {
    "sem_justa_causa": {"aviso": True, "multa_fgts": 0.40, "13_prop": True, "ferias_prop": True},
    "justa_causa": {"aviso": False, "multa_fgts": 0.0, "13_prop": False, "ferias_prop": False},
    "pedido_demissao": {"aviso": True, "multa_fgts": 0.0, "13_prop": True, "ferias_prop": True},
    "acordo_mutuo": {"aviso": True, "multa_fgts": 0.20, "13_prop": True, "ferias_prop": True},
}


def calcular_aviso_previo(anos: int) -> int:
    """Calcula dias de aviso prévio (30 + 3 por ano, máx 90)."""
    return min(30 + (anos * 3), 90)


def calcular_rescisao(salario: float, meses_trabalhados: int, tipo: str,
                       saldo_fgts: float = 0, ferias_vencidas: bool = False) -> dict:
    anos = meses_trabalhados // 12
    meses_restantes = meses_trabalhados % 12
    reg = TIPOS_RESCISAO.get(tipo, TIPOS_RESCISAO["sem_justa_causa"])

    dias_aviso = calcular_aviso_previo(anos) if reg["aviso"] else 0
    valor_aviso = (salario / 30) * dias_aviso if reg["aviso"] else 0

    valor_13 = (salario / 12) * meses_restantes if reg["13_prop"] and meses_restantes > 0 else 0

    valor_ferias_prop = ((salario / 12) * meses_restantes) * (4/3) if reg["ferias_prop"] and meses_restantes > 0 else 0
    valor_ferias_venc = salario * (4/3) if ferias_vencidas else 0

    multa = saldo_fgts * reg["multa_fgts"]

    total = valor_aviso + valor_13 + valor_ferias_prop + valor_ferias_venc + multa

    return {
        "tipo": tipo,
        "salario": salario,
        "meses_trabalhados": meses_trabalhados,
        "anos": anos,
        "aviso_previo_dias": dias_aviso,
        "aviso_previo_valor": valor_aviso,
        "decimo_terceiro_proporcional": valor_13,
        "ferias_proporcionais": valor_ferias_prop,
        "ferias_vencidas": valor_ferias_venc,
        "multa_fgts": multa,
        "total_bruto": total,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculadora de Rescisão CLT")
    parser.add_argument("--salario", type=float, required=True, help="Salário mensal (R$)")
    parser.add_argument("--meses", type=int, required=True, help="Meses trabalhados")
    parser.add_argument("--tipo", choices=list(TIPOS_RESCISAO.keys()),
                        default="sem_justa_causa", help="Tipo de rescisão")
    parser.add_argument("--fgts", type=float, default=0, help="Saldo FGTS acumulado (R$)")
    parser.add_argument("--ferias-vencidas", action="store_true", help="Tem férias vencidas?")
    args = parser.parse_args()

    r = calcular_rescisao(args.salario, args.meses, args.tipo, args.fgts, args.ferias_vencidas)

    nomes = {
        "sem_justa_causa": "Demissão sem Justa Causa",
        "justa_causa": "Demissão com Justa Causa",
        "pedido_demissao": "Pedido de Demissão",
        "acordo_mutuo": "Acordo Mútuo (art. 484-A CLT)",
    }

    print("\n" + "=" * 55)
    print(f"  RESCISÃO — {nomes.get(r['tipo'], r['tipo']).upper()}")
    print("=" * 55)
    print(f"  Salário:              R$ {r['salario']:>10,.2f}")
    print(f"  Tempo de serviço:     {r['anos']} anos e {r['meses_trabalhados'] % 12} meses")
    print()
    print("  VERBAS RESCISÓRIAS:")
    if r["aviso_previo_valor"] > 0:
        print(f"  Aviso prévio ({r['aviso_previo_dias']}d): R$ {r['aviso_previo_valor']:>10,.2f}")
    if r["decimo_terceiro_proporcional"] > 0:
        print(f"  13° proporcional:     R$ {r['decimo_terceiro_proporcional']:>10,.2f}")
    if r["ferias_proporcionais"] > 0:
        print(f"  Férias prop. + 1/3:   R$ {r['ferias_proporcionais']:>10,.2f}")
    if r["ferias_vencidas"] > 0:
        print(f"  Férias vencidas+1/3:  R$ {r['ferias_vencidas']:>10,.2f}")
    if r["multa_fgts"] > 0:
        print(f"  Multa FGTS:           R$ {r['multa_fgts']:>10,.2f}")
    print("  " + "-" * 40)
    print(f"  TOTAL BRUTO:          R$ {r['total_bruto']:>10,.2f}")
    print("=" * 55)
    print("\n⚠️  Valor bruto. Sujeito a descontos de INSS e IR.")
    print("    Consulte um advogado trabalhista para sua situação.")


if __name__ == "__main__":
    main()
