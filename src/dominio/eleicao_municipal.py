"""Composição: eleição municipal agrega candidatos + resultado."""

from dataclasses import dataclass
from typing import Dict, List

from src.dominio.candidato import Candidato
from src.dominio.resultado import ResultadoEleitoral


@dataclass
class EleicaoMunicipal:
    candidatos: List[Candidato]
    resultado: ResultadoEleitoral

    def __post_init__(self) -> None:
        if not isinstance(self.candidatos, list) or not self.candidatos:
            raise ValueError("candidatos deve ser lista não vazia")
        if not all(isinstance(c, Candidato) for c in self.candidatos):
            raise TypeError("todos os elementos devem ser Candidato")
        if not isinstance(self.resultado, ResultadoEleitoral):
            raise TypeError("resultado deve ser ResultadoEleitoral")

        nomes_candidatos = {c.nome for c in self.candidatos}
        nomes_votos = set(self.resultado.votos_por_candidato.keys())
        faltando = nomes_votos - nomes_candidatos
        if faltando:
            raise ValueError(
                f"votos para candidatos não cadastrados: {sorted(faltando)}"
            )

    @property
    def votos_por_partido(self) -> Dict[str, int]:
        partido_por_nome = {c.nome: c.partido for c in self.candidatos}
        agregado: Dict[str, int] = {}
        for nome, votos in self.resultado.votos_por_candidato.items():
            partido = partido_por_nome[nome]
            agregado[partido] = agregado.get(partido, 0) + votos
        return agregado

    @property
    def numero_efetivo_partidos(self) -> float:
        """Laakso-Taagepera: NEP = 1 / sum(p_i^2)."""
        total = self.resultado.total_votos
        if total == 0:
            return 0.0
        proporcoes = [v / total for v in self.votos_por_partido.values()]
        soma_quadrados = sum(p ** 2 for p in proporcoes)
        if soma_quadrados == 0:
            return 0.0
        return 1.0 / soma_quadrados

    @property
    def fragmentacao(self) -> float:
        """Índice de Rae: 1 - sum(p_i^2). Entre 0 (monopartido) e ~1."""
        total = self.resultado.total_votos
        if total == 0:
            return 0.0
        proporcoes = [v / total for v in self.votos_por_partido.values()]
        return 1.0 - sum(p ** 2 for p in proporcoes)

    def volatilidade_vs(self, anterior: "EleicaoMunicipal") -> float:
        """Índice de Pedersen: 0.5 * sum(|p_it - p_i(t-1)|)."""
        if not isinstance(anterior, EleicaoMunicipal):
            raise TypeError("anterior deve ser EleicaoMunicipal")
        if anterior.resultado.codigo_ibge != self.resultado.codigo_ibge:
            raise ValueError("volatilidade requer mesmo município")

        total_atual = self.resultado.total_votos
        total_ant = anterior.resultado.total_votos
        if total_atual == 0 or total_ant == 0:
            return 0.0

        prop_atual = {
            p: v / total_atual for p, v in self.votos_por_partido.items()
        }
        prop_ant = {
            p: v / total_ant for p, v in anterior.votos_por_partido.items()
        }
        partidos = set(prop_atual) | set(prop_ant)
        soma = sum(
            abs(prop_atual.get(p, 0.0) - prop_ant.get(p, 0.0)) for p in partidos
        )
        return 0.5 * soma
