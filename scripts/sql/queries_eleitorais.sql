-- =============================================================================
-- 5 queries progressivas sobre dados eleitorais do TSE
-- Banco: democracia_em_dados
-- Projeto: Democracia em Dados
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Q1: Total de votos por partido em SP capital, 2024, vereador (1º turno)
-- Conceito: JOIN simples entre tabela fato e dimensão
-- ---------------------------------------------------------------------------
SELECT
    p.sg_partido,
    p.nm_partido,
    SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS total_votos
FROM votacao_partido_munzona v
JOIN partido p ON v.nr_partido = p.nr_partido
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE e.ano_eleicao = 2024
  AND e.nr_turno = 1
  AND v.cd_cargo = 13                -- Vereador
  AND v.cd_municipio = 71072         -- São Paulo (código TSE)
GROUP BY p.sg_partido, p.nm_partido
ORDER BY total_votos DESC;


-- ---------------------------------------------------------------------------
-- Q2: Votos médios por zona eleitoral e partido, SP 2024 vereador
-- Conceito: GROUP BY com múltiplas dimensões + AVG
-- ---------------------------------------------------------------------------
SELECT
    v.nr_zona,
    p.sg_partido,
    AVG(v.qt_votos_nominais + v.qt_votos_legenda) AS media_votos,
    SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS total_votos,
    COUNT(*) AS n_registros
FROM votacao_partido_munzona v
JOIN partido p ON v.nr_partido = p.nr_partido
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE e.ano_eleicao = 2024
  AND e.nr_turno = 1
  AND v.cd_cargo = 13
  AND v.cd_municipio = 71072
GROUP BY v.nr_zona, p.sg_partido
HAVING total_votos > 1000
ORDER BY v.nr_zona, total_votos DESC;


-- ---------------------------------------------------------------------------
-- Q3: Ranking de partidos por zona eleitoral (SP 2024, vereador)
-- Conceito: window function ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)
-- ---------------------------------------------------------------------------
WITH votos_zona AS (
    SELECT
        v.nr_zona,
        p.sg_partido,
        SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS total_votos
    FROM votacao_partido_munzona v
    JOIN partido p ON v.nr_partido = p.nr_partido
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE e.ano_eleicao = 2024
      AND e.nr_turno = 1
      AND v.cd_cargo = 13
      AND v.cd_municipio = 71072
    GROUP BY v.nr_zona, p.sg_partido
)
SELECT
    nr_zona,
    sg_partido,
    total_votos,
    ROW_NUMBER() OVER (PARTITION BY nr_zona ORDER BY total_votos DESC) AS ranking
FROM votos_zona
HAVING ranking <= 3
ORDER BY nr_zona, ranking;


-- ---------------------------------------------------------------------------
-- Q4: Zonas onde o partido mais votado mudou entre 2020 e 2024 (vereador)
-- Conceito: CTE encadeada + self-join para comparação temporal
-- ---------------------------------------------------------------------------
WITH votos_por_ano AS (
    SELECT
        e.ano_eleicao,
        v.nr_zona,
        p.sg_partido,
        SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS total_votos
    FROM votacao_partido_munzona v
    JOIN partido p ON v.nr_partido = p.nr_partido
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE e.ano_eleicao IN (2020, 2024)
      AND e.nr_turno = 1
      AND v.cd_cargo = 13
      AND v.cd_municipio = 71072
    GROUP BY e.ano_eleicao, v.nr_zona, p.sg_partido
),
ranking AS (
    SELECT
        ano_eleicao,
        nr_zona,
        sg_partido,
        total_votos,
        ROW_NUMBER() OVER (
            PARTITION BY ano_eleicao, nr_zona
            ORDER BY total_votos DESC
        ) AS pos
    FROM votos_por_ano
),
lider_2020 AS (
    SELECT nr_zona, sg_partido AS partido_2020
    FROM ranking WHERE ano_eleicao = 2020 AND pos = 1
),
lider_2024 AS (
    SELECT nr_zona, sg_partido AS partido_2024
    FROM ranking WHERE ano_eleicao = 2024 AND pos = 1
)
SELECT
    l20.nr_zona,
    l20.partido_2020,
    l24.partido_2024,
    CASE WHEN l20.partido_2020 != l24.partido_2024
         THEN 'MUDOU' ELSE 'MANTEVE' END AS status
FROM lider_2020 l20
JOIN lider_2024 l24 ON l20.nr_zona = l24.nr_zona
ORDER BY status DESC, l20.nr_zona;


-- ---------------------------------------------------------------------------
-- Q5: Partido com maior crescimento percentual por zona (2020→2024, vereador)
-- Conceito: subquery correlacionada + cálculo de variação percentual
-- ---------------------------------------------------------------------------
WITH votos_2020 AS (
    SELECT
        v.nr_zona,
        p.sg_partido,
        SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS votos
    FROM votacao_partido_munzona v
    JOIN partido p ON v.nr_partido = p.nr_partido
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE e.ano_eleicao = 2020 AND e.nr_turno = 1
      AND v.cd_cargo = 13 AND v.cd_municipio = 71072
    GROUP BY v.nr_zona, p.sg_partido
    HAVING votos >= 100       -- mínimo para evitar distorção percentual
),
votos_2024 AS (
    SELECT
        v.nr_zona,
        p.sg_partido,
        SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS votos
    FROM votacao_partido_munzona v
    JOIN partido p ON v.nr_partido = p.nr_partido
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE e.ano_eleicao = 2024 AND e.nr_turno = 1
      AND v.cd_cargo = 13 AND v.cd_municipio = 71072
    GROUP BY v.nr_zona, p.sg_partido
),
crescimento AS (
    SELECT
        v24.nr_zona,
        v24.sg_partido,
        v20.votos AS votos_2020,
        v24.votos AS votos_2024,
        ROUND((v24.votos - v20.votos) / v20.votos * 100, 1) AS pct_crescimento
    FROM votos_2024 v24
    JOIN votos_2020 v20
        ON v24.nr_zona = v20.nr_zona
        AND v24.sg_partido = v20.sg_partido
),
ranking AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY nr_zona
            ORDER BY pct_crescimento DESC
        ) AS pos
    FROM crescimento
)
SELECT
    nr_zona,
    sg_partido,
    votos_2020,
    votos_2024,
    pct_crescimento
FROM ranking
WHERE pos = 1
ORDER BY pct_crescimento DESC;
