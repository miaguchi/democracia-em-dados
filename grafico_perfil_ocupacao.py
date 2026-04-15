"""Gráfico: distribuição de ocupações de candidatos por tipo de zona de voto."""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("outputs/perfil_candidatos_zonas.csv")

# Recategoriza bins mais úteis
df["perfil_zona"] = pd.cut(
    df["pct_alta_dens"],
    bins=[-0.01, 10, 25, 101],
    labels=["Voto periférico\n(<10% em alta dens.)",
            "Voto misto\n(10-25%)",
            "Voto culturalmente\nconcentrado (>25%)"],
)

# Tabela cruzada
ct = pd.crosstab(df["categoria_ocup"], df["perfil_zona"], normalize="columns") * 100
# Ordem: mais interessante primeiro
ordem = ["academia_cultura", "profissional_liberal", "empresario", "servidor_publico",
         "politico", "religioso", "saude", "outros", "outros_tecnicos"]
ct = ct.reindex([c for c in ordem if c in ct.index]).fillna(0)

rotulos = {
    "academia_cultura": "Academia / cultura / imprensa",
    "profissional_liberal": "Profissional liberal (médico, adv., eng.)",
    "empresario": "Empresário / comerciante",
    "servidor_publico": "Servidor público",
    "politico": "Político incumbente",
    "religioso": "Religioso",
    "saude": "Profissional de saúde",
    "outros": "Outros (inclui apelidos populares)",
    "outros_tecnicos": "Outros técnicos",
}
ct.index = [rotulos.get(i, i) for i in ct.index]

fig, ax = plt.subplots(figsize=(12, 6.5))
ct.T.plot(kind="bar", stacked=True, ax=ax, colormap="tab10", width=0.7, edgecolor="white")
ax.set_xlabel("Perfil territorial do voto do candidato", fontsize=11)
ax.set_ylabel("% dos candidatos (com ≥500 votos)", fontsize=11)
ax.set_title(
    "Ocupação declarada dos candidatos a vereador × tipo de zona onde seu voto se concentra\n"
    "SP 2024 — 547 candidatos, % por coluna",
    fontsize=12,
)
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=9)
ax.set_ylim(0, 100)
plt.xticks(rotation=0, fontsize=9)

plt.tight_layout()
saida = Path("outputs/grafico_ocupacao_por_tipo_zona.png")
plt.savefig(saida, dpi=150, bbox_inches="tight")
print(f"Gráfico: {saida}")
print("\nTabela de distribuição:")
print(ct.round(1).to_string())
