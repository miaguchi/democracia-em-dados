from dataclasses import dataclass
from typing import Optional

UFS_VALIDAS = {
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
}


@dataclass
class Candidato:
    nome: str
    partido: str
    uf: str
    genero: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.nome, str) or not self.nome.strip():
            raise ValueError("nome inválido")
        if not isinstance(self.partido, str) or not self.partido.strip():
            raise ValueError("partido inválido")
        if self.uf not in UFS_VALIDAS:
            raise ValueError(f"UF inválida: {self.uf}")
        if self.genero is not None and self.genero not in {"M", "F", "NB"}:
            raise ValueError("gênero inválido")
