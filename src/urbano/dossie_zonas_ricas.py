"""Dossiê focado: comportamento eleitoral nas zonas ricas de SP.

Alvos empíricos do projeto de mestrado (Miaguchi 2023):
- Zonas-chave: 5 (Jardim Paulista), 251 (Pinheiros), 258 (Indianópolis)
- Corredor das universidades: 1 (Bela Vista), 2 (Perdizes), 3 (Santa Ifigênia),
  5 (Jardim Paulista), 251 (Pinheiros), 346 (Butantã) + 6 (Vila Mariana)

Produz para cada zona e ano (2020, 2024):
- Top 10 partidos em vereador e prefeito
- Escore ideológico médio ponderado
- NEP (Laakso-Taagepera) — fragmentação partidária
- Pedersen 2020→2024
- Bloco dominante quintipartite

Compara com a média da cidade para testar H1 (padrão distinto nas zonas ricas).
"""

from pathlib import Path

import pandas as pd

from src.partidario.analise_volatilidade import (
    carregar_sp_prefeito,
    carregar_sp_vereador,
    pedersen,
    votos_por_partido,
)
from src.partidario.ideologia import (
    ESCORE_BOLOGNESI,
    bloco_quintipartite,
    usar_quintipartite,
    volatilidade_decomposta,
    votos_por_bloco,
)

usar_quintipartite()

ZONAS_ALVO = {
    1: "Bela Vista",
    2: "Perdizes",
    3: "Santa Ifigênia",
    5: "Jardim Paulista",
    6: "Vila Mariana",
    251: "Pinheiros",
    258: "Indianópolis",
    346: "Butantã",
}

SAIDA_CSV = Path("outputs/dossie_zonas_ricas.csv")


def nep(votos: pd.Series) -> float:
    """Laakso-Taagepera (1979): NEP = 1 / sum(p_i^2)."""
    total = votos.sum()
    if total == 0:
        return 0.0
    props = votos / total
    return 1.0 / (props ** 2).sum()


def escore_medio(votos: pd.Series) -> float:
    tab = pd.DataFrame({"v": votos.values, "e": votos.index.map(ESCORE_BOLOGNESI.get)})
    tab = tab.dropna()
    if tab["v"].sum() == 0:
        return float("nan")
    return (tab["v"] * tab["e"]).sum() / tab["v"].sum()


def por_zona(df: pd.DataFrame, zona: int) -> pd.Series:
    sub = df[df["NR_ZONA"] == zona]
    return sub.groupby("PARTIDO")["VOTOS"].sum().sort_values(ascending=False)


def relatorio_cargo(cargo: str, carregar_fn):
    print(f"\n{'#' * 85}")
    print(f"#  {cargo}")
    print(f"{'#' * 85}")
    df_2020 = carregar_fn(2020)
    df_2024 = carregar_fn(2024)

    # Totais da cidade (referência)
    c20 = votos_por_partido(df_2020)
    c24 = votos_por_partido(df_2024)
    vt_cid, ve_cid, vd_cid = volatilidade_decomposta(c20, c24)
    print(f"\n[REFERÊNCIA — CIDADE INTEIRA]")
    print(f"  escore médio 2020: {escore_medio(c20):.3f}   2024: {escore_medio(c24):.3f}")
    print(f"  NEP             2020: {nep(c20):6.2f}   2024: {nep(c24):6.2f}")
    print(f"  Pedersen: {vt_cid:.4f} | V_entre: {ve_cid:.4f} ({ve_cid/vt_cid*100:.1f}%)")

    linhas = []
    for zona, nome in ZONAS_ALVO.items():
        v20 = por_zona(df_2020, zona)
        v24 = por_zona(df_2024, zona)
        if v20.empty or v24.empty:
            continue
        vt, ve, vd = volatilidade_decomposta(v20, v24)
        e20, e24 = escore_medio(v20), escore_medio(v24)
        n20, n24 = nep(v20), nep(v24)

        print(f"\n── Zona {zona:>3} — {nome} ──────────────────────────────────")
        print(
            f"  escore médio: {e20:.3f} → {e24:.3f}  "
            f"(Δ = {e24 - e20:+.3f}; cidade Δ = "
            f"{escore_medio(c24) - escore_medio(c20):+.3f})"
        )
        print(f"  NEP        : {n20:6.2f} → {n24:6.2f}")
        print(f"  Pedersen   : {vt:.4f}  |  V_entre: {ve:.4f} ({ve/vt*100:.1f}%)")

        # Bloco dominante
        b20 = votos_por_bloco(v20)
        b24 = votos_por_bloco(v24)
        pct20 = (b20 / b20.sum() * 100).round(1)
        pct24 = (b24 / b24.sum() * 100).round(1)
        blocos_df = pd.DataFrame({"2020 %": pct20, "2024 %": pct24}).fillna(0)
        ordem = [
            "ESQUERDA",
            "CENTRO-ESQUERDA",
            "CENTRO",
            "CENTRO-DIREITA",
            "DIREITA",
            "DESCONHECIDO",
        ]
        blocos_df = blocos_df.reindex([x for x in ordem if x in blocos_df.index])
        print("  Blocos:")
        for b, row in blocos_df.iterrows():
            print(f"    {b:<16} {row['2020 %']:>6.1f} → {row['2024 %']:>6.1f}")

        # Top 5 partidos em cada ano
        print("  Top 5 partidos:")
        for ano, v in [(2020, v20), (2024, v24)]:
            tops = v.head(5)
            linha = " | ".join(
                f"{p} {n/v.sum()*100:.1f}%" for p, n in tops.items()
            )
            print(f"    {ano}: {linha}")

        linhas.append(
            {
                "zona": zona,
                "nome": nome,
                "cargo": cargo,
                "escore_2020": e20,
                "escore_2024": e24,
                "delta_escore": e24 - e20,
                "nep_2020": n20,
                "nep_2024": n24,
                "pedersen": vt,
                "v_entre_blocos": ve,
                "v_dentro_blocos": vd,
                "pct_esq_2020": pct20.get("ESQUERDA", 0) + pct20.get("CENTRO-ESQUERDA", 0),
                "pct_esq_2024": pct24.get("ESQUERDA", 0) + pct24.get("CENTRO-ESQUERDA", 0),
                "pct_dir_2020": pct20.get("DIREITA", 0) + pct20.get("CENTRO-DIREITA", 0),
                "pct_dir_2024": pct24.get("DIREITA", 0) + pct24.get("CENTRO-DIREITA", 0),
            }
        )
    return pd.DataFrame(linhas)


tab_ver = relatorio_cargo("VEREADOR", carregar_sp_vereador)
tab_pref = relatorio_cargo("PREFEITO 1T", carregar_sp_prefeito)

SAIDA_CSV.parent.mkdir(parents=True, exist_ok=True)
pd.concat([tab_ver, tab_pref]).to_csv(SAIDA_CSV, index=False)
print(f"\n\nCSV salvo: {SAIDA_CSV}")
