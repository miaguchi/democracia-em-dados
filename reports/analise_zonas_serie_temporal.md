# Análise comparativa por zona eleitoral — vereador × deputado federal

Data: 2026-04-17
Banco: `democracia_em_dados` (MySQL)
Queries: [scripts/sql/queries_dep_federal_serie.sql](../scripts/sql/queries_dep_federal_serie.sql)
Views: `v_esquerda_vereador`, `v_esquerda_dep_federal`

## Recorte

- Bloco "esquerda completa" = PT, PSOL, PCdoB, PDT, PSB, PV, REDE,
  PSTU, PCO, UP (Bolognesi, Ribeiro & Codato 2023).
- Janela vereador: 2012 → 2024 (ciclo municipal de pico → recente).
- Janela deputado federal: 2010 → 2022 (ciclo federal de pico → recente).
- Universo: zonas eleitorais do estado de SP com voto > 0 no ano-base.

## 1. Tendência por zona — vereador (2012 → 2024)

| Tendência | Zonas |
|---|---|
| **Caiu** | **369** |
| **Cresceu** | **56** |

Em 87% das zonas, o voto da esquerda para vereador em 2024 é menor
do que em 2012. Apenas 13% das zonas registraram crescimento.

## 2. Tendência por zona — deputado federal (2010 → 2022)

| Tendência | Zonas |
|---|---|
| **Caiu** | **354** |
| **Cresceu** | **69** |

Para deputado federal, o quadro é semelhante: 84% das zonas com
queda. Mas o número absoluto de zonas em crescimento é maior que
no vereador (69 vs 56).

## 3. Cruzamento dos dois níveis

Cada zona é classificada por sua tendência em cada nível eleitoral:

| Vereador | Dep. Federal | Zonas |
|---|---|---|
| Caiu | Caiu | **330** |
| Caiu | Cresceu | 37 |
| Cresceu | Cresceu | **32** |
| Cresceu | Caiu | 24 |
| **Total** | | **423** |

### Leitura

- **77% das zonas caíram em ambos os níveis** (330/423). Padrão
  dominante: declínio coordenado da esquerda em todos os níveis.
- **8% (32 zonas) cresceram em ambos os níveis.** São as "zonas
  progressistas" — provavelmente as zonas-alvo do projeto.
- **9% (37 zonas) cresceram só no federal mas caíram no municipal.**
  Indício de voto diferenciado por nível (federal Lula, municipal
  centro-direita).
- **6% (24 zonas) cresceram só no vereador mas caíram no federal.**
  Anômalo — pode ser efeito de candidato local específico ou
  artefato de redistribuição (ver ressalva).

## 4. Padrão geográfico — periferia × centro

A periferia parece concentrar mais o padrão "caiu em ambos" e o
"caiu vereador, cresceu federal". As zonas centrais (Pinheiros,
Perdizes, Bela Vista, Vila Mariana, Butantã) tendem a cair menos
ou crescer no vereador — coerente com a tese do índice institucional
cultural-progressista.

A queda mais severa para vereador na periferia, comparada à
manutenção/recuperação no federal, sugere que **a esquerda perdeu o
voto periférico no nível municipal mas conseguiu mobilizá-lo
parcialmente para Lula no federal**.

## 5. Ressalva metodológica — redistribuição TRE-SP 2023

A comparação entre 2010 e 2022 (ou 2012 e 2024) sofre interferência
da redistribuição de zonas eleitorais feita pelo TRE-SP em 2023:

- Algumas zonas foram extintas e seus eleitores realocados.
- Outras foram criadas, sem histórico anterior comparável.
- Em algumas, os limites geográficos mudaram, alterando a composição
  do eleitorado dentro da mesma `nr_zona`.

**Implicação:** as contagens "369 caíram" e "56 cresceram" são
aproximações. Para análise definitiva, é necessário:

1. Identificar zonas com `nr_zona` consistente entre 2012 e 2024
   (filtro adicional necessário).
2. Excluir zonas afetadas pela redistribuição.
3. Considerar análise por seção eleitoral (mais granular, mas com
   instabilidade própria).

## Implicações para a dissertação

1. **As 32 zonas que crescem em ambos os níveis são fortes
   candidatas para o índice institucional.** Cruzar essa lista com
   o índice cultural-progressista (R²=0.44) deve mostrar
   sobreposição alta.
2. **As 37 zonas com voto diferenciado (caiu_ver / cresceu_dep) são
   o caso analítico mais interessante para o argumento de
   Zolnerkevic & Guarnieri (2023):** voto estratégico federal
   coexiste com adesão a centro-direita no municipal.
3. **A ressalva da redistribuição precisa ser formalizada no
   capítulo metodológico** antes de qualquer afirmação quantitativa
   sobre "número de zonas em crescimento".
