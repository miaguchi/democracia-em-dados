from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ResultadoEleitoral:
    codigo_ibge: int
    nome_municipio: str
    uf: str
    ano: int
    turno: int
    votos_por_candidato: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._validar_codigo_ibge()
        self._validar_uf()
        self._validar_ano()
        self._validar_turno()
        self._validar_votos()

    def _validar_codigo_ibge(self) -> None:
        if not isinstance(self.codigo_ibge, int):
            raise TypeError("codigo_ibge deve ser inteiro")
        if not (1_000_000 <= self.codigo_ibge <= 9_999_999):
            raise ValueError(
                f"codigo_ibge inválido: {self.codigo_ibge}. Deve ter 7 dígitos."
            )

    def _validar_uf(self) -> None:
        ufs_validas = {
            "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
            "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
            "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"
        }
        if self.uf not in ufs_validas:
            raise ValueError(f"UF inválida: {self.uf}")

    def _validar_ano(self) -> None:
        if self.ano < 1994:
            raise ValueError(f"ano inválido: {self.ano}")
        if self.ano % 2 != 0:
            raise ValueError(f"ano deve ser par (eleição): {self.ano}")

    def _validar_turno(self) -> None:
        if self.turno not in (1, 2):
            raise ValueError(f"turno deve ser 1 ou 2, recebido: {self.turno}")

    def _validar_votos(self) -> None:
        for candidato, votos in self.votos_por_candidato.items():
            if not isinstance(candidato, str) or not candidato.strip():
                raise ValueError(f"nome de candidato inválido: {candidato!r}")
            if not isinstance(votos, int) or votos < 0:
                raise ValueError(
                    f"votos de {candidato} inválidos: {votos}. "
                    "Deve ser inteiro não-negativo."
                )

    @property
    def total_votos(self) -> int:
        return sum(self.votos_por_candidato.values())

    @property
    def numero_candidatos(self) -> int:
        return sum(1 for v in self.votos_por_candidato.values() if v > 0)

    @property
    def vencedor(self) -> Optional[str]:
        if not self.votos_por_candidato or self.total_votos == 0:
            return None

        max_votos = max(self.votos_por_candidato.values())
        vencedores = [
            nome for nome, votos in self.votos_por_candidato.items()
            if votos == max_votos
        ]
        if len(vencedores) > 1:
            return None
        return vencedores[0]

    def percentual_de(self, candidato: str) -> float:
        if self.total_votos == 0:
            return 0.0
        return self.votos_por_candidato.get(candidato, 0) / self.total_votos

    def margem_de_vitoria(self) -> float:
        if self.total_votos == 0:
            return 0.0

        votos_ordenados = sorted(self.votos_por_candidato.values(), reverse=True)
        if len(votos_ordenados) < 2:
            return 1.0

        primeiro, segundo = votos_ordenados[0], votos_ordenados[1]
        return (primeiro - segundo) / self.total_votos

    def numero_efetivo_candidatos(self) -> float:
        if self.total_votos == 0:
            return 0.0

        proporcoes = [v / self.total_votos for v in self.votos_por_candidato.values()]
        soma_quadrados = sum(p ** 2 for p in proporcoes)

        if soma_quadrados == 0:
            return 0.0
        return 1.0 / soma_quadrados