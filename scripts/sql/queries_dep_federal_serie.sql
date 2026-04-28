-- =============================================================================
-- Série temporal — Esquerda em SP, deputado federal (1998-2022)
-- Banco: democracia_em_dados (MySQL)
-- =============================================================================
-- Códigos de partidos (escala Bolognesi, Ribeiro & Codato 2023 — esquerda):
--   13=PT, 50=PSOL, 65=PCdoB, 12=PDT, 40=PSB, 43=PV, 18=REDE,
--   16=PSTU, 29=PCO, 80=UP
-- Cargos:
--   6  = Deputado Federal
--   13 = Vereador
-- =============================================================================

USE democracia_em_dados;


-- ---------------------------------------------------------------------------
-- VIEW: v_esquerda_vereador
-- Pivot por zona × ano (vereador) — anos municipais 2000-2024
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_esquerda_vereador AS
SELECT v.nr_zona,
    SUM(CASE WHEN e.ano_eleicao = 2000 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2000,
    SUM(CASE WHEN e.ano_eleicao = 2004 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2004,
    SUM(CASE WHEN e.ano_eleicao = 2008 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2008,
    SUM(CASE WHEN e.ano_eleicao = 2012 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2012,
    SUM(CASE WHEN e.ano_eleicao = 2016 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2016,
    SUM(CASE WHEN e.ano_eleicao = 2020 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2020,
    SUM(CASE WHEN e.ano_eleicao = 2024 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2024
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)
  AND v.cd_cargo = 13
  AND e.nr_turno = 1
GROUP BY v.nr_zona;


-- ---------------------------------------------------------------------------
-- VIEW: v_esquerda_dep_federal
-- Pivot por zona × ano (deputado federal) — anos federais 1998-2022
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_esquerda_dep_federal AS
SELECT v.nr_zona,
    SUM(CASE WHEN e.ano_eleicao = 1998 THEN v.qt_votos_nominais ELSE 0 END) AS esq_1998,
    SUM(CASE WHEN e.ano_eleicao = 2002 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2002,
    SUM(CASE WHEN e.ano_eleicao = 2006 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2006,
    SUM(CASE WHEN e.ano_eleicao = 2010 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2010,
    SUM(CASE WHEN e.ano_eleicao = 2014 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2014,
    SUM(CASE WHEN e.ano_eleicao = 2018 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2018,
    SUM(CASE WHEN e.ano_eleicao = 2022 THEN v.qt_votos_nominais ELSE 0 END) AS esq_2022
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)
  AND v.cd_cargo = 6
  AND e.nr_turno = 1
GROUP BY v.nr_zona;


-- ---------------------------------------------------------------------------
-- Q1: Trajetória da esquerda por zona (deputado federal)
-- ---------------------------------------------------------------------------
SELECT * FROM v_esquerda_dep_federal ORDER BY esq_2022 DESC LIMIT 20;


-- ---------------------------------------------------------------------------
-- Q2: Variação 2010→2022 por zona (deputado federal)
-- Conceito: cálculo de variação percentual sobre VIEW
-- ---------------------------------------------------------------------------
SELECT nr_zona, esq_2010, esq_2022,
    ROUND((esq_2022 - esq_2010) / esq_2010 * 100, 1) AS variacao_pct
FROM v_esquerda_dep_federal
WHERE esq_2010 > 0
ORDER BY variacao_pct DESC;


-- ---------------------------------------------------------------------------
-- Q3: Contagem de zonas que cresceram vs caíram (vereador 2012→2024)
-- ---------------------------------------------------------------------------
SELECT
    CASE WHEN esq_2024 > esq_2012 THEN 'cresceu' ELSE 'caiu' END AS tendencia,
    COUNT(*) AS zonas
FROM v_esquerda_vereador
WHERE esq_2012 > 0
GROUP BY tendencia;


-- ---------------------------------------------------------------------------
-- Q4: Contagem de zonas que cresceram vs caíram (dep federal 2010→2022)
-- ---------------------------------------------------------------------------
SELECT
    CASE WHEN esq_2022 > esq_2010 THEN 'cresceu' ELSE 'caiu' END AS tendencia,
    COUNT(*) AS zonas
FROM v_esquerda_dep_federal
WHERE esq_2010 > 0
GROUP BY tendencia;


-- ---------------------------------------------------------------------------
-- Q5: Cruzamento — comportamento da zona nos dois níveis
-- Conceito: JOIN entre duas VIEWs + agregação por par de tendências
-- ---------------------------------------------------------------------------
SELECT
    CASE WHEN ver.esq_2024 > ver.esq_2012 THEN 'cresceu_ver' ELSE 'caiu_ver' END AS ver,
    CASE WHEN dep.esq_2022 > dep.esq_2010 THEN 'cresceu_dep' ELSE 'caiu_dep' END AS dep,
    COUNT(*) AS zonas
FROM v_esquerda_vereador ver
JOIN v_esquerda_dep_federal dep ON ver.nr_zona = dep.nr_zona
WHERE ver.esq_2012 > 0 AND dep.esq_2010 > 0
GROUP BY ver, dep
ORDER BY zonas DESC;


-- ---------------------------------------------------------------------------
-- Q6: Zonas que cresceram em AMBOS os níveis (zonas progressistas)
-- ---------------------------------------------------------------------------
SELECT
    ver.nr_zona,
    ver.esq_2012, ver.esq_2024,
    ROUND((ver.esq_2024 - ver.esq_2012) / ver.esq_2012 * 100, 1) AS var_ver_pct,
    dep.esq_2010, dep.esq_2022,
    ROUND((dep.esq_2022 - dep.esq_2010) / dep.esq_2010 * 100, 1) AS var_dep_pct
FROM v_esquerda_vereador ver
JOIN v_esquerda_dep_federal dep ON ver.nr_zona = dep.nr_zona
WHERE ver.esq_2024 > ver.esq_2012
  AND dep.esq_2022 > dep.esq_2010
  AND ver.esq_2012 > 0 AND dep.esq_2010 > 0
ORDER BY var_ver_pct DESC;
