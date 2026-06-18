---
name: trabalhista-brasil
description: >
  Use para CLT, cálculo de salário líquido, rescisão, férias, FGTS, horas extras,
  CLT vs PJ, aposentadoria, INSS, processos trabalhistas, orientação sobre provas
  e direitos. Ativa em "calcular salário", "rescisão", "CLT ou PJ", "quanto ganho
  por hora", "INSS", "aposentadoria", "processo trabalhista", "horas extras".
tags: [clt, trabalhista, rescisao, salario, inss, aposentadoria, processo-trabalhista]
---

# 👷 Trabalhista — CLT, Salário e Aposentadoria

> ⚠️ Orientação educativa. Para processos trabalhistas, consulte advogado habilitado na OAB.
> Referência: [CLT completa](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm)

---

## Calculadoras disponíveis

### 1. Calculadora de Salário Líquido
Dado o salário bruto, calcula descontos e valor líquido:

**Descontos obrigatórios:**
- **INSS** (tabela progressiva 2026):
  | Faixa salarial | Alíquota |
  |---------------|---------|
  | Até R$ 1.518,00 | 7,5% |
  | R$ 1.518,01 a R$ 2.793,88 | 9% |
  | R$ 2.793,89 a R$ 4.190,83 | 12% |
  | R$ 4.190,84 a R$ 8.157,41 | 14% |

- **IRRF** (tabela progressiva mensal 2026)
- Vale-transporte: desconto máximo de 6% do salário
- Vale-refeição: conforme convenção coletiva

```bash
python3 scripts/salario_liquido.py --bruto 5000 --dependentes 1
```

### 2. Calculadora de Valor por Hora
```
Salário mensal ÷ (dias úteis × horas/dia)
Exemplo: R$ 4.500 ÷ (22 × 8) = R$ 25,57/hora
```

Horas extras:
- Dias úteis: + 50% (mínimo)
- Finais de semana/feriados: + 100% (mínimo, conforme CCT)
- Noturno (22h–5h): + 20% adicional

### 3. Calculadora de Rescisão
Tipos e verbas devidas:

| Tipo | Aviso | Multa FGTS | 13° prop. | Férias prop. |
|------|-------|-----------|-----------|-------------|
| Sem justa causa | ✅ | 40% | ✅ | ✅ + 1/3 |
| Justa causa | ❌ | ❌ | ❌ | ❌ |
| Pedido de demissão | ✅ | ❌ | ✅ | ✅ + 1/3 |
| Acordo mútuo (484-A) | 50% | 20% | ✅ | ✅ + 1/3 |

```bash
python3 scripts/rescisao_calculator.py --salario 4500 --meses 36 --tipo sem_justa_causa --fgts 15000
```

### 4. CLT vs PJ — Qual compensa mais?
Perguntar ao usuário:
- Qual o valor ofertado como CLT? E como PJ?
- Tem dependentes? (impacta plano de saúde)
- A empresa oferece benefícios (VT, VR, plano, etc.)?
- Tem estabilidade no contrato PJ?

**Fórmula geral CLT → PJ equivalente:**
```
Salário PJ necessário = Salário CLT × 1,35 a 1,50
(para compensar FGTS, 13°, férias, INSS e benefícios)
```

```bash
python3 scripts/clt_vs_pj.py --clt 8000 --beneficios 1500 --pj 12000
```

### 5. Calculadora de INSS
```bash
python3 scripts/inss_calculator.py --salario 5000
```

### 6. Estimativa de Aposentadoria
```bash
python3 scripts/aposentadoria_estimativa.py --idade 35 --contribuicoes 13 --salario_medio 5000
```

---

## Regras de Aposentadoria 2026

### Modalidades principais (Reforma de 2019)

| Modalidade | Mulheres | Homens |
|------------|----------|--------|
| Por idade | 60 anos + 15 anos contribuição | 65 anos + 15 anos contribuição |
| Por tempo | 57 anos + 30 anos contribuição | 62 anos + 35 anos contribuição |
| Especial | 55–60 anos (exposição a agentes nocivos) | — |

**Mínimo de contribuições:** 180 meses (15 anos) para aposentadoria por idade

### Regras de Transição 2026 (para quem contribuía antes de nov/2019)

**Regra de Pontos:**
- Mulheres: 93 pontos em 2026 (soma idade + anos de contribuição)
- Homens: 103 pontos em 2026
- Meta final: 100 pontos (mulheres) e 105 pontos (homens)

**Regra de Idade Progressiva:**
- Mulheres: 59 anos em 2026 (meta: 62)
- Homens: 64 anos em 2026 (meta: 65)

**Regra do Pedágio:**
- Precisa cumprir 50% ou 100% do tempo que faltava em nov/2019
- Sem limite mínimo de idade

### Cálculo do benefício
- Média dos 100% dos salários de contribuição desde julho/1994
- Valor integral: 60% + 2% por ano acima de 20 anos (homens) ou 15 anos (mulheres)

---

## Processo Trabalhista — Orientação

Ao usuário relatar uma situação trabalhista, perguntar:

1. **O que aconteceu?** (demissão indevida, assédio, horas não pagas, etc.)
2. **Quais provas você tem?**
   - Holerites, contracheques
   - Mensagens (WhatsApp, e-mail)
   - Testemunhas
   - Cartão ponto
   - Contratos e aditivos
   - Fotos/vídeos (se aplicável)
3. **Quanto tempo desde o ocorrido?**
   - Prazo prescricional: **2 anos** após demissão para reclamar
   - Atos dentro do emprego: prescrição de **5 anos** retroativos

**Orientação sobre provas:**
- Mensagens de WhatsApp são válidas como prova (TST admite)
- E-mails corporativos são válidas
- Testemunhas: peso importante no processo
- Prints de conversas: salvar com data visível
- Documentar tudo em papel se possível (assédio moral, etc.)

**Fórum competente:**
- Vara do Trabalho da cidade onde o serviço era prestado
- Justiça do Trabalho é gratuita para trabalhador hipossuficiente

> ⚠️ Sempre recomende consulta a advogado trabalhista antes de entrar com ação.

---

## Principais Direitos CLT

| Direito | Referência |
|---------|-----------|
| Salário mínimo | R$ 1.518,00 (2026) — Art. 76 CLT |
| Férias 30 dias + 1/3 | Art. 129 CLT |
| 13° salário | Lei 4.090/62 |
| FGTS 8% | Lei 8.036/90 |
| Aviso prévio proporcional | Lei 12.506/11 |
| Hora extra +50% | Art. 59 CLT |
| Adicional noturno +20% | Art. 73 CLT |
| Intervalo intrajornada | Art. 71 CLT |
| Licença maternidade 120 dias | Art. 392 CLT |
| Licença paternidade 5 dias | Art. 10 ADCT |
