from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.ingestao.tse_downloader import TSEDownloader

_ROOT / "data/raw/votacao_secao_2020_SP.zip".unlink(missing_ok=True)  # zip truncado anterior

d = TSEDownloader(raw_dir=_ROOT / "data/raw", processed_dir=_ROOT / "data/processed")
p2020 = d.ingerir("votacao_secao", 2020, uf="SP")
p2024 = d.ingerir("votacao_secao", 2024, uf="SP")

