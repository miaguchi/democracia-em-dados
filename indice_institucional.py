"""Índice de densidade institucional cultural-progressista por zona eleitoral.

A hipótese alternativa (ao voto de classe) é que o fator explicativo do
voto progressista nos bairros ricos é a densidade de instituições
educativo-culturais de perfil cosmopolita/universitário/progressista.
Este script operacionaliza essa hipótese quantitativamente.

Categorias identificadas por palavras-chave no nome do local de votação:

1. UNIVERSIDADE: locais com vínculo universitário (USP, Mackenzie, PUC,
   Uninove, FAAP, FMU, Insper, FMABC, etc.). Proxy da presença de
   corpo discente/docente/funcionários acadêmicos.

2. ESCOLA_PROGRESSISTA: escolas particulares de tradição construtivista
   (Vera Cruz, Equipe, Lumiar, Oswald de Andrade, Escola da Vila,
   Stella Maris, Horizontes, Itaca, Projeto, Albert Sabin).

3. PRESTIGIO_PUBLICO: escolas públicas com tradição de prestígio
   cultural/intelectual (Caetano de Campos, Fernão Dias Paes,
   Godofredo Furtado, Amorim Lima, Clorinda Danti, Fidelino de
   Figueiredo).

4. INTERNACIONAL_CULTURAL: instituições culturais internacionais com
   perfil cosmopolita (Goethe, Alliance Française, British, Dante
   Alighieri, Instituto Cervantes).

O índice final é simplesmente a contagem de locais em qualquer uma
dessas categorias dividida pelo total de locais da zona — é a
FRAÇÃO de locais culturais-progressistas da zona.
"""

from pathlib import Path
import re
import unicodedata
import pandas as pd
import geopandas as gpd

SHAPEFILE_LV = Path("data/raw/shapes/EL2022_LV_ESP_CEM_V2/EL2022_LV_ESP_CEM_V2.shp")
CSV_SOCIO = Path("outputs/socioeconomia_por_zona.csv")
SAIDA = Path("outputs/indice_institucional_por_zona.csv")


def normalizar(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ASCII", "ignore").decode()
    return s.upper().strip()


# Padrões por categoria
PADROES = {
    "UNIVERSIDADE": [
        r"\bUSP\b",
        r"\bMACKENZIE\b",
        r"\bPUC\b",
        r"\bUNINOVE\b",
        r"\bUNIFEOB\b",
        r"\bUNIFAE\b",
        r"\bFMU\b",
        r"\bFMABC\b",
        r"\bFAAP\b",
        r"\bINSPER\b",
        r"\bUNIBAN\b",
        r"\bUNIBERO\b",
        r"\bUNIP\b",
        r"\bSENAC\b",
        r"\bSENAI\b",
        r"\bFATEC\b",
        r"\bFACULDADE\b",
        r"\bUNIVERSIDADE\b",
        r"CAMPUS",
    ],
    "ESCOLA_PROGRESSISTA": [
        r"\bVERA CRUZ\b",
        r"\bEQUIPE\b",
        r"\bLUMIAR\b",
        r"\bESCOLA DA VILA\b",
        r"\bVILA DAS INFANCIAS\b",
        r"\bOSWALD DE ANDRADE\b",
        r"\bSTELLA MARIS\b",
        r"\bCOLEGIO HORIZONTES\b",
        r"\bITACA\b",
        r"\bPROJETO\b",
        r"\bALBERT SABIN\b",
        r"\bNOVA ESCOLA\b",
        r"\bSITO CATALAO\b",
        r"\bMAKIGUTI\b",
    ],
    "PRESTIGIO_PUBLICO": [
        r"\bCAETANO DE CAMPOS\b",
        r"\bFERNAO DIAS\b",
        r"\bGODOFREDO FURTADO\b",
        r"AMORIM LIMA",
        r"\bCLORINDA DANTI\b",
        r"\bFIDELINO DE FIGUEIREDO\b",
        r"\bANTONIO ALVES CRUZ\b",
        r"\bANESIA MARTINS MATOS\b",
        r"\bPORTO SEGURO\b",
    ],
    "INTERNACIONAL_CULTURAL": [
        r"GOETHE",
        r"ALLIANCE",
        r"DANTE ALIGHIERI",
        r"CERVANTES",
        r"\bBRITISH\b",
        r"BRITANICA",
        r"FRANCESA",
        r"ITALIANA",
    ],
}


def classificar(nome: str) -> set:
    nome_norm = normalizar(nome)
    categorias = set()
    for cat, padroes in PADROES.items():
        for padrao in padroes:
            if re.search(padrao, nome_norm):
                categorias.add(cat)
                break
    return categorias


def construir_indice() -> pd.DataFrame:
    gdf = gpd.read_file(SHAPEFILE_LV)
    sp = gdf[gdf["MUN_NOME"] == "SAO PAULO"].copy()
    sp["NR_ZONA"] = sp["ZE_NUM"].astype(int)

    # Classifica cada local
    sp["categorias"] = sp["NOME_LV"].map(classificar)
    sp["is_universidade"] = sp["categorias"].map(lambda c: "UNIVERSIDADE" in c).astype(int)
    sp["is_progressista"] = sp["categorias"].map(lambda c: "ESCOLA_PROGRESSISTA" in c).astype(int)
    sp["is_prestigio"] = sp["categorias"].map(lambda c: "PRESTIGIO_PUBLICO" in c).astype(int)
    sp["is_internacional"] = sp["categorias"].map(lambda c: "INTERNACIONAL_CULTURAL" in c).astype(int)
    sp["is_cultural_progressista"] = (
        (sp["is_universidade"] + sp["is_progressista"] + sp["is_prestigio"] + sp["is_internacional"]) > 0
    ).astype(int)

    # Agrega por zona
    agg = sp.groupby("NR_ZONA").agg(
        n_locais=("NOME_LV", "count"),
        n_universidade=("is_universidade", "sum"),
        n_progressista=("is_progressista", "sum"),
        n_prestigio=("is_prestigio", "sum"),
        n_internacional=("is_internacional", "sum"),
        n_cultural_progressista=("is_cultural_progressista", "sum"),
        nome_ze=("ZE_NOME", "first"),
    )
    agg["indice_cultural"] = agg["n_cultural_progressista"] / agg["n_locais"] * 100
    return agg


if __name__ == "__main__":
    idx = construir_indice()
    print(f"\nZonas analisadas: {len(idx)}")

    # Top e bottom
    print("\n=== TOP 15 ZONAS POR DENSIDADE INSTITUCIONAL CULTURAL-PROGRESSISTA ===")
    top = idx.sort_values("indice_cultural", ascending=False).head(15)
    print(top[["nome_ze","n_locais","n_universidade","n_progressista",
               "n_prestigio","n_internacional","indice_cultural"]].to_string(
        float_format=lambda x: f"{x:6.1f}"
    ))

    print("\n=== BOTTOM 10 (menor densidade) ===")
    bot = idx.sort_values("indice_cultural").head(10)
    print(bot[["nome_ze","n_locais","n_cultural_progressista","indice_cultural"]].to_string(
        float_format=lambda x: f"{x:6.1f}"
    ))

    # Integra com socioeconomia + escore
    socio = pd.read_csv(CSV_SOCIO).set_index("NR_ZONA")
    merge = idx.join(socio[["renda_pc_media","escore_ver_2024","escore_pref_2024"]])
    merge.to_csv(SAIDA)
    print(f"\nCSV: {SAIDA}")

    # Correlação
    print("\n=== CORRELAÇÕES ===")
    for col in ["escore_ver_2024","escore_pref_2024"]:
        for pred in ["renda_pc_media","indice_cultural"]:
            r = merge[[pred,col]].corr().iloc[0,1]
            print(f"  {pred:25} × {col}: r = {r:+.3f}")

    # Regressão múltipla
    import numpy as np
    sub = merge.dropna(subset=["escore_ver_2024","renda_pc_media","indice_cultural"])
    X = np.column_stack([
        np.ones(len(sub)),
        sub["renda_pc_media"].values,
        sub["indice_cultural"].values,
    ])
    for dep in ["escore_ver_2024","escore_pref_2024"]:
        y = sub[dep].values
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        y_hat = X @ beta
        r2 = 1 - ((y - y_hat)**2).sum() / ((y - y.mean())**2).sum()
        print(f"\n  OLS {dep}:")
        print(f"    intercepto     = {beta[0]:+.4f}")
        print(f"    renda_pc_media = {beta[1]:+.6f}")
        print(f"    indice_cultural= {beta[2]:+.4f}")
        print(f"    R²             = {r2:.3f}")
