"""Ingestão de dados do TSE (CDN de dados abertos)."""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Dict

import pandas as pd
import requests


class TSEDownloader:
    BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

    TIPOS: Dict[str, str] = {
        "votacao_partido_munzona": "votacao_partido_munzona/votacao_partido_munzona_{ano}.zip",
        "consulta_cand": "consulta_cand/consulta_cand_{ano}.zip",
    }

    CSV_ENCODING = "latin-1"
    CSV_SEP = ";"

    def __init__(self, raw_dir: Path, processed_dir: Path) -> None:
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def url(self, tipo: str, ano: int) -> str:
        if tipo not in self.TIPOS:
            raise ValueError(
                f"tipo inválido: {tipo!r}. Válidos: {sorted(self.TIPOS)}"
            )
        return f"{self.BASE_URL}/{self.TIPOS[tipo].format(ano=ano)}"

    def download(self, tipo: str, ano: int, *, force: bool = False) -> Path:
        destino = self.raw_dir / f"{tipo}_{ano}.zip"
        if destino.exists() and not force:
            return destino
        resposta = requests.get(self.url(tipo, ano), stream=True, timeout=60)
        resposta.raise_for_status()
        with destino.open("wb") as f:
            for chunk in resposta.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return destino

    def extract(self, zip_path: Path) -> Path:
        zip_path = Path(zip_path)
        destino = self.raw_dir / zip_path.stem
        destino.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(destino)
        return destino

    def csv_to_parquet(
        self, csv_path: Path, parquet_path: Path | None = None
    ) -> Path:
        csv_path = Path(csv_path)
        if parquet_path is None:
            parquet_path = self.processed_dir / f"{csv_path.stem}.parquet"
        df = pd.read_csv(
            csv_path,
            sep=self.CSV_SEP,
            encoding=self.CSV_ENCODING,
            low_memory=False,
        )
        df.to_parquet(parquet_path, index=False)
        return parquet_path

    def ingerir(self, tipo: str, ano: int, uf: str | None = None) -> list[Path]:
        zip_path = self.download(tipo, ano)
        extraido = self.extract(zip_path)
        alvos = sorted(extraido.glob("*.csv"))
        if uf is not None:
            alvos = [p for p in alvos if f"_{uf.upper()}" in p.name.upper()]
        return [self.csv_to_parquet(p) for p in alvos]
