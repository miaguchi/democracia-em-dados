import pandas as pd
import pytest

from src.dominio.local_votacao import classificar_local, filtrar_locais_cem


# ---------------------------------------------------------------------------
# classificar_local
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lv_tipo,nome,esperado", [
    # Educacionais claros
    ("EE", "FULANO DE TAL", "educacional"),
    ("EMEF", "ESCOLA X", "educacional"),
    ("EM", "ESCOLA Y", "educacional"),
    ("EMEI", "CRIANCA FELIZ", "educacional"),
    ("FAC", "ANHANGUERA", "educacional"),
    ("UNIV", "USP", "educacional"),
    ("ETEC", "JORGE STREET", "educacional"),
    ("COLEGIO", "SAO BENTO", "educacional"),
    # Sistema S = educacional
    ("SESI", "SESI VILA LEOPOLDINA", "educacional"),
    ("SENAI", "SENAI BRAS", "educacional"),
    ("SENAC", "SENAC CENTRO", "educacional"),
    ("SEBRAE", "SEBRAE SP", "educacional"),
    # CEU com escola = educacional
    ("CEU EMEF", "CEU EMEF JAGUARE", "educacional"),
    ("CEU EMEI", "CEU EMEI PAZ", "educacional"),
    ("CEU CEI", "CEU CEI SABIA", "educacional"),
    ("CEU CEE", "CEU CEE X", "educacional"),
    # APAE, EJA, CEEJA = educacional
    ("APAE", "APAE CAMPINAS", "educacional"),
    ("EJA", "EJA CENTRO", "educacional"),
    ("CEEJA", "CEEJA SP", "educacional"),
    # INST e ASSOC ED = educacional
    ("INST", "FEDERAL DE SAO PAULO", "educacional"),
    ("ASSOC ED", "EUGENIO MONTALE", "educacional"),
    # FUND educacional (nome genérico, não é lar)
    ("FUND", "FUNDACAO EDUCACIONAL DE SAO CARLOS", "educacional"),
    # Não-educacionais claros
    ("CDP", "CDP PINHEIROS", "nao_educacional"),
    ("PENIT", "PENITENCIARIA FEMININA", "nao_educacional"),
    ("FUND CASA", "FUND CASA FRANCO DA ROCHA", "nao_educacional"),
    ("CPP", "CPP PACAEMBU", "nao_educacional"),
    ("POSTO SAUDE", "UBS JARDIM SAO LUIZ", "nao_educacional"),
    ("UBS", "UBS CENTRO", "nao_educacional"),
    ("IGREJA", "IGREJA METODISTA", "nao_educacional"),
    ("PASTORAL", "PASTORAL DA CRIANCA", "nao_educacional"),
    ("ASSOC", "ASSOC MORADORES", "nao_educacional"),
    ("ASSOC CULT", "ASSOC CULTURAL NIPONICA", "nao_educacional"),
    ("CLUBE", "CLUBE MUNICIPAL", "nao_educacional"),
    ("CLUBE ATL", "CLUBE ATLETICO X", "nao_educacional"),
    ("CDC", "CDC IBIRAPUERA", "nao_educacional"),
    ("CREAS", "CREAS LAPA", "nao_educacional"),
    ("CCA", "CCA CENTRO", "nao_educacional"),
    ("SECRETARIA", "SECRETARIA MUNICIPAL", "nao_educacional"),
    ("ESP CULT", "ESPACO CULTURAL X", "nao_educacional"),
    ("BIBLI", "BIBLIOTECA MUNICIPAL", "nao_educacional"),
    ("GURI", "GURI SANTA MARCELINA", "nao_educacional"),
    ("EQUIP PUB", "GINASIO MUNICIPAL", "nao_educacional"),
    ("AUTARQUIA", "SUBPREFEITURA X", "nao_educacional"),
    ("BAIRRO", "CANGUME", "nao_educacional"),
    ("ASSENT", "BOM PASTOR", "nao_educacional"),
    ("NUCLEO", "CORACAO MATERNO", "nao_educacional"),
    ("CEU", "CEU BUTANTA", "nao_educacional"),
    ("COOP", "COOP AGRICOLA", "nao_educacional"),
    ("ASSIST SOC", "ASSIST SOCIAL X", "nao_educacional"),
    # FUND com nome de lar = não-educacional
    ("FUND", "LAR ANALIA FRANCO", "nao_educacional"),
    ("FUND", "LAR MONSENHOR FILIPPO", "nao_educacional"),
])
def test_classificar_local(lv_tipo, nome, esperado):
    assert classificar_local(lv_tipo, nome) == esperado


# ---------------------------------------------------------------------------
# filtrar_locais_cem
# ---------------------------------------------------------------------------

@pytest.fixture
def gdf_exemplo():
    """GeoDataFrame mínimo simulando estrutura da base CEM."""
    return pd.DataFrame({
        "LV_TIPO": ["EE", "EMEF", "CDP", "IGREJA", "CEU", "CEU EMEF",
                     "SESI", "FUND", "FUND"],
        "NOME_LV": ["FULANO", "BELTRANO", "CDP X", "METODISTA", "CEU Y",
                     "CEU EMEF Z", "SESI W", "FUNDACAO EDUCACIONAL",
                     "LAR ANALIA FRANCO"],
    })


def test_filtrar_retorna_dois_dataframes(gdf_exemplo):
    educ, nao_educ = filtrar_locais_cem(gdf_exemplo)
    assert len(educ) + len(nao_educ) == len(gdf_exemplo)


def test_filtrar_classifica_corretamente(gdf_exemplo):
    educ, nao_educ = filtrar_locais_cem(gdf_exemplo)
    # educ: EE, EMEF, CEU EMEF, SESI, FUND(educacional) = 5
    # nao_educ: CDP, IGREJA, CEU(puro), FUND(LAR) = 4
    assert len(educ) == 5
    assert len(nao_educ) == 4


def test_filtrar_adiciona_coluna_classificacao(gdf_exemplo):
    educ, nao_educ = filtrar_locais_cem(gdf_exemplo)
    assert (educ["classificacao"] == "educacional").all()
    assert (nao_educ["classificacao"] == "nao_educacional").all()
