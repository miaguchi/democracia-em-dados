import pytest
from democracia_em_dados import ResultadoEleitoral


@pytest.fixture
def resultado_basico():
    return ResultadoEleitoral(
        codigo_ibge=3550308,
        nome_municipio="São Paulo",
        uf="SP",
        ano=2022,
        turno=1,
        votos_por_candidato={"LULA": 3_000_000, "BOLSONARO": 2_500_000},
    )


@pytest.fixture
def resultado_empate():
    return ResultadoEleitoral(
        codigo_ibge=3550308,
        nome_municipio="São Paulo",
        uf="SP",
        ano=2022,
        turno=1,
        votos_por_candidato={"A": 1000, "B": 1000},
    )


def test_total_votos(resultado_basico):
    assert resultado_basico.total_votos == 5_500_000


def test_vencedor_claro(resultado_basico):
    assert resultado_basico.vencedor == "LULA"


def test_vencedor_empate_retorna_none(resultado_empate):
    assert resultado_empate.vencedor is None


def test_percentual_de_candidato(resultado_basico):
    pct = resultado_basico.percentual_de("LULA")
    assert pct == pytest.approx(3_000_000 / 5_500_000)


def test_margem_de_vitoria(resultado_basico):
    margem_esperada = (3_000_000 - 2_500_000) / 5_500_000
    assert resultado_basico.margem_de_vitoria() == pytest.approx(margem_esperada)


def test_nec_dois_candidatos_iguais(resultado_empate):
    assert resultado_empate.numero_efetivo_candidatos() == pytest.approx(2.0)


def test_uf_invalida():
    with pytest.raises(ValueError, match="UF inválida"):
        ResultadoEleitoral(3550308, "X", "XX", 2022, 1, {"A": 100})


def test_turno_invalido():
    with pytest.raises(ValueError, match="turno deve ser 1 ou 2"):
        ResultadoEleitoral(3550308, "X", "SP", 2022, 3, {"A": 100})


def test_codigo_ibge_nao_inteiro():
    with pytest.raises(TypeError):
        ResultadoEleitoral("3550308", "X", "SP", 2022, 1, {"A": 100})


def test_ano_impar():
    with pytest.raises(ValueError, match="ano deve ser par"):
        ResultadoEleitoral(3550308, "X", "SP", 2023, 1, {"A": 100})


def test_votos_negativos():
    with pytest.raises(ValueError, match="votos.*inválidos"):
        ResultadoEleitoral(3550308, "X", "SP", 2022, 1, {"A": -1})


def test_nome_candidato_vazio():
    with pytest.raises(ValueError, match="nome de candidato inválido"):
        ResultadoEleitoral(3550308, "X", "SP", 2022, 1, {"": 100})


def test_total_votos_vazio():
    r = ResultadoEleitoral(3550308, "X", "SP", 2022, 1, {})
    assert r.total_votos == 0


def test_percentual_candidato_inexistente(resultado_basico):
    assert resultado_basico.percentual_de("CIRO") == 0.0


def test_margem_candidato_unico():
    r = ResultadoEleitoral(3550308, "X", "SP", 2022, 1, {"A": 1000})
    assert r.margem_de_vitoria() == 1.0