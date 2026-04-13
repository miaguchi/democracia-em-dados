from pathlib import Path
from src.ingestao.tse_downloader import TSEDownloader

Path("data/raw/votacao_secao_2020_SP.zip").unlink(missing_ok=True)  # zip truncado anterior

d = TSEDownloader(raw_dir=Path("data/raw"), processed_dir=Path("data/processed"))
p2020 = d.ingerir("votacao_secao", 2020, uf="SP")
p2024 = d.ingerir("votacao_secao", 2024, uf="SP")

