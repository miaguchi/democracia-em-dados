from democracia_em_dados import ResultadoEleitoral

r = ResultadoEleitoral(
    codigo_ibge=3550308,
    nome_municipio="São Paulo",
    uf="SP",
    ano=2022,
    turno=1,
    votos_por_candidato={"LULA": 3000000, "BOLSONARO": 2500000}
)

print(r.total_votos)
print(r.vencedor)
print(r.numero_efetivo_candidatos())