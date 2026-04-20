Use democracia_em_dados;
show tables;

SELECT nr_zona,
       SUM(CASE WHEN cd_eleicao = 426 THEN qt_votos_nominais ELSE 0 END) as votos_2020,
       SUM(CASE WHEN cd_eleicao = 619 THEN qt_votos_nominais ELSE 0 END) as votos_2024
FROM votacao_partido_munzona
WHERE nr_partido = 13 AND cd_cargo = 13 AND cd_eleicao IN (426, 619)
GROUP BY nr_zona
ORDER BY votos_2024 DESC;


select * from (select nr_zona, 
    SUM(CASE WHEN nr_partido = 13 THEN qt_votos_nominais ELSE 0 END) as votos_PT,
    SUM(CASE WHEN nr_partido = 50 then qt_votos_nominais else 0 end) as votos_psol
from votacao_partido_munzona
where nr_partido in (13,50) and cd_eleicao = 619 and cd_cargo =13
group by nr_zona 
order by votos_PSOL desc ) as resultado
where votos_psol > votos_pt

SELECT cd_eleicao, ds_eleicao FROM eleicao WHERE ano_eleicao = 2024;

SELECT nr_partido, COUNT(*) as vezes_lider FROM (
    SELECT nr_zona, nr_partido, SUM(qt_votos_nominais) as total_votos,
           ROW_NUMBER() OVER (PARTITION BY nr_zona ORDER BY SUM(qt_votos_nominais) DESC) as ranking
    FROM votacao_partido_munzona
    WHERE cd_eleicao = 619 AND cd_cargo = 13
    GROUP BY nr_zona, nr_partido
) as resultado
WHERE ranking = 1
GROUP BY nr_partido
ORDER BY vezes_lider DESC;

    