"""Testes offline: constroem um zip fake com CSV no formato TSE."""

import zipfile

import pandas as pd
import pytest

from src.ingestao.tse_downloader import TSEDownloader


@pytest.fixture
def downloader(tmp_path):
    return TSEDownloader(
        raw_dir=tmp_path / "raw",
        processed_dir=tmp_path / "processed",
    )


@pytest.fixture
def zip_fake(tmp_path):
    csv_sp = tmp_path / "votacao_SP.csv"
    csv_sp.write_text(
        "ANO;UF;MUNICIPIO;VOTOS\n"
        "2022;SP;São Paulo;3000000\n"
        "2022;SP;Campinas;500000\n",
        encoding="latin-1",
    )
    csv_rj = tmp_path / "votacao_RJ.csv"
    csv_rj.write_text(
        "ANO;UF;MUNICIPIO;VOTOS\n"
        "2022;RJ;Rio;1000000\n",
        encoding="latin-1",
    )
    zip_path = tmp_path / "votacao_partido_munzona_2022.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(csv_sp, arcname="votacao_SP.csv")
        zf.write(csv_rj, arcname="votacao_RJ.csv")
    return zip_path


def test_url_formata_corretamente(downloader):
    url = downloader.url("consulta_cand", 2022)
    assert url.endswith("/consulta_cand/consulta_cand_2022.zip")


def test_url_tipo_invalido(downloader):
    with pytest.raises(ValueError, match="tipo inválido"):
        downloader.url("inexistente", 2022)


def test_extract_cria_diretorio(downloader, zip_fake):
    extraido = downloader.extract(zip_fake)
    assert extraido.is_dir()
    assert (extraido / "votacao_SP.csv").exists()
    assert (extraido / "votacao_RJ.csv").exists()


def test_csv_to_parquet(downloader, zip_fake):
    extraido = downloader.extract(zip_fake)
    parquet = downloader.csv_to_parquet(extraido / "votacao_SP.csv")
    assert parquet.exists()
    df = pd.read_parquet(parquet)
    assert list(df.columns) == ["ANO", "UF", "MUNICIPIO", "VOTOS"]
    assert len(df) == 2
    assert df.loc[df["MUNICIPIO"] == "São Paulo", "VOTOS"].iloc[0] == 3_000_000


def test_download_usa_cache(downloader, monkeypatch, zip_fake):
    destino_esperado = downloader.raw_dir / "votacao_partido_munzona_2022.zip"
    destino_esperado.parent.mkdir(parents=True, exist_ok=True)
    destino_esperado.write_bytes(zip_fake.read_bytes())

    def _falha(*args, **kwargs):
        raise AssertionError("não deveria chamar a rede")

    monkeypatch.setattr("requests.get", _falha)
    resultado = downloader.download("votacao_partido_munzona", 2022)
    assert resultado == destino_esperado


def test_ingerir_filtra_por_uf(downloader, monkeypatch, zip_fake):
    destino = downloader.raw_dir / "votacao_partido_munzona_2022.zip"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(zip_fake.read_bytes())
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("offline")),
    )
    parquets = downloader.ingerir("votacao_partido_munzona", 2022, uf="SP")
    assert len(parquets) == 1
    assert "SP" in parquets[0].name
