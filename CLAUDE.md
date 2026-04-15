# Projeto: Democracia em Dados / Radiografia Eleitoral do Brasil

## Contexto
Projeto de ciência política computacional analisando comportamento eleitoral 
em zonas eleitorais de São Paulo (2012-2024), com foco em bairros ricos. 
Serve simultaneamente como base empírica para dissertação de mestrado 
(DCP/FFLCH-USP) e como portfólio técnico para BNDES/setor privado.

## Stack
- Python 3.11+ via conda-forge
- pandas, geopandas, statsmodels, linearmodels, libpysal/esda
- matplotlib, seaborn para viz estática
- MySQL Workbench para dados estruturados
- reportlab para PDFs
- pytest para testes

## Convenções de código
- Type hints obrigatórios em funções públicas
- Docstrings no estilo NumPy
- snake_case para funções/variáveis, PascalCase para classes
- Black + ruff via pre-commit
- Toda função estatística precisa de teste pytest correspondente

## Estrutura de diretórios
- data/raw/ — dados brutos do TSE/IBGE/CEM, imutáveis, no .gitignore
- data/processed/ — output dos pipelines, regenerável
- src/ — módulos Python organizados por eixo (partidario, financiamento, urbano)
- src/sintese/ — análises transversais que combinam mais de um eixo
- src/casos/<cidade>/ — replicações e cidades-caso (uma subpasta por cidade)
- src/ingestao/, src/dominio/ — infraestrutura compartilhada
- scripts/ — geradores de PDF e utilitários executáveis
- notebooks/ — exploração apenas, não entram em resultados finais
- reports/ — markdown e PDFs versionados
- outputs/figures, outputs/tables, outputs/logs
- tests/

## Decisões metodológicas já tomadas
- Escala ideológica: Bolognesi, Ribeiro & Codato (2023)
- Limiar centro-direita/direita: 7,00 (com sensibilidade testada para MDB)
- Volatilidade: Pedersen (1979) decomposta por Bartolini & Mair (1990)
- Vizinhança espacial: k=6 nearest neighbors para LISA
- Geometrias: pacote geobr (não shapefiles manuais)
- Locais de votação: base CEM/USP EL2022_LV_ESP_CEM_V2

## Regras importantes para o agente
1. NUNCA simular dados. Se um dado não existe localmente, parar e avisar.
2. Sempre validar Content-Length de downloads do TSE.
3. Resultados estatísticos precisam de IC ou erro-padrão reportado.
4. Antes de implementar nova análise, escrever teste pytest primeiro.
5. Toda figura final precisa de versão PNG (300 dpi) e código que a regenera.
6. Não decidir econometria sozinho — propor opções e esperar confirmação.
7. Commits seguem Conventional Commits (feat:, fix:, docs:, test:, refactor:).

## Comandos comuns
- `make test` — roda pytest
- `make lint` — ruff + black --check
- `make pipeline-eixo1` — regenera todos os outputs do eixo partidário
- (adicionar conforme criados)
