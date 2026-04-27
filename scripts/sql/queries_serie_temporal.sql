-- =============================================================================
-- Série temporal — voto de esquerda em SP, 1998-2024
-- Banco: democracia_em_dados (MySQL)
-- =============================================================================
-- Códigos de partidos (escala Bolognesi, Ribeiro & Codato 2023 — esquerda):
--   13 = PT
--   50 = PSOL
--   65 = PCdoB
--   12 = PDT
--   40 = PSB
--   43 = PV
--   18 = REDE
--   16 = PSTU
--   29 = PCO
--   80 = UP
--
-- Cargos:
--   6  = Deputado Federal
--   13 = Vereador
-- =============================================================================


-- ---------------------------------------------------------------------------
-- Q1: Série temporal PT+PSOL para vereador (2012-2024)
-- Conceito: filtro por subset de partidos + agregação anual
-- ---------------------------------------------------------------------------
SELECT
    e.ano_eleicao,
    SUM(v.qt_votos_nominais) AS votos_nominais,
    SUM(v.qt_votos_legenda)  AS votos_legenda,
    SUM(v.qt_votos_nominais + v.qt_votos_legenda) AS total_votos
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50)        -- PT e PSOL
  AND v.cd_cargo = 13                  -- Vereador
  AND e.nr_turno = 1
  AND e.ano_eleicao IN (2012, 2016, 2020, 2024)
GROUP BY e.ano_eleicao
ORDER BY e.ano_eleicao;


-- ---------------------------------------------------------------------------
-- Q2: Série temporal esquerda completa (Bolognesi) — vereador (2000-2024)
-- Conceito: agregação por ciclo eleitoral municipal
-- ---------------------------------------------------------------------------
SELECT
    e.ano_eleicao,
    SUM(v.qt_votos_nominais) AS total_nominais
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)
  AND v.cd_cargo = 13                  -- Vereador
  AND e.nr_turno = 1
GROUP BY e.ano_eleicao
ORDER BY e.ano_eleicao;


-- ---------------------------------------------------------------------------
-- Q3: Série temporal esquerda completa — deputado federal (1998-2022)
-- Conceito: agregação por ciclo eleitoral federal (anos pares não-municipais)
-- ---------------------------------------------------------------------------
SELECT
    e.ano_eleicao,
    SUM(v.qt_votos_nominais) AS total_nominais
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50, 65, 12, 40, 43, 18, 16, 29, 80)
  AND v.cd_cargo = 6                   -- Deputado Federal
  AND e.nr_turno = 1
GROUP BY e.ano_eleicao
ORDER BY e.ano_eleicao;


-- ---------------------------------------------------------------------------
-- Q4: Comparação PT vs PSOL por zona — vereador SP capital, 2024
-- Conceito: pivot manual com SUM + CASE WHEN para criar colunas por partido
-- ---------------------------------------------------------------------------
SELECT
    v.nr_zona,
    SUM(CASE WHEN v.nr_partido = 13 THEN v.qt_votos_nominais ELSE 0 END) AS votos_pt,
    SUM(CASE WHEN v.nr_partido = 50 THEN v.qt_votos_nominais ELSE 0 END) AS votos_psol,
    SUM(CASE WHEN v.nr_partido = 13 THEN v.qt_votos_nominais ELSE 0 END)
        + SUM(CASE WHEN v.nr_partido = 50 THEN v.qt_votos_nominais ELSE 0 END) AS soma
FROM votacao_partido_munzona v
JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
WHERE v.nr_partido IN (13, 50)
  AND v.cd_cargo = 13
  AND v.cd_municipio = 71072            -- São Paulo capital
  AND e.ano_eleicao = 2024
  AND e.nr_turno = 1
GROUP BY v.nr_zona
ORDER BY soma DESC;


-- ---------------------------------------------------------------------------
-- Q5: Zonas onde PSOL supera PT — vereador SP capital, 2024
-- Conceito: subquery + filtro pós-agregação (HAVING via outer query)
-- ---------------------------------------------------------------------------
SELECT * FROM (
    SELECT
        v.nr_zona,
        SUM(CASE WHEN v.nr_partido = 13 THEN v.qt_votos_nominais ELSE 0 END) AS votos_pt,
        SUM(CASE WHEN v.nr_partido = 50 THEN v.qt_votos_nominais ELSE 0 END) AS votos_psol
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido IN (13, 50)
      AND v.cd_cargo = 13
      AND v.cd_municipio = 71072
      AND e.ano_eleicao = 2024
      AND e.nr_turno = 1
    GROUP BY v.nr_zona
) AS comparativo
WHERE votos_psol > votos_pt
ORDER BY (votos_psol - votos_pt) DESC;
