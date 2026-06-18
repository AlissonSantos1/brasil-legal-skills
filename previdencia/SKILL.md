---
name: previdencia-brasil
description: >
  Use para INSS, aposentadoria, benefícios previdenciários, cálculo de contribuição,
  regras de transição 2026, auxílio-doença, salário-maternidade, pensão por morte.
  Ativa em "aposentadoria", "INSS", "quando posso me aposentar", "auxílio-doença",
  "salário-maternidade", "BPC", "contribuição INSS".
tags: [inss, aposentadoria, previdencia, beneficios, transicao-2026, auxilio-doenca]
---

# 💊 Previdência Social — INSS e Aposentadoria

> ⚠️ Orientação educativa. Para planejamento previdenciário personalizado,
> consulte advogado previdenciarista. Fontes: [gov.br/inss](https://www.gov.br/inss)

---

## Tabela de Contribuição INSS 2026

### Empregado CLT (progressiva)

| Faixa salarial (R$) | Alíquota |
|--------------------|---------|
| Até 1.518,00 | 7,5% |
| 1.518,01 a 2.793,88 | 9,0% |
| 2.793,89 a 4.190,83 | 12,0% |
| 4.190,84 a 8.157,41 | 14,0% |

> Contribuição calculada progressivamente (como o IR), não sobre o total.

### MEI
- 5% do salário mínimo = R$ 75,90/mês (2026)
- Garante aposentadoria por idade (não por tempo)
- **Não** garante aposentadoria por incapacidade permanente (salvo complementação)

### Autônomo / Contribuinte Individual
- 20% sobre o salário de contribuição (entre R$ 1.518 e R$ 8.157,41)
- Pode optar por 11% (plano simplificado) — aposenta apenas por idade

---

## Modalidades de Aposentadoria 2026

### Para quem ingressou após nov/2019 (regra permanente)

| Modalidade | Mulheres | Homens |
|------------|----------|--------|
| Por idade | 62 anos + 15 anos contrib. | 65 anos + 15 anos contrib. |
| Por tempo (programada) | 57 anos + 30 anos contrib. | 62 anos + 35 anos contrib. |
| Especial (atividade nociva) | 25/20/15 anos + idade mín. | 25/20/15 anos + idade mín. |
| Por incapacidade permanente | Qualquer idade | Qualquer idade |

### Regras de Transição 2026 (quem contribuía antes de nov/2019)

**Opção 1 — Regra de Pontos (mais popular)**
- Mulheres: 93 pontos em 2026 (aumenta 1/ano até 100)
- Homens: 103 pontos em 2026 (aumenta 1/ano até 105)
- Fórmula: idade + anos de contribuição = pontos
- Contribuição mínima: mulheres 30 anos, homens 35 anos

**Opção 2 — Idade Progressiva**
- Mulheres: 59 anos em 2026 (aumenta 0,5/ano até 62)
- Homens: 64 anos em 2026 (aumenta 0,5/ano até 65)
- Contribuição mínima: mulheres 30 anos, homens 35 anos

**Opção 3 — Pedágio de 50%**
- Para quem faltava até 2 anos em nov/2019
- Precisa cumprir 50% do tempo restante
- Sem limite mínimo de idade

**Opção 4 — Pedágio de 100%**
- Para quem faltava mais de 2 anos em nov/2019
- Precisa cumprir 100% do tempo restante
- Mulheres: mínimo 57 anos | Homens: mínimo 60 anos

---

## Cálculo do Benefício

### Salário de Benefício
- Média de **100% dos salários** de contribuição desde julho/1994
- Corrigidos pelo INPC (índice de correção previdenciária)

### Alíquota do benefício
- **60%** do salário de benefício (base)
- **+2% por ano** que exceder 20 anos (homens) ou 15 anos (mulheres)
- **Exemplo:** homem com 40 anos de contribuição = 60% + (20 × 2%) = **100%**

### Teto do INSS 2026
- R$ 8.157,41/mês

```bash
# Estimar aposentadoria
python3 scripts/aposentadoria_estimativa.py --idade 45 --contribuicoes 20 --salario_medio 6000 --sexo masculino
```

---

## Outros Benefícios Previdenciários

| Benefício | Carência | Valor |
|-----------|----------|-------|
| Auxílio por incapacidade temporária | 12 meses | 91% do salário de benefício |
| Aposentadoria por incapacidade permanente | 12 meses | 100% (comum) ou 150% (acidente) |
| Salário-maternidade (CLT) | — | Último salário (pago pelo INSS) |
| Salário-maternidade (autônoma) | 10 meses | Média dos últimos 12 salários |
| Pensão por morte | — | 50% + 10% por dependente (mín. 60%) |
| BPC/LOAS (assistencial) | — | 1 salário mínimo |
| Auxílio-acidente | — | 50% do salário de benefício |

---

## Planejamento Previdenciário — Perguntas para orientar

1. Qual sua idade atual e há quantos anos contribui?
2. Pretende se aposentar em qual idade?
3. É empregado CLT, autônomo, MEI ou servidor público?
4. Tem períodos sem contribuição (desemprego, MEI, etc.)?
5. Trabalhou em atividades especiais (insalubres)?
6. Tem previdência privada (PGBL/VGBL)?

Com essas informações, calcular:
- Qual regra de transição é mais vantajosa
- Quantos anos ainda faltam
- Se vale a pena contribuir como autônomo para antecipar

---

## Planejamento Avançado de Carreira Contributiva

### Estratégias por perfil

| Perfil | Problema comum | Estratégia |
|--------|---------------|------------|
| **CLT com lacunas** | Períodos desempregado sem contribuir | Contribuição como autônomo retroativa (máx. 5 anos) via GPS |
| **MEI querendo + benefícios** | MEI só garante aposentadoria por idade | Complementar com contribuição de 15% (total 20%) |
| **Autônomo** | Sem vínculo — benefício depende só das contribuições | Escolher plano pleno (20%) para garantir todos benefícios |
| **Próximo da aposentadoria** | Poucos anos faltando | Simular custo vs. benefício de contribuir até o limite |
| **Alto salário** | Teto INSS em R$ 8.157,41 | PGBL para compensar; avaliar previdência privada complementar |

### Períodos sem contribuição — como regularizar

1. **Contribuição retroativa** — possível pelos últimos **5 anos** (art. 45-A da Lei 8.212/91)
   - Via GPS (Guia da Previdência Social) com código específico
   - Acréscimos: SELIC + 2% multa

2. **Certidão de Tempo de Contribuição (CTC)** — unifica períodos de regimes diferentes
   (RPPS ↔ RGPS)

3. **Período MEI** — conta como contribuição, mas apenas para aposentadoria por **idade**;
   para tempo de contribuição, é necessário ter contribuído pelo plano complementar

### PGBL vs. VGBL — quando usar cada um

| | PGBL | VGBL |
|---|------|------|
| **Deduz no IR** | Sim — até 12% da renda tributável | Não |
| **Tributação no resgate** | Sobre valor total (principal + rendimento) | Só sobre rendimento |
| **Para quem** | Quem declara IR completo e paga imposto | Quem declara simplificado ou isento |
| **Estratégia** | Deduzir agora na alíquota alta, resgatar na aposentadoria com alíquota menor | Acumular sem tributação sobre principal |

### Calculadoras disponíveis

```bash
# Estimativa de aposentadoria com ranking de regras
python3 scripts/aposentadoria_estimativa.py \
  --idade 45 --contribuicoes 20 --salario-medio 6000 --sexo M --pre-reforma

# Planejamento completo: estratégias, custo de contribuição, análise PGBL
python3 scripts/planejamento_contributivo.py \
  --idade 42 --contribuicoes 18 --salario 7000 --sexo F --pre-reforma \
  --plano pleno --renda-anual 84000 --aliquota-ir 0.275 --aporte-pgbl 10080
```
