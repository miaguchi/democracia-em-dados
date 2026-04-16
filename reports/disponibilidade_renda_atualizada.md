# Disponibilidade de dados de renda atualizados (Censo 2022)

Data da verificação: 2026-04-16

## 1. IBGE — Rendimento do responsável por setor censitário

**Status: DISPONÍVEL desde 30/04/2025.**

O IBGE divulgou em 30 de abril de 2025 os dados de rendimento do
responsável pelo domicílio como parte dos "Agregados por Setores
Censitários: Resultados do Universo" do Censo Demográfico 2022.

- **Nível de agregação:** setor censitário (o mais desagregado possível)
- **Variável:** rendimento nominal mensal do responsável pelo domicílio
- **Cobertura:** todo o território nacional, incluindo São Paulo
- **Tipo de dado:** universo (não amostra — todos os domicílios)
- **Formato:** CSV e XLSX

**Acesso:**
- FTP: https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/
- Catálogo: https://biblioteca.ibge.gov.br/index.php/biblioteca-catalogo?view=detalhes&id=2102136
- Dicionário de dados: disponível no mesmo diretório FTP (dicionario_de_dados_renda_responsavel.xlsx)
- Nota metodológica: n. 02/2025 (descreve coleta, crítica, imputação e limitações)

**Não precisa de login, API ou registro.** Download direto pelo FTP.

**Limitação:** é o rendimento do *responsável*, não a renda domiciliar
per capita completa. A renda per capita depende dos microdados da
amostra, que têm cronograma separado (ver item 2).

## 2. IBGE — Resultados da amostra (renda domiciliar completa)

**Status: resultados preliminares de Trabalho e Rendimento já divulgados.**

Os resultados preliminares da amostra sobre Trabalho e Rendimento foram
divulgados em dezembro de 2024 (dados iniciais) com atualizações em 2025.

- **Nível de agregação dos resultados preliminares:** Brasil, UF, município
  (NÃO por setor censitário)
- **Microdados da amostra:** previstos para o 3º trimestre de 2025
  (permitiriam recalcular renda por áreas de ponderação, mas não por
  setor censitário individual)

**Para o projeto:** os microdados da amostra, quando disponíveis,
permitiriam calcular renda domiciliar per capita por área de ponderação
(agrupamento de setores), mas NÃO por setor individual. Para setor
censitário, o rendimento do responsável (item 1) é o que existe.

## 3. SIDRA/IBGE — Tabelas online

**Status: tabelas do Censo 2022 disponíveis no SIDRA.**

Tabelas relevantes:
- Tabela 10296: rendimento domiciliar per capita mensal (nível município)
- Tabela 10297: participação do rendimento do trabalho na composição
  do rendimento domiciliar

**Nível de agregação:** município e UF (NÃO setor censitário).
O SIDRA não disponibiliza dados por setor — para setor, usar o FTP.

## 4. Fundação Seade — IPVS versão 2022

**Status: DISPONÍVEL (atualizado com Censo 2022).**

O IPVS (Índice Paulista de Vulnerabilidade Social) versão 2022 foi
atualizado com dados do Censo 2022.

- **Nível de agregação:** setor censitário
- **Cobertura:** ~93 mil setores do Estado de São Paulo (de ~103 mil)
- **Variáveis:** 6 grupos de vulnerabilidade social (combinam renda do
  responsável + características demográficas)
- **Formato:** shapefile com coordenadas + grupo IPVS

**Acesso:**
- Portal: https://ipvs.seade.gov.br/
- Dados abertos: https://www.governoaberto.sp.gov.br/dataset/seade-ipvs-versao-2022
- Principais resultados: https://ipvs.seade.gov.br/wp-content/uploads/2026/01/IPVS-2022-principais-resultados.pdf

**Não precisa de login.** Download direto.

**Para o projeto:** o IPVS é um índice composto (não renda pura), mas
pode servir como proxy de vulnerabilidade/renda. Vantagem: já está em
shapefile com geometria de setores.

## 5. CEM/USP — Bases por setor censitário

**Status: em andamento, São Paulo ainda NÃO disponível.**

O CEM está organizando dados do Censo 2022 por setor censitário para
as 22 principais regiões metropolitanas do Brasil. Primeiro lote
(Baixada Santista, Belém, Belo Horizonte, Brasília, Campinas)
já disponível. RM de São Paulo: previsto para lotes futuros.

- Acesso: https://centrodametropole.fflch.usp.br/pt-br/download-de-dados

## Resumo para o projeto

| Fonte | Disponível? | Nível | Variável de renda |
|-------|-------------|-------|-------------------|
| IBGE FTP (universo) | SIM | Setor censitário | Rendimento do responsável |
| IBGE amostra | PARCIAL | Município/UF | Renda per capita (micro em breve) |
| SIDRA | SIM | Município | Renda per capita |
| Seade IPVS 2022 | SIM | Setor censitário | Índice composto (proxy) |
| CEM/USP | NÃO (SP pendente) | Setor censitário | 246 variáveis (quando sair) |

**Recomendação para atualizar os dados de renda do projeto:**
O caminho mais direto é baixar os agregados de rendimento do responsável
por setor censitário do FTP do IBGE (item 1) e refazer o join espacial
que hoje usa o Censo 2010. Isso atualiza a variável de renda de 2010
para 2022 sem mudar a metodologia.
