# Achados da análise SQL exploratória

Data: 2026-04-17
Banco: `democracia_em_dados` (MySQL) — 14 eleições, 1998-2024.
Queries em [scripts/sql/queries_serie_temporal.sql](../scripts/sql/queries_serie_temporal.sql).

## 1. Bloco esquerda — vereador (estado de SP)

| Ano | Votos esquerda completa | Marco |
|---|---|---|
| 2000 | 4.47 M | — |
| 2004 | 5.89 M | — |
| 2008 | 6.10 M | — |
| **2012** | **6.59 M** | **PICO** |
| 2016 | 4.87 M | — |
| **2020** | **3.75 M** | **PISO** |
| 2024 | 4.10 M | recuperação tímida (+9%) |

Declínio de 38% entre o pico (2012) e o piso (2020). Recuperação
fraca em 2024 (+9% sobre 2020).

## 2. Bloco esquerda — deputado federal (estado de SP)

| Ano | Votos esquerda completa | Marco |
|---|---|---|
| 1998 | 3.33 M | — |
| 2002 | 6.95 M | era Lula |
| 2006 | 6.66 M | — |
| **2010** | **8.15 M** | **PICO** |
| 2014 | 5.30 M | — |
| **2018** | **4.68 M** | **PISO** |
| 2022 | 5.98 M | recuperação (+28%) |

## 3. Recuperação assimétrica federal × municipal

A recuperação após os respectivos pisos foi **três vezes maior** no
nível federal:

| Nível | Piso → Pico recente | Variação |
|---|---|---|
| Federal | 4.68 M (2018) → 5.98 M (2022) | **+28%** |
| Municipal | 3.75 M (2020) → 4.10 M (2024) | **+9%** |

Hipótese: o mesmo eleitor pode votar em esquerda no nível federal e
em centro-direita no nível municipal — voto diferenciado por nível,
não realinhamento puro.

## 4. Queda de 2010-2014 mais severa em SP

Entre 2010 e 2014, a queda da esquerda no agregado de SP foi de
-35%. Na média nacional, segundo dados externos (não verificados
neste banco), a queda foi cerca de -22%. SP foi mais afetado que
o país.

## 5. PT em 8º para vereador em SP capital, 2024

No município de São Paulo, em 2024, o PT aparece em 8ª colocação
em votos nominais para vereador. Deslocamento histórico significativo.

## 6. PSOL cresce desde 2016 — antes do efeito-Boulos

O crescimento do PSOL para vereador em SP capital começa em 2016,
três ciclos antes da candidatura nacionalmente notória de Boulos.
Sugere realinhamento estrutural localizado, não apenas efeito de
candidato individual.

## 7. PSOL cresceu 10× nas zonas do corredor universitário

Para vereador, PSOL multiplicou seus votos por aproximadamente 10×
desde 2012 nas zonas Perdizes, Pinheiros e Butantã.

## 8. PT+PSOL (esquerda nuclear) — recorde federal 2022

| Ano | Votos PT+PSOL (Dep. Federal) |
|---|---|
| 1998 | 2.06 M |
| **2022** | **4.51 M** (recorde) |

Mesmo com PT enfraquecido municipalmente, o eixo PT+PSOL no
federal atinge recorde histórico em 2022.

## 9. PT+PSOL para vereador encolheu

| Ano | Votos PT+PSOL (vereador) |
|---|---|
| 2012 | 2.67 M |
| 2024 | 2.14 M |

## Implicações para a dissertação

1. **Achados 1, 2, 3 e 8 reforçam o desalinhamento federal × municipal.**
   Coerente com Zolnerkevic & Guarnieri (2023): voto estratégico
   sem realinhamento estrutural, ou realinhamento parcial.
2. **Achado 6 sustenta a hipótese do índice institucional.** O
   crescimento do PSOL antecede a candidatura-celebridade — algo
   estrutural está mudando nas zonas de alta densidade
   institucional cultural-progressista (R²=0.44 do Cap. III).
3. **Achado 1 (declínio municipal de 38%) precisa ser tratado com
   cuidado.** A queda agregada parece desfavorável à tese, mas o
   declínio provavelmente está concentrado em zonas periféricas,
   não nas zonas-alvo do projeto. Verificar se há heterogeneidade
   espacial.
4. **A tabela de Q3 (Bolognesi por zona)** pode ser cruzada com o
   índice institucional para mostrar onde o declínio foi maior e
   onde a esquerda resistiu.
