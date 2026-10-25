-- =====================================================================
-- KPIs de acidentes nas rodovias federais - PRF 2025
-- Banco: SQLite | Tabela: acidentes (uma linha por acidente)
-- Cada consulta começa com "-- name: <nome>" para o script 03 executar.
-- Definição de letalidade usada em todo o projeto:
--   mortos_por_100_acidentes = 100.0 * SUM(mortos) / COUNT(*)
-- Atenção: não há dados de volume de tráfego. Os rankings mostram onde
-- há MAIS acidentes e mortes, não necessariamente a via mais perigosa.
-- =====================================================================

-- name: 01_visao_geral
SELECT
    COUNT(*)                                              AS acidentes,
    SUM(mortos)                                           AS mortos,
    SUM(feridos)                                          AS feridos,
    SUM(classificacao_acidente = 'Com Vítimas Fatais')    AS acidentes_fatais,
    ROUND(100.0 * SUM(classificacao_acidente = 'Com Vítimas Fatais') / COUNT(*), 1) AS pct_acidentes_fatais,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)              AS mortos_por_100_acidentes
FROM acidentes;

-- name: 02_por_uf
SELECT
    uf,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes,
    RANK() OVER (ORDER BY SUM(mortos) DESC)    AS ranking_mortos
FROM acidentes
GROUP BY uf
ORDER BY mortos DESC;

-- name: 03_top_trechos_br_uf
-- Combinação BR + UF, só com pelo menos 300 acidentes para a taxa ser confiável.
SELECT
    br, uf,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
WHERE br IS NOT NULL
GROUP BY br, uf
HAVING COUNT(*) >= 300
ORDER BY mortos DESC
LIMIT 10;

-- name: 04_por_hora
SELECT
    hora,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY hora
ORDER BY hora;

-- name: 05_por_dia_semana
SELECT
    dia_semana,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY dia_semana
ORDER BY CASE dia_semana
    WHEN 'Segunda-feira' THEN 1 WHEN 'Terça-feira' THEN 2 WHEN 'Quarta-feira' THEN 3
    WHEN 'Quinta-feira' THEN 4 WHEN 'Sexta-feira' THEN 5 WHEN 'Sábado' THEN 6 ELSE 7 END;

-- name: 06_por_fase_do_dia
SELECT
    fase_dia,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY fase_dia
ORDER BY mortos_por_100_acidentes DESC;

-- name: 07_top_causas
SELECT
    causa_acidente,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM acidentes), 1) AS pct_do_total
FROM acidentes
GROUP BY causa_acidente
HAVING COUNT(*) >= 500
ORDER BY acidentes DESC
LIMIT 10;

-- name: 08_causas_mais_letais
-- Causas com poucos casos distorcem a taxa, por isso o filtro de volume mínimo.
SELECT
    causa_acidente,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY causa_acidente
HAVING COUNT(*) >= 500
ORDER BY mortos_por_100_acidentes DESC
LIMIT 10;

-- name: 09_por_tipo_de_acidente
SELECT
    tipo_acidente,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY tipo_acidente
HAVING COUNT(*) >= 500
ORDER BY mortos_por_100_acidentes DESC;

-- name: 10_por_clima
SELECT
    grupo_clima,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
GROUP BY grupo_clima
ORDER BY acidentes DESC;

-- name: 11_evolucao_mensal
-- LAG compara cada mês com o anterior.
WITH mensal AS (
    SELECT mes, COUNT(*) AS acidentes, SUM(mortos) AS mortos
    FROM acidentes
    GROUP BY mes
)
SELECT
    mes, acidentes, mortos,
    ROUND(100.0 * (acidentes - LAG(acidentes) OVER (ORDER BY mes))
          / LAG(acidentes) OVER (ORDER BY mes), 1) AS var_pct_acidentes_mes_anterior
FROM mensal
ORDER BY mes;

-- name: 12_sp_top_municipios
SELECT
    municipio,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos,
    ROUND(100.0 * SUM(mortos) / COUNT(*), 1)   AS mortos_por_100_acidentes
FROM acidentes
WHERE uf = 'SP'
GROUP BY municipio
ORDER BY acidentes DESC
LIMIT 10;

-- name: 13_sp_top_causas
SELECT
    causa_acidente,
    COUNT(*)                                   AS acidentes,
    SUM(mortos)                                AS mortos
FROM acidentes
WHERE uf = 'SP'
GROUP BY causa_acidente
ORDER BY acidentes DESC
LIMIT 5;

-- name: 14_alcool_por_dia_semana
-- Acidentes por ingestão de álcool e peso no total de cada dia.
SELECT
    dia_semana,
    SUM(causa_acidente = 'Ingestão de álcool pelo condutor')   AS acidentes_alcool,
    COUNT(*)                                                   AS acidentes_total,
    ROUND(100.0 * SUM(causa_acidente = 'Ingestão de álcool pelo condutor') / COUNT(*), 1) AS pct_alcool
FROM acidentes
GROUP BY dia_semana
ORDER BY pct_alcool DESC;

-- name: 15_checagem_totais
-- Verificação: somar as partes deve dar o total geral.
SELECT
    (SELECT COUNT(*) FROM acidentes)                                   AS total_acidentes,
    (SELECT SUM(a) FROM (SELECT COUNT(*) a FROM acidentes GROUP BY uf))   AS soma_uf,
    (SELECT SUM(a) FROM (SELECT COUNT(*) a FROM acidentes GROUP BY hora)) AS soma_hora,
    (SELECT SUM(a) FROM (SELECT COUNT(*) a FROM acidentes GROUP BY grupo_clima)) AS soma_clima;
