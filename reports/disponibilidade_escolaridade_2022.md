# Disponibilidade de % superior completo (Censo 2022) por nível geográfico

Data da verificação: 2026-05-03

## Conclusão direta

**% com nível superior completo NÃO está disponível por setor censitário
no Censo 2022 — e nunca estará.** É variável da amostra, e o IBGE não
publica dados de amostra ao nível de setor por proteção de sigilo
estatístico (só ~10% dos domicílios entram).

Disponibilidade real por nível geográfico:

| Nível | Disponível? | Como acessar |
|---|---|---|
| **Setor censitário** | NÃO (nem está previsto) | — |
| **Município** | SIM | SIDRA tabelas 10063, 10064, 10065 |
| **Área de ponderação** | SIM (agora) | Microdados da amostra, FTP IBGE (3T/2025) |
| **Distrito/Subdistrito** | NÃO confirmado | — |
| **Bairro (CEM)** | A verificar | Pode ter via lote CEM-USP futuro |

## O que tem nos agregados por setor (universo)

Verificação direta no FTP IBGE (`Censo_Demografico_2022/Agregados_por_Setores_Censitarios/`):

Temas disponíveis no dicionário oficial (1411 variáveis):
- Alfabetização (V00644-V01005)
- Características do Domicílio (Partes 1, 2, 3)
- Cor ou Raça
- Demografia
- Parentesco
- Óbitos

Conjuntos PCT (Indígenas e Quilombolas) também disponíveis com
variáveis específicas.

**Educação/escolaridade NÃO aparece como tema** — apenas alfabetização
(sabe ler/escrever ou não), que é proxy fraca em áreas urbanas.

## SIDRA — tabelas com superior completo (nível município)

| Tabela | Conteúdo | Níveis disponíveis |
|---|---|---|
| 10063 | Faixas etárias × sexo × raça | BR, GR, UF |
| 10064 | Faixas etárias | BR, GR, UF, **município** |
| 10065 | Sexo × raça | BR, GR, UF, **município** |

Para SP capital, isso daria **um único valor agregado** (município
inteiro). Não diferencia entre zonas — inútil para a análise por
zona eleitoral.

## Microdados da amostra por área de ponderação

Previstos para 3T/2025; em maio/2026 devem estar disponíveis.

**Área de ponderação** = agrupamento de setores censitários (≈ bairros).
SP capital tem ~310 áreas de ponderação. Não é setor mas é mais
granular que município.

### O que seria necessário para usar

1. Baixar microdados da amostra de SP no FTP do IBGE.
2. Filtrar variável de instrução (≥ superior completo).
3. Calcular % por área de ponderação (com pesos amostrais).
4. Carregar shapefile das áreas de ponderação SP 2022.
5. Spatial join: área de ponderação → zona eleitoral.
   Como uma zona pode conter várias áreas e vice-versa, precisa
   ponderar por área de interseção ou por população.
6. Agregar % superior completo por zona (média ponderada).

**Trabalho estimado**: 3-5 horas de ETL séria, com cuidado para
preservar pesos amostrais.

## Alternativas pragmáticas para o projeto

| Opção | Custo | Qualidade |
|---|---|---|
| Manter alfabetização como proxy | 0h (já feito) | Baixa (saturada em SP) |
| Usar % superior do município (1 valor) | 1h | Inútil — não varia por zona |
| Microdados → área de ponderação → zona | 3-5h | Boa — variável por zona |
| Solicitar dado especial ao IBGE (RAIS-IBGE) | semanas | Excelente, mas burocrático |

**Recomendação:** se o controle por escolaridade for crítico para a
banca, vale a ETL de microdados → área de ponderação → zona. Se for
suficiente para o argumento, manter alfabetização (já feito) e
relatar transparentemente a limitação no capítulo metodológico.

## Para registro

A questão "renda + escolaridade substituem o índice institucional?"
foi respondida no atual M7 com alfabetização: **NÃO**. O índice
ganha 9.4 pp de R² acima de renda + alfabetização. Se substituirmos
alfabetização por % superior (variável correlacionada mas mais forte),
o ganho marginal pode cair, mas dificilmente desaparece — porque o
índice institucional captura presença física de instituições, não só
densidade de pessoas educadas que moram ali.
