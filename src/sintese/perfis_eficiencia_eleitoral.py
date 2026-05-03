"""Perfis de eficiência eleitoral — quem aceita mais, quem aceita menos.

Cruza a base consolidada de eleitos (votos × financiamento) com
arquétipos identificados pelo nome de urna do candidato:

- Religioso: PASTOR, BISPO, MISSIONÁRIO, IRMÃO, DIÁCONO, APÓSTOLO
- Força/segurança: SARGENTO, MAJOR, CABO, CAPITÃO, TENENTE, DELEGADO,
  CORONEL, INSPETOR, COMANDANTE, POLICIAL, GUARDA, BOMBEIRO
- Profissional/técnico: DR., DOUTOR(A), PROFESSOR(A), PROF., ENG.,
  ENGENHEIRO
- Familiar/dinastia: NETO, FILHO, JR, JÚNIOR, FILHA
- Coletivo: MANDATA, BANCADA, JUNTAS, COLETIVO
- Outros (sem arquétipo claro)

Compara eficiência (votos/R$ mil) por arquétipo × cargo × bloco.
Maior eficiência = candidato mais aceito naturalmente, precisa de
menos investimento para converter votos.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import re
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

CSV_BASE = _ROOT / "outputs/tables/votos_vs_financiamento_todos_cargos.csv"
SAIDA_CSV = _ROOT / "outputs/tables/perfis_eficiencia_eleitoral.csv"
SAIDA_FIG = _ROOT / "outputs/figures/perfis_eficiencia_eleitoral.png"

# Padrões para detectar arquétipo pelo nome de urna
ARQUETIPOS = [
    ("Religioso", [
        r"\bPASTOR\b", r"\bPASTORA\b", r"\bBISPO\b", r"\bBISPA\b",
        r"\bMISSION", r"\bIRM[ÃA]O\b", r"\bIRM[ÃA]\b", r"\bDI[ÁA]CONO\b",
        r"\bAP[ÓO]STOLO\b", r"\bPADRE\b", r"\bFREI\b", r"\bREVERENDO\b",
        r"\bPRESBÍTERO\b", r"\bRABINO\b",
    ]),
    ("Segurança", [
        r"\bSARGENTO\b", r"\bMAJOR\b", r"\bCABO\b", r"\bCAPIT[ÃA]O\b",
        r"\bTENENTE\b", r"\bDELEGADO\b", r"\bDELEGADA\b", r"\bCORONEL\b",
        r"\bINSPETOR\b", r"\bCOMANDANTE\b", r"\bPM\b", r"\bGCM\b",
        r"\bGUARDA\b", r"\bBOMBEIRO\b", r"\bBRIGADIER\b", r"\bSOLDADO\b",
        r"\bPOLICIAL\b", r"\bAGENTE\b",
    ]),
    ("Profissional", [
        r"\bDR\b\.?", r"\bDR[A]?\b\.?", r"\bDOUTOR\b", r"\bDOUTORA\b",
        r"\bPROFESSOR\b", r"\bPROFESSORA\b", r"\bPROF\b\.?",
        r"\bENG\b\.?", r"\bENGENHEIRO\b", r"\bENGENHEIRA\b",
        r"\bADVOGAD[OA]\b", r"\bM[ÉE]DIC[OA]\b", r"\bDENTISTA\b",
    ]),
    ("Familiar/Dinastia", [
        r"\bNETO\b$", r"\bFILHO\b$", r"\bFILHA\b$", r"\bJR\b\.?$",
        r"\bJ[UÚ]NIOR\b$", r"\bSOBRINHO\b$",
    ]),
    ("Coletivo/Mandata", [
        r"\bMANDATA\b", r"\bMANDATO COLETIVO\b", r"\bBANCADA\b",
        r"\bJUNTAS\b", r"\bCOLETIV[OA]\b",
    ]),
]


def classificar_arquetipo(nome: str) -> str:
    """Retorna o primeiro arquétipo que casa com o nome (em uppercase)."""
    if not isinstance(nome, str):
        return "Outros"
    n = nome.upper().strip()
    for label, padroes in ARQUETIPOS:
        for p in padroes:
            if re.search(p, n):
                return label
    return "Outros"


def main() -> None:
    print("=" * 80)
    print("PERFIS DE EFICIÊNCIA ELEITORAL — quem o eleitorado aceita mais")
    print("=" * 80)

    df = pd.read_csv(CSV_BASE)
    df = df[df["receita_2024"] > 0].copy()
    df["arquetipo"] = df["nome"].map(classificar_arquetipo)
    df["eficiencia"] = df["votos"] / (df["receita_2024"] / 1000)
    df["custo_voto"] = df["receita_2024"] / df["votos"]

    print(f"\nN eleitos com receita > 0: {len(df)}")
    print(f"\nDistribuição por arquétipo:")
    print(df["arquetipo"].value_counts().to_string())

    # Por arquétipo (todos os cargos)
    print(f"\n--- Eficiência por arquétipo (todos os cargos × anos) ---")
    print(f"  {'Arquétipo':<22} {'N':>5} {'votos_med':>10} {'receita_med':>14} "
          f"{'cust_med':>9} {'cust_mediana':>13} {'votos/R$mil':>12}")
    by_arq = df.groupby("arquetipo").agg(
        n=("nome", "count"),
        votos_med=("votos", "mean"),
        receita_med=("receita_2024", "mean"),
        cust_med=("custo_voto", "mean"),
        cust_mediana=("custo_voto", "median"),
        ef_med=("eficiencia", "median"),
    ).sort_values("ef_med", ascending=False)
    for arq, r in by_arq.iterrows():
        print(f"  {arq:<22} {int(r['n']):>5} {r['votos_med']:>10,.0f} "
              f"R$ {r['receita_med']/1000:>10,.0f}k "
              f"R$ {r['cust_med']:>6,.0f} R$ {r['cust_mediana']:>9,.0f} "
              f"{r['ef_med']:>12,.0f}")

    # Por arquétipo × bloco ideológico
    print(f"\n--- Custo mediano por voto (R$ 2024) por arquétipo × bloco ---")
    pb = df.groupby(["arquetipo", "bloco"])["custo_voto"].median().unstack().round(2)
    print(pb.to_string())

    # Por arquétipo × cargo
    print(f"\n--- N por arquétipo × cargo ---")
    pc = df.groupby(["arquetipo", "cargo"])["nome"].count().unstack(fill_value=0)
    print(pc.to_string())

    print(f"\n--- Custo mediano por arquétipo × cargo ---")
    pcc = df.groupby(["arquetipo", "cargo"])["custo_voto"].median().unstack().round(2)
    print(pcc.to_string())

    # Top 15 mais eficientes (custo/voto baixo)
    print(f"\n--- TOP 15 mais eficientes (menor R$/voto) ---")
    top = df.nsmallest(15, "custo_voto")[["nome", "partido", "bloco", "arquetipo",
                                           "cargo", "ano", "votos", "receita_2024",
                                           "custo_voto"]]
    print(top.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))

    print(f"\n--- BOTTOM 15 menos eficientes (maior R$/voto) ---")
    bot = df.nlargest(15, "custo_voto")[["nome", "partido", "bloco", "arquetipo",
                                          "cargo", "ano", "votos", "receita_2024",
                                          "custo_voto"]]
    print(bot.to_string(index=False, float_format=lambda x: f"{x:,.0f}"))

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA_CSV, index=False)
    print(f"\nCSV salvo: {SAIDA_CSV}")

    # ===== Visualização =====
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=120)
    cores_bloco = {"ESQUERDA": "#d62728", "CENTRO": "#7f7f7f",
                    "DIREITA": "#1f77b4", "DESCONHECIDO": "#cccccc"}

    # Painel 1: barras — custo mediano por arquétipo
    ax = axes[0, 0]
    by_arq_sorted = by_arq.sort_values("cust_mediana")
    cores = ["#2ca02c" if v < 15 else "#d62728" if v > 30 else "#ff7f0e"
             for v in by_arq_sorted["cust_mediana"]]
    bars = ax.barh(by_arq_sorted.index, by_arq_sorted["cust_mediana"],
                    color=cores, alpha=0.85, edgecolor="black", linewidth=0.4)
    for bar, v, n in zip(bars, by_arq_sorted["cust_mediana"], by_arq_sorted["n"]):
        ax.annotate(f"R$ {v:.1f} (n={int(n)})",
                    xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                    xytext=(3, 0), textcoords="offset points",
                    fontsize=9, va="center")
    ax.set_xlabel("Custo mediano por voto (R$ 2024)")
    ax.set_title("Eficiência por arquétipo (mediana — menor = melhor)",
                  fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    # Painel 2: boxplot eficiência por arquétipo × bloco
    ax = axes[0, 1]
    arq_order = list(by_arq_sorted.index)
    width = 0.27
    x = np.arange(len(arq_order))
    for i, b in enumerate(["ESQUERDA", "CENTRO", "DIREITA"]):
        valores = []
        for a in arq_order:
            v = df[(df["arquetipo"] == a) & (df["bloco"] == b)]["custo_voto"].median()
            valores.append(v if not np.isnan(v) else 0)
        ax.bar(x + (i - 1) * width, valores, width, color=cores_bloco[b],
                alpha=0.85, edgecolor="black", linewidth=0.4, label=b)
    ax.set_xticks(x)
    ax.set_xticklabels(arq_order, rotation=15, ha="right", fontsize=9)
    ax.set_ylabel("Custo mediano por voto (R$ 2024)")
    ax.set_title("Custo por voto: arquétipo × bloco ideológico",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # Painel 3: scatter votos × receita, colorido por arquétipo
    ax = axes[1, 0]
    cores_arq = {
        "Religioso": "#9467bd", "Segurança": "#1f77b4",
        "Profissional": "#2ca02c", "Familiar/Dinastia": "#ff7f0e",
        "Coletivo/Mandata": "#d62728", "Outros": "#cccccc",
    }
    for arq, c in cores_arq.items():
        sub = df[df["arquetipo"] == arq]
        if sub.empty: continue
        ax.scatter(sub["receita_2024"]/1000, sub["votos"],
                   c=c, s=40, alpha=0.6, edgecolor="black",
                   linewidth=0.2, label=f"{arq} (n={len(sub)})")
    # Linha de referência R$ 30/voto
    rec_x = np.logspace(2, 5, 100)
    ax.plot(rec_x, rec_x * 1000 / 30, "k--", alpha=0.4,
             label="R$ 30/voto (mediana geral)")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Receita declarada (R$ mil 2024)")
    ax.set_ylabel("Votos do eleito")
    ax.set_title("Votos × receita por arquétipo (log-log)",
                  fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.3, which="both")

    # Painel 4: heatmap arquétipo × cargo (custo)
    ax = axes[1, 1]
    cargos_ord = ["Vereador", "Prefeito", "Deputado Estadual",
                   "Deputado Federal", "Senador", "Governador"]
    arq_ord = list(by_arq_sorted.index)
    pcc = pcc.reindex(index=arq_ord, columns=cargos_ord).astype(float)
    im = ax.imshow(pcc.values, cmap="YlOrRd", aspect="auto")
    for i in range(pcc.shape[0]):
        for j in range(pcc.shape[1]):
            v = pcc.iat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=9, fontweight="bold",
                        color="white" if v > 30 else "black")
    ax.set_xticks(range(pcc.shape[1]))
    ax.set_xticklabels(pcc.columns, rotation=15, ha="right")
    ax.set_yticks(range(pcc.shape[0]))
    ax.set_yticklabels(pcc.index)
    fig.colorbar(im, ax=ax, label="R$/voto (mediana)")
    ax.set_title("Custo mediano: arquétipo × cargo",
                  fontsize=11, fontweight="bold")

    fig.suptitle(
        "Perfis de eficiência eleitoral — eleitos em SP\n"
        f"N={len(df)} | classificados por arquétipo no nome de urna",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
