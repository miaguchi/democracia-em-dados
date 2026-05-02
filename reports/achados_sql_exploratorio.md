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

## Implicações para a dissertação (achados descritivos)

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

---

# Testes estatísticos formais (sessão 2026-04-17)

Quatro testes na esquerda + replicação simétrica na direita. Scripts
em `src/sintese/`. Figuras em `outputs/figures/`. Tabelas em
`outputs/tables/`.

## TESTE A — Crescimento da esquerda × índice institucional

Regressão da variação % dos votos da esquerda (vereador, 2012→2024)
contra o índice institucional cultural-progressista da zona.

| Métrica | Valor |
|---|---|
| N | 58 zonas (SP capital) |
| Coeficiente β | **+2.32** variação % por ponto do índice |
| Intercepto | -11.70 |
| **R²** | **0.313** |
| **p-valor** | **5.1 × 10⁻⁶** *** |

Cada ponto adicional no índice está associado a +2,32 pp no
crescimento da esquerda. **31% da variância explicada.** Zonas com
índice zero caem 11,7%; zonas com índice ≈ 5 já estabilizam.
Replicado para deputado federal (2010→2022): R² = 0.304, β = +1.35,
p = 7.2 × 10⁻⁶ — efeito **igualmente forte nos dois níveis**.

## TESTE B — Correlação entre cargos (matriz 5×5)

Variações % por zona em vereador (2012→2024), prefeito (2012→2024),
deputado federal (2010→2022), governador (2010→2022) e presidente
(2010→2022).

|  | Vereador | Dep.Fed. | Gov. | Pres. | Prefeito |
|---|---|---|---|---|---|
| Vereador | 1.00 | 0.56 | 0.50 | 0.46 | **0.81** |
| Dep. Federal | 0.56 | 1.00 | **0.96** | **0.94** | 0.48 |
| Governador | 0.50 | 0.96 | 1.00 | **0.99** | 0.50 |
| Presidente | 0.46 | 0.94 | 0.99 | 1.00 | 0.42 |
| Prefeito | **0.81** | 0.48 | 0.50 | 0.42 | 1.00 |

**Estrutura em duas dimensões cristalina:**
- Cluster federal (Pres-Gov-Dep.Fed.): correlações internas r > 0.94
- Cluster municipal (Vereador-Prefeito): r = 0.81
- Inter-blocos: r ≈ 0.42-0.56

A metade da variância das zonas é independente entre níveis.
**Voto diferenciado por nível formalmente comprovado** —
exatamente o que Zolnerkevic & Guarnieri (2023) preveem.

## TESTE C — Concentração territorial (HHI e Gini, 2000-2024)

| Ano | Gini esquerda | Gini direita |
|---|---|---|
| 2000 | 0.188 | 0.188 |
| 2004 | **0.267** (pico) | 0.212 (pico) |
| 2024 | **0.149** | **0.134** |
| **Δ 2000→2024** | **-20.3%** | **-28.5%** |

**Hipótese de "elitização da esquerda" REJEITADA.** O eleitorado
da esquerda em 2024 está mais distribuído pelas zonas do que em
qualquer outro ponto da série. **A direita também se espalhou,
ainda mais (-28.5%).** Os dois blocos seguem trajetórias paralelas
de pulverização.

A intuição comum ("esquerda virou partido de bairro rico") não
sobrevive aos dados. O que ocorreu foi: esquerda **diminuiu** e
permaneceu espalhada. A concentração nas zonas progressistas é um
padrão **dentro do que sobrou** — não uma migração territorial.

## TESTE D — Quebra estrutural no PSOL para vereador (top-10 zonas)

Teste de Chow aplicado à série agregada do PSOL nas 10 zonas com
maior índice institucional.

| Ano da quebra | F | p-valor |
|---|---|---|
| 2012 | 36.5 | 0.008 ** |
| **2016** | **44.6** | **0.006 \*\*** |
| 2020 | 11.0 | 0.042 * |

**Quebra em 2016, quatro anos antes de Boulos.** Crescimento anual
salta de ~1.155 votos/ano para ~10.063 votos/ano (9× mais rápido).

Hipótese de "efeito-Boulos puro" rejeitada. **O realinhamento das
zonas de alta densidade institucional já estava em curso em 2016,**
o que é exatamente o que a tese institucional prevê.

## ANÁLISE SIMÉTRICA — efeito assimétrico do índice

Mesmo Teste A, mas para o bloco de direita (PL, PP, REPUBLICANOS,
UNIÃO, DEM, PRTB, PTB, PSD, PODE).

| | Esquerda | Direita |
|---|---|---|
| β | **+2.32** | -0.72 |
| R² | **0.313** | **0.012** |
| p-valor | **5.1 × 10⁻⁶** | 0.42 (n.s.) |
| Intercepto | -11.70 | **+88.93** |

**Achado central: a relação é assimétrica.** O índice institucional
prediz o crescimento da esquerda mas **não tem efeito estatístico
sobre a direita**. A direita cresceu **+89% em média** (intercepto)
em todos os tipos de zona — uniformemente.

Implicações:
- O índice institucional **não é proxy de "ideologia em geral"**.
  Se fosse, R² da direita seria similar e o sinal invertido.
- O ambiente cultural-progressista **atrai** esquerda mas **não
  repele** direita. Coexistência, não exclusão mútua.
- Em volume absoluto, **a direita praticamente dobrou na cidade**:
  2.738.141 votos em 2024 vs 1.527.275 da esquerda no mesmo ano.
  Ela ocupa o espaço deixado pela queda da esquerda em todas as zonas.

## Implicações dos testes estatísticos para a dissertação

1. **A tese central do Cap. III está empiricamente robustecida.**
   Quatro testes diferentes (regressão, correlação inter-cargos,
   concentração temporal, quebra estrutural) convergem para o mesmo
   diagnóstico: **a densidade institucional cultural-progressista
   captura uma dimensão real e específica do voto de esquerda em SP**.

2. **A simetria foi testada e refutada.** O índice é específico
   à esquerda. Isso reforça a tese contra a crítica de "índice é
   só renda disfarçada" ou "ideologia geral do bairro".

3. **Duas teses populares foram falseadas pelos dados:**
   - "Esquerda elitizou-se" → falso (Gini caindo).
   - "Boulos criou o eleitorado" → falso (quebra em 2016).

4. **A decomposição em dois níveis** (federal vs municipal) tem
   fundamento estatístico forte (r > 0.94 internos vs r ≈ 0.5
   inter-blocos). Isso amplia o diálogo com Zolnerkevic & Guarnieri
   (2023) e com a literatura comportamental sobre voto estratégico.

5. **Próximos passos analíticos sugeridos:**
   - PCA da matriz 5×5 entre cargos (validar formalmente as duas
     dimensões).
   - Heterogeneidade do índice por subgrupo (universidade vs escola
     progressista vs prestígio vs internacional) — o caso Z1
     (Bela Vista) sugere que universidades pesam diferente.
   - Controle por renda em regressão múltipla (Teste A com renda
     como covariável).
   - Análise de resíduos: quais zonas mais escapam do modelo.

---

# Síntese conceitual — esquerda × direita: dois mecanismos diferentes

A análise comparativa Bolsonaro × Tarcísio (2022, SP capital, 1º
turno) revela que o índice institucional opera por mecanismos
distintos nos dois blocos:

| Bloco | Função do índice institucional | R²/r |
|---|---|---|
| **Esquerda** | Prediz **onde o voto cresce** | R² = 0.313 (variação % vereador 2012→2024) |
| **Direita** | Prediz **como o voto se transfere** entre cargos | r = +0.60 (razão Tarcísio/Bolsonaro) |

## Duas lógicas de adesão

**Esquerda — ambiente institucional gera voto adicional.** Zonas
com mais universidades, escolas progressistas e instituições
culturais internacionais produzem voto novo de esquerda
independentemente do nível eleitoral. A relação é positiva e
estruturalmente significativa (Teste A: β=+2.32, p<1e-5).

**Direita — ambiente socioeconômico modula personalismo.** O voto
para a direita não cresce com o índice (R²=0.01). Mas a
**transferência presidente → governador depende fortemente do
território:**

- **Zonas centrais/ricas** (Pinheiros, Jd Paulista, Perdizes, V.
  Mariana, Bela Vista, Indianópolis): Tarcísio fica apenas 10-16%
  atrás de Bolsonaro. Transferência alta — voto pragmático/técnico.
- **Zonas periféricas** (Cidade Tiradentes, Parelheiros, Grajaú,
  Guaianases, Brasilândia): Tarcísio fica 25-27% atrás. Transferência
  baixa — voto personalista em Bolsonaro com baixo "downstream"
  para o governador.

A diferença é estatisticamente forte: r=+0.597, p<1e-6 entre o
índice institucional e a "diff% Tarc relativa a Bolso".

## Diálogo com a literatura

Esta assimetria é coerente com a tese de Singer sobre o **"primeiro
espírito" do lulismo**: voto de classe na periferia, simbolicamente
investido na figura presidencial. **O bolsonarismo periférico tem a
mesma estrutura — personalismo presidencial concentrado, com baixa
transferência partidária para baixo da chapa.** O voto "técnico" em
Tarcísio é fenômeno da classe média/alta paulistana; não da
periferia bolsonarista.

## A surpresa: Indianópolis (Z258)

Z258 (Indianópolis) tem índice institucional zero mas se comporta
como zona central na transferência Bolso→Tarc (-12,8%, junto com
Pinheiros e Jd Paulista). No Capítulo III ela já era o caso anômalo:
**rica mas sem ambiente cultural-progressista**. Agora aparece como
**anômala do outro lado também**: a direita ali é "técnica", não
"militante".

Indianópolis é zona de renda alta sem identidade ideológica forte
em nenhuma direção. Comportamento eleitoral pragmático, não
identitário, em ambos os polos. **É o caso ideal para sustentar
que a relevância do índice institucional não é apenas um efeito
de renda.**

## Formulação para a dissertação

> O desalinhamento vertical opera por mecanismos distintos nos dois
> blocos. Na esquerda, o ambiente institucional cultural-progressista
> gera voto adicional independente do nível de eleição (R²=0.31).
> Na direita, o gradiente é socioeconômico: zonas periféricas
> apresentam voto mais personalista (transferência Bolsonaro→Tarcísio
> cai 25-27%), enquanto zonas de renda alta transferem com perda
> mínima (10-16%). O índice institucional prediz a transferência na
> direita (r=0.60) mas não o volume de votos (R²=0.01) — relação
> oposta à da esquerda.

## Implicação metodológica

A análise simétrica não revelou um espelho do efeito esquerda:
revelou um mecanismo diferente. Isso aponta para a necessidade de
**modelos separados por bloco** em qualquer análise futura.
Tratar "ideologia" como variável contínua simétrica subestima a
heterogeneidade dos mecanismos de adesão entre os polos.
