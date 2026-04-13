import pytest

from src.dominio import Candidato, EleicaoMunicipal, ResultadoEleitoral


@pytest.fixture
def candidatos_2022():
    return [
        Candidato(nome="LULA", partido="PT", uf="SP", genero="M"),
        Candidato(nome="BOLSONARO", partido="PL", uf="SP", genero="M"),
        Candidato(nome="CIRO", partido="PDT", uf="SP", genero="M"),
    ]


@pytest.fixture
def resultado_2022():
    return ResultadoEleitoral(
        codigo_ibge=3550308,
        nome_municipio="São Paulo",
        uf="SP",
        ano=2022,
        turno=1,
        votos_por_candidato={"LULA": 3_000_000, "BOLSONARO": 2_500_000, "CIRO": 500_000},
    )


@pytest.fixture
def eleicao_2022(candidatos_2022, resultado_2022):
    return EleicaoMunicipal(candidatos=candidatos_2022, resultado=resultado_2022)


def test_votos_por_partido(eleicao_2022):
    assert eleicao_2022.votos_por_partido == {
        "PT": 3_000_000,
        "PL": 2_500_000,
        "PDT": 500_000,
    }


def test_nep_tres_partidos(eleicao_2022):
    total = 6_000_000
    p = [3_000_000 / total, 2_500_000 / total, 500_000 / total]
    esperado = 1 / sum(x ** 2 for x in p)
    assert eleicao_2022.numero_efetivo_partidos == pytest.approx(esperado)


def test_fragmentacao_entre_zero_e_um(eleicao_2022):
    frag = eleicao_2022.fragmentacao
    assert 0 < frag < 1


def test_candidatos_deve_ser_lista_nao_vazia(resultado_2022):
    with pytest.raises(ValueError, match="lista não vazia"):
        EleicaoMunicipal(candidatos=[], resultado=resultado_2022)


def test_resultado_com_nome_nao_cadastrado(candidatos_2022):
    resultado = ResultadoEleitoral(
        codigo_ibge=3550308,
        nome_municipio="São Paulo",
        uf="SP",
        ano=2022,
        turno=1,
        votos_por_candidato={"LULA": 1000, "FANTASMA": 500},
    )
    with pytest.raises(ValueError, match="não cadastrados"):
        EleicaoMunicipal(candidatos=candidatos_2022, resultado=resultado)


def test_volatilidade_pedersen():
    cands = [
        Candidato(nome="A", partido="PT", uf="SP"),
        Candidato(nome="B", partido="PL", uf="SP"),
    ]
    r1 = ResultadoEleitoral(3550308, "São Paulo", "SP", 2018, 1, {"A": 600, "B": 400})
    r2 = ResultadoEleitoral(3550308, "São Paulo", "SP", 2022, 1, {"A": 400, "B": 600})
    e1 = EleicaoMunicipal(cands, r1)
    e2 = EleicaoMunicipal(cands, r2)
    assert e2.volatilidade_vs(e1) == pytest.approx(0.2)


def test_volatilidade_mesmo_resultado_eh_zero(eleicao_2022):
    assert eleicao_2022.volatilidade_vs(eleicao_2022) == pytest.approx(0.0)


def test_volatilidade_municipios_diferentes(eleicao_2022, candidatos_2022):
    r_outro = ResultadoEleitoral(
        codigo_ibge=3304557,
        nome_municipio="Rio",
        uf="RJ",
        ano=2022,
        turno=1,
        votos_por_candidato={"LULA": 1000, "BOLSONARO": 1000, "CIRO": 1000},
    )
    cands_rj = [
        Candidato(nome="LULA", partido="PT", uf="RJ"),
        Candidato(nome="BOLSONARO", partido="PL", uf="RJ"),
        Candidato(nome="CIRO", partido="PDT", uf="RJ"),
    ]
    outra = EleicaoMunicipal(cands_rj, r_outro)
    with pytest.raises(ValueError, match="mesmo município"):
        eleicao_2022.volatilidade_vs(outra)
