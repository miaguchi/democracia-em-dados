"""TESTE D — Quebra estrutural no crescimento do PSOL para vereador.

Hipótese: o crescimento do PSOL nas zonas de alto índice institucional
começou ANTES da candidatura nacional de Boulos (2020). Se a quebra
estrutural for detectada em 2016, fortalece a tese de realinhamento
estrutural; se for em 2020, efeito-candidato não pode ser descartado.

Método:
- Selecionar top-10 zonas por índice institucional cultural-progressista.
- Agregar votos do PSOL (vereador, 1º turno) por ano (2000-2024).
- Aplicar teste de Chow para cada candidato a ponto de quebra.
- F-statistic compara modelo restrito (1 reta) vs não-restrito (2 retas).

Limitação: N=7 pontos. Poder estatístico baixo. Resultado é
indicativo, não conclusivo.
"""

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import matplotlib.pyplot as plt
import mysql.connector
import numpy as np
import pandas as pd
from scipy import stats

from src.ingestao.carregar_mysql import MYSQL_CONFIG, DATABASE

CSV_INDICE = _ROOT / "outputs/indice_institucional_por_zona.csv"
SAIDA_FIG = _ROOT / "outputs/figures/quebra_estrutural_psol.png"
SAIDA_CSV = _ROOT / "outputs/tables/quebra_estrutural_psol.csv"

CD_MUNICIPIO_SP = 71072
CD_PARTIDO_PSOL = 50
ANOS = [2000, 2004, 2008, 2012, 2016, 2020, 2024]


def votos_psol_por_zona_ano(zonas: list[int]) -> pd.DataFrame:
    """Retorna pivot zona × ano de votos do PSOL para vereador."""
    conn = mysql.connector.connect(database=DATABASE, **MYSQL_CONFIG)
    zonas_str = ",".join(str(z) for z in zonas)
    sql = f"""
    SELECT v.nr_zona, e.ano_eleicao, SUM(v.qt_votos_nominais) AS votos
    FROM votacao_partido_munzona v
    JOIN eleicao e ON v.cd_eleicao = e.cd_eleicao AND v.nr_turno = e.nr_turno
    WHERE v.nr_partido = {CD_PARTIDO_PSOL}
      AND v.cd_cargo = 13
      AND v.cd_municipio = {CD_MUNICIPIO_SP}
      AND e.nr_turno = 1
      AND v.nr_zona IN ({zonas_str})
      AND e.ano_eleicao IN ({",".join(str(a) for a in ANOS)})
    GROUP BY v.nr_zona, e.ano_eleicao
    """
    df = pd.read_sql(sql, conn)
    conn.close()
    pivot = df.pivot(index="nr_zona", columns="ano_eleicao", values="votos").fillna(0)
    pivot = pivot.reindex(columns=ANOS, fill_value=0)
    return pivot


def ols_simples(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """OLS y ~ a + b*x. Retorna (a, b, RSS)."""
    if len(x) < 2:
        return 0.0, 0.0, 0.0
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    rss = float(((y - y_hat) ** 2).sum())
    return float(beta[0]), float(beta[1]), rss


def chow_test(t: np.ndarray, y: np.ndarray, k: int) -> dict:
    """Teste de Chow para quebra após o k-ésimo ponto.

    Modelo restrito: y = a + b*t (sobre todos os pontos).
    Modelo não-restrito: duas regressões separadas (antes e depois de k).

    F = ((RSS_R - RSS_U) / p) / (RSS_U / (n - 2p))
    onde p é o número de parâmetros por segmento (2: intercepto + slope).
    """
    n = len(t)
    if k < 2 or n - k < 2:
        return {"F": np.nan, "p_value": np.nan, "rss_unrest": np.nan}

    _, _, rss_r = ols_simples(t, y)
    _, _, rss_1 = ols_simples(t[:k], y[:k])
    _, _, rss_2 = ols_simples(t[k:], y[k:])
    rss_u = rss_1 + rss_2

    p = 2
    df_num = p
    df_den = n - 2 * p
    if df_den <= 0 or rss_u <= 0:
        return {"F": np.nan, "p_value": np.nan, "rss_unrest": rss_u}

    F = ((rss_r - rss_u) / df_num) / (rss_u / df_den)
    pval = 1 - stats.f.cdf(F, df_num, df_den) if F > 0 else 1.0
    return {"F": float(F), "p_value": float(pval), "rss_unrest": rss_u,
            "rss_rest": rss_r, "df_num": df_num, "df_den": df_den}


def main() -> None:
    print("=" * 65)
    print("TESTE D — Quebra estrutural no crescimento do PSOL")
    print("=" * 65)

    # Top 10 zonas por índice institucional
    idx = pd.read_csv(CSV_INDICE).sort_values("indice_cultural", ascending=False)
    top10 = idx.head(10)
    print(f"\nTop 10 zonas por índice institucional:")
    for _, r in top10.iterrows():
        print(f"  Z{int(r['NR_ZONA']):>3}  {r['nome_ze']:<20} idx={r['indice_cultural']:5.1f}%")

    zonas = top10["NR_ZONA"].astype(int).tolist()

    # Votos PSOL por zona × ano
    pivot = votos_psol_por_zona_ano(zonas)
    print(f"\nMatriz votos PSOL (top 10 zonas × 7 anos):")
    print(pivot.to_string(float_format=lambda x: f"{x:,.0f}".replace(",", ".")))

    # Série agregada (soma das 10 zonas por ano)
    serie = pivot.sum(axis=0)
    print(f"\nTotal PSOL nas top-10 zonas, por ano:")
    for ano, v in serie.items():
        print(f"  {ano}: {v:>8,.0f}")

    # Teste de Chow para cada candidato a ponto de quebra
    t = np.array(ANOS, dtype=float)
    # Centralizar t para estabilidade numérica
    t_c = t - t.mean()
    y = serie.values.astype(float)

    print(f"\n--- Teste de Chow para cada ponto de quebra ---")
    print(f"  (k = índice do primeiro ponto APÓS a quebra)")
    print(f"  {'Ano':>6}  {'k':>3}  {'F':>8}  {'p-valor':>10}  Significância")

    resultados = []
    for k in range(2, len(ANOS) - 1):  # 2..5 — precisa pelo menos 2 pontos cada lado
        ano_quebra = ANOS[k]
        res = chow_test(t_c, y, k)
        F = res["F"]
        pval = res["p_value"]
        if pval < 0.001:
            sig = "*** (p<0.001)"
        elif pval < 0.01:
            sig = "** (p<0.01)"
        elif pval < 0.05:
            sig = "* (p<0.05)"
        elif pval < 0.10:
            sig = ". (p<0.10)"
        else:
            sig = "n.s."
        print(f"  {ano_quebra:>6}  {k:>3}  {F:>8.3f}  {pval:>10.4f}  {sig}")
        resultados.append({
            "ano_quebra": ano_quebra,
            "k": k,
            "F": F,
            "p_value": pval,
        })

    df_res = pd.DataFrame(resultados)
    melhor = df_res.iloc[df_res["F"].argmax()]
    print(f"\nQuebra mais forte: {int(melhor['ano_quebra'])} "
          f"(F={melhor['F']:.3f}, p={melhor['p_value']:.4g})")

    # Salvar
    SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_res.to_csv(SAIDA_CSV, index=False)
    print(f"CSV salvo: {SAIDA_CSV}")

    # Plot — série agregada com retas dos dois segmentos da melhor quebra
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=120)

    # Painel 1: trajetórias individuais das 10 zonas
    cmap = plt.cm.tab10
    for i, (z, row) in enumerate(pivot.iterrows()):
        nome = top10[top10["NR_ZONA"] == z]["nome_ze"].iloc[0]
        ax1.plot(ANOS, row.values, "o-", color=cmap(i % 10),
                 alpha=0.7, linewidth=1.5, markersize=5,
                 label=f"Z{int(z)} {nome[:14]}")
    ax1.set_xlabel("Ano da eleição")
    ax1.set_ylabel("Votos PSOL (vereador, 1T)")
    ax1.set_title("Top 10 zonas por índice institucional —\ntrajetórias individuais",
                  fontsize=11)
    ax1.legend(fontsize=7, loc="upper left", framealpha=0.9, ncol=2)
    ax1.set_xticks(ANOS)
    ax1.grid(alpha=0.3)

    # Painel 2: série agregada com quebra estrutural
    k_best = int(melhor["k"])
    ano_q = int(melhor["ano_quebra"])

    # Retas dos dois segmentos
    a1, b1, _ = ols_simples(t_c[:k_best], y[:k_best])
    a2, b2, _ = ols_simples(t_c[k_best:], y[k_best:])

    ax2.plot(ANOS, y, "o-", color="black", linewidth=2.5, markersize=10,
             label="Total nas top-10 zonas", zorder=3)

    # Reta antes da quebra
    t_seg1 = t[:k_best]
    y_seg1 = a1 + b1 * (t_seg1 - t.mean())
    ax2.plot(t_seg1, y_seg1, "--", color="#1f77b4", linewidth=2,
             label=f"Antes ({ANOS[0]}-{ANOS[k_best-1]}):  β={b1:+.0f}/ano")

    # Reta depois
    t_seg2 = t[k_best:]
    y_seg2 = a2 + b2 * (t_seg2 - t.mean())
    ax2.plot(t_seg2, y_seg2, "--", color="#d62728", linewidth=2,
             label=f"Depois ({ano_q}-{ANOS[-1]}):  β={b2:+.0f}/ano")

    # Marcar ponto de quebra
    ax2.axvline(ano_q, color="red", linestyle=":", alpha=0.5, linewidth=2)
    ax2.annotate(f"Quebra: {ano_q}\nF={melhor['F']:.2f}, p={melhor['p_value']:.3f}",
                 xy=(ano_q, y.max() * 0.55),
                 xytext=(ano_q + 0.3, y.max() * 0.7),
                 fontsize=10, fontweight="bold",
                 arrowprops=dict(arrowstyle="->", color="red"))

    ax2.set_xlabel("Ano da eleição")
    ax2.set_ylabel("Votos PSOL agregados (top-10 zonas)")
    ax2.set_title("Quebra estrutural — agregado top-10 zonas\n"
                  "Vereador, PSOL, 1º turno",
                  fontsize=11, fontweight="bold")
    ax2.legend(fontsize=9, loc="upper left", framealpha=0.9)
    ax2.set_xticks(ANOS)
    ax2.grid(alpha=0.3)

    fig.suptitle(
        "TESTE D — Quebra estrutural no crescimento do PSOL\n"
        "Hipótese: crescimento começou antes de Boulos (2020)",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout()
    SAIDA_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA_FIG, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Figura salva: {SAIDA_FIG}")


if __name__ == "__main__":
    main()
