# Inventário da base CEM/USP EL2022_LV_ESP_CEM_V2

Data: 2026-04-16
Objetivo: mapear categorias de locais de votação para planejamento futuro de teste placebo.

## (a) Estrutura da base

- **Arquivo:** `data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp`
- **Dimensões:** 10.843 linhas x 132 colunas
- **Geometria:** POINT (coordenadas dos locais de votação)

### Colunas descritivas

| Coluna     | Tipo    | Descrição                          |
|------------|---------|-------------------------------------|
| ID         | int64   | Identificador                       |
| ANO_ELE    | int64   | Ano da eleição (2022)               |
| COD_LV     | int64   | Código do local de votação          |
| NOME_LV    | str     | Nome do local de votação            |
| LV_TIT     | str     | Título honorífico (Professor, etc.) |
| LV_TIPO    | str     | Tipo/categoria do local             |
| END_LV     | str     | Endereço                            |
| CODESC     | float64 | Código da escola (quando aplicável) |
| MUN_SIG    | str     | Sigla do município                  |
| MUN_NOME   | str     | Nome do município                   |
| CD_MUN_T   | int64   | Código do município (TSE)           |
| CD_MUN_I   | int64   | Código do município (IBGE)          |
| ZE_COD     | str     | Código da zona eleitoral            |
| ZE_NUM     | int64   | Número da zona eleitoral            |
| ZE_NOME    | str     | Nome da zona eleitoral              |
| FR_LIM     | str     | Fronteira/limite                    |
| ORIG_LL    | str     | Origem lat/lon (ex: TSE)            |

### Colunas de resultados eleitorais

Prefixos indicam turno e cargo:
- `PS22_` — 1o turno, Presidente
- `GO22_` — 1o turno, Governador
- `SE22_` — 1o turno, Senador
- `DF22_` — 1o turno, Deputado Federal
- `DE22_` — 1o turno, Deputado Estadual

Os sufixos numéricos correspondem a códigos de candidato/partido.

## (b) Categorias de local de votação (LV_TIPO)

A coluna `LV_TIPO` contém 188 categorias únicas. Abaixo as mais frequentes,
organizadas por perfil funcional.

### Educacionais (maioria)

| LV_TIPO  | Contagem | Descrição provável                    |
|----------|----------|----------------------------------------|
| EE       | 4.502    | Escola Estadual                        |
| EMEF     | 1.770    | Escola Municipal de Ensino Fundamental |
| EM       | 1.127    | Escola Municipal                       |
| EMEI     | 512      | Escola Municipal de Educação Infantil  |
| EMEB     | 480      | Escola Municipal de Educação Básica    |
| COLEGIO  | 466      | Colégio (genérico)                     |
| EMEIEF   | 216      | EMEI + EF combinada                    |
| EMEIF    | 110      | EMEI + EF combinada (variante)         |
| FAC      | 107      | Faculdade                              |
| UNIV     | 85       | Universidade                           |
| ESCOLA   | 74       | Escola (genérica)                      |
| UME      | 72       | Unidade Municipal de Educação          |
| ETEC     | 70       | Escola Técnica Estadual                |
| EMEFEI   | 56       | EMEF + EI combinada                    |
| EPG      | 54       | Escola da Prefeitura de Guarulhos      |
| EEPG     | 51       | Escola Estadual de 1o Grau             |
| CEMEB    | 51       | Centro Municipal de Educação Básica    |
| EEPSG    | 46       | Escola Estadual de 1o e 2o Grau        |

### Educação infantil / creches

| LV_TIPO      | Contagem |
|--------------|----------|
| CEI          | 106      |
| CRECHE       | 45       |
| CMEI         | 15       |
| CRECHE MUN   | 22       |
| CEMEI        | 36       |

### CEUs (equipamentos multiuso)

| LV_TIPO   | Contagem |
|-----------|----------|
| CEU       | 22       |
| CEU EMEF  | 16       |
| CEU EMEI  | 10       |
| CEU CEI   | 6        |
| CEU CEE   | 1        |

### Sistema S e profissionalizantes

| LV_TIPO | Contagem |
|---------|----------|
| SESI    | 71       |
| SENAI   | 13       |
| SENAC   | 12       |
| FATEC   | 20       |
| ETE     | 34       |

### Sistema prisional / socioeducativo

| LV_TIPO    | Contagem |
|------------|----------|
| CDP        | 30       |
| PENIT      | 27       |
| FUND CASA  | 16       |
| CPP        | 1        |

### Saúde

| LV_TIPO      | Contagem |
|--------------|----------|
| POSTO SAUDE  | 22       |
| UBS          | 1        |

### Associações e entidades

| LV_TIPO     | Contagem |
|-------------|----------|
| ASSOC       | 27       |
| ASSOC CULT  | 3        |
| ASSOC ED    | 2        |
| APAE        | 11       |
| COOP        | 3        |
| ASSIST SOC  | 1        |

### Religiosos

| LV_TIPO   | Contagem |
|-----------|----------|
| IGREJA    | 8        |
| PASTORAL  | 1        |

### Esportivos / culturais / outros

| LV_TIPO    | Contagem |
|------------|----------|
| CLUBE      | 3        |
| CLUBE ATL  | 1        |
| ESP CULT   | 1        |
| BIBLI      | 1        |
| GURI       | 1        |
| EQUIP PUB  | 3        |
| CREAS      | 1        |
| CCA        | 1        |
| SECRETARIA | 1        |
| NUCLEO     | 1        |
| CDC        | 1        |

### Título honorífico (LV_TIT)

A coluna `LV_TIT` contém o título do homenageado. As 5 mais frequentes:

| LV_TIT      | Contagem |
|-------------|----------|
| (sem título)| 5.673    |
| PROFESSOR   | 1.830    |
| PROFESSORA  | 1.758    |
| DOUTOR      | 425      |
| PADRE       | 132      |

## (c) Amostra de 50 nomes de locais de votação (NOME_LV)

Amostra aleatória (seed=42) para ilustrar a diversidade dos nomes:

| #  | Nome                                     |
|----|------------------------------------------|
| 1  | ROSENTINA FARIA SYLLOS                   |
| 2  | PAULO KOELLE                             |
| 3  | VILMA LEONE DAL POGETTO                  |
| 4  | ENGENHEIRO GOULART                       |
| 5  | ANIZIO DA SILVEIRA                       |
| 6  | ASP NAYAN XAVIER RIBEIRO                 |
| 7  | SUZANA DIAS                              |
| 8  | BRUNO FLORENZANO                         |
| 9  | ANHANGUERA EDUCACIONAL                   |
| 10 | VICENTE DE PAULA ALMEIDA                 |
| 11 | OLIVIO PEIXOTO                           |
| 12 | ANTONIO ADIB CHAMMAS                     |
| 13 | BENEDITINO                               |
| 14 | JOEL ANTONIO DE LIMA GENESIO             |
| 15 | MARIA ELENA COLONIA                      |
| 16 | AYRES DE MOURA                           |
| 17 | FADA AZUL                                |
| 18 | BERNADETE DE LOURDES GOMES CLAUDIO       |
| 19 | JOSE ARNONI                              |
| 20 | MARIA CRISTINA DINIZ DE ALMEIDA          |
| 21 | ROQUE CONCEICAO MARTINS                  |
| 22 | JOSE BENEDITO LEITE BARTHOLOMEI          |
| 23 | YONNE DIAS DE AGUIAR                     |
| 24 | LAZARA ANTONINHA DA SILVA MILHORANCA     |
| 25 | CRIANCA FELIZ                            |
| 26 | JONAS PIRES                              |
| 27 | ESPIRITO SANTO                           |
| 28 | PRESCILIANO PINTO DE OLIVEIRA            |
| 29 | JARDIM DO ENGENHO                        |
| 30 | ANTONIO MARINHO DE CARVALHO FILHO        |
| 31 | SEBASTIAO PEREIRA VIDAL                  |
| 32 | ANTONIO MOLLON                           |
| 33 | ANTONIO DE LOURDES RONDON                |
| 34 | ALICE ROLIM DE MOURA HOLTZ               |
| 35 | ABRAO BENJAMIM                           |
| 36 | SAO LUIS                                 |
| 37 | PAULINO CARLOS                           |
| 38 | LUIZ GONZAGA HORTA LISBOA                |
| 39 | PLINIO AYROSA                            |
| 40 | DAVID ZEIGER                             |
| 41 | ALICE ROSSITO CERVONE                    |
| 42 | VITOR GERALDO SIMONSEN                   |
| 43 | ANTONIO MIGUEL PEREIRA JUNIOR            |
| 44 | TAUFIK DAUD KURBAN                       |
| 45 | EDGARD PIMENTEL REZENDE                  |
| 46 | CIVITATIS                                |
| 47 | NELSON MANDELA                           |
| 48 | ALTINA MAYNARDES ARAUJO                  |
| 49 | JOSE TOMAZ NETO                          |
| 50 | JOAQUIM PEREIRA DA SILVA                 |

**Observação:** A grande maioria dos nomes são homenagens a pessoas.
Nomes descritivos (ex: "Fada Azul", "Criança Feliz", "Jardim do Engenho",
"Espírito Santo") são minoria e tendem a ser creches/escolas infantis
ou instituições religiosas.

## (d) Classificação dos locais para teste placebo

Classificação decidida em 2026-04-16. Critério: "educacional" = qualquer
instituição cuja função primária é ensino (inclui Sistema S, colégios
confessionais, EJA, educação especial). CEUs com escola nomeada no tipo
(CEU EMEF, CEU EMEI, CEU CEI, CEU CEE) são educacionais; CEU puro é
não-educacional por ser equipamento multiuso.

### Não-educacional (~161 locais)

Candidatos ao grupo placebo.

| Subgrupo | LV_TIPO | N |
|---|---|---|
| Prisional/socioeducativo | CDP (30), PENIT (27), FUND CASA (16), CPP (1) | 74 |
| Associações/cooperativas | ASSOC (27), ASSOC CULT (3), COOP (3), ASSIST SOC (1) | 34 |
| Saúde | POSTO SAUDE (22), UBS (1) | 23 |
| Religioso | IGREJA (8), PASTORAL (1) | 9 |
| Administrativo/público | AUTARQUIA (5), SECRETARIA (1) | 6 |
| Esportivo | CLUBE (3), CLUBE ATL (1), CDC (1) | 5 |
| Cultural | ESP CULT (1), BIBLI (1), GURI (1) | 3 |
| Equipamento público | EQUIP PUB (3) | 3 |
| Comunidade/assentamento | BAIRRO (3), ASSENT (1) | 4 |
| Assistência social | CREAS (1), CCA (1) | 2 |
| CEU puro | CEU (22) | 22 |
| Nucleo assistencial | NUCLEO (1) | 1 |
| Fundações não-educacionais | FUND: LAR ANALIA FRANCO, LAR MONSENHOR FILIPPO | 2 |

**Total não-educacional: ~161 locais** (excluindo as 2 fundações que
precisam ser filtradas por nome, não por LV_TIPO).

### Educacional (~10.682 locais)

Todo o restante, incluindo:
- Escolas estaduais/municipais e variantes (EE, EMEF, EM, EMEI, EMEB, etc.)
- Creches e educação infantil (CEI, CRECHE, CEMEI, CMEI, etc.)
- Ensino superior (FAC, UNIV, FATEC, FECAP, ITB)
- Ensino técnico (ETEC, ETE)
- Sistema S (SESI=71, SENAI=13, SENAC=12, SEBRAE=1)
- CEUs com escola (CEU EMEF=16, CEU EMEI=10, CEU CEI=6, CEU CEE=1)
- EJA e educação especial (CEEJA, CIEJA, EJA, EMEE, CEE, APAE)
- Fundações educacionais (13 das 15 FUND)
- Institutos (INST=7, todos educacionais)
- Associações educacionais (ASSOC ED=2)
- Colégios e variantes (COLEGIO, COL MUN, LICEU, EXTERNATO, etc.)

### Notas metodológicas

1. O grupo não-educacional (~161) é pequeno frente ao educacional (~10.682),
   o que limita poder estatístico do placebo.
2. O subgrupo prisional (74 locais) tem eleitorado com perfil sociodemográfico
   muito distinto — considerar análise separada ou controle adicional.
3. Duas fundações (LAR ANALIA FRANCO, LAR MONSENHOR FILIPPO) precisam ser
   filtradas por NOME_LV, não por LV_TIPO, pois as demais 13 FUND são
   educacionais.
