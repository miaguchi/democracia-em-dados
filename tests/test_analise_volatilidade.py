"""Testes do módulo de análise de volatilidade (Pedersen + normalização)."""

import pandas as pd
import pytest

from src.partidario.analise_volatilidade import (
    normalizar_partido,
    pedersen,
    pedersen_por_zona,
)


class TestNormalizarPartido:
    def test_partido_comum_nao_muda(self):
        assert normalizar_partido("MDB") == "MDB"
        assert normalizar_partido("PSB") == "PSB"

    def test_membros_da_federacao_pt_viram_rotulo_unico(self):
        assert normalizar_partido("PT") == "FED_PT_PCDOB_PV"
        assert normalizar_partido("PC do B") == "FED_PT_PCDOB_PV"
        assert normalizar_partido("PV") == "FED_PT_PCDOB_PV"

    def test_fusao_uniao_brasil(self):
        assert normalizar_partido("DEM") == "UNIÃO"
        assert normalizar_partido("PSL") == "UNIÃO"

    def test_fusao_prd(self):
        assert normalizar_partido("PATRIOTA") == "PRD"
        assert normalizar_partido("PTB") == "PRD"


class TestPedersen:
    def test_mesmos_votos_volatilidade_zero(self):
        s = pd.Series({"A": 100, "B": 50, "C": 25})
        assert pedersen(s, s) == pytest.approx(0.0)

    def test_troca_total_volatilidade_um(self):
        ant = pd.Series({"A": 100})
        atu = pd.Series({"B": 100})
        assert pedersen(ant, atu) == pytest.approx(1.0)

    def test_entre_zero_e_um(self):
        ant = pd.Series({"A": 60, "B": 40})
        atu = pd.Series({"A": 40, "B": 60})
        # |0.6-0.4| + |0.4-0.6| = 0.4; /2 = 0.2
        assert pedersen(ant, atu) == pytest.approx(0.2)

    def test_partido_novo_conta_como_mudanca(self):
        ant = pd.Series({"A": 100})
        atu = pd.Series({"A": 50, "B": 50})
        # |1.0-0.5| + |0-0.5| = 1.0; /2 = 0.5
        assert pedersen(ant, atu) == pytest.approx(0.5)


class TestPedersenPorZona:
    def test_zonas_apenas_em_interseccao(self):
        # Zona 1 só existe em ant, zona 3 só em atu, zona 2 nos dois.
        ant = pd.DataFrame({"A": [100, 80], "B": [0, 20]}, index=[1, 2])
        atu = pd.DataFrame({"A": [100, 80], "B": [0, 20]}, index=[2, 3])
        resultado = pedersen_por_zona(ant, atu)
        assert list(resultado.index) == [2]
        # Zona 2 em ant: A=80, B=20 (80%/20%). Em atu: A=100, B=0 (100%/0%).
        # Pedersen = 0.5 * (|0.8-1.0| + |0.2-0|) = 0.2
        assert resultado.iloc[0] == pytest.approx(0.2)

    def test_sinal_bate_com_pedersen_global_para_zona_unica(self):
        ant = pd.DataFrame({"A": [60], "B": [40]}, index=[1])
        atu = pd.DataFrame({"A": [40], "B": [60]}, index=[1])
        resultado = pedersen_por_zona(ant, atu)
        assert resultado.iloc[0] == pytest.approx(0.2)
