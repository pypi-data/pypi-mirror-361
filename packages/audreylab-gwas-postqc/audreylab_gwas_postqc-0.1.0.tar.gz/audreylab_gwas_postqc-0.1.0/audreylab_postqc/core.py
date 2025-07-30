"""
Core functions for AudreyLab-GWAS_PostQC

This module provides the main computational functions used for merging, filtering,
and formatting Regenie GWAS outputs.

Author: Etienne Ntumba
Lab: Audrey Grant Lab, McGill University
"""

import pandas as pd
import numpy as np
from scipy.stats import chi2

def hwe_p(obs_hets, obs_hom1, obs_hom2):
    n = obs_hets + obs_hom1 + obs_hom2
    if n == 0:
        return 1.0
    p = (2 * obs_hom2 + obs_hets) / (2 * n)
    q = 1 - p
    exp_h1 = n * p * p
    exp_hets = 2 * n * p * q
    exp_h2 = n * q * q
    stat = sum([
        (obs_hom1 - exp_h1) ** 2 / exp_h1 if exp_h1 > 0 else 0,
        (obs_hets - exp_hets) ** 2 / exp_hets if exp_hets > 0 else 0,
        (obs_hom2 - exp_h2) ** 2 / exp_h2 if exp_h2 > 0 else 0,
    ])
    return chi2.sf(stat, df=1)

def parse_info(info, key):
    if pd.isna(info): return np.nan
    for kv in str(info).split(";"):
        if kv.startswith(f"{key}="):
            return kv.split("=")[1]
    return np.nan

def merge_files(input_dir, pattern):
    from glob import glob
    import os
    files = sorted(glob(os.path.join(input_dir, pattern)))
    dfs = [pd.read_csv(f, sep="\t") for f in files]
    return pd.concat(dfs, ignore_index=True)

def filter_df(df, min_emac, min_hwe):
    id_col = "ID" if "ID" in df.columns else "Name" if "Name" in df.columns else None
    if id_col is None:
        raise ValueError("Aucune colonne 'ID' ou 'Name' trouvée.")
    df = df[df[id_col].astype(str).str.startswith("rs")]
    if "AAF" in df.columns and "Num_Cases" in df.columns and "Num_Controls" in df.columns:
        df["EMAC"] = 2 * df["AAF"] * (df["Num_Cases"] + df["Num_Controls"])
    else:
        df["EMAC"] = np.nan
    if all(col in df.columns for col in ["Cases_Het", "Cases_Ref", "Cases_Alt"]):
        df["HWE_P"] = df.apply(lambda r: hwe_p(r["Cases_Het"], r["Cases_Ref"], r["Cases_Alt"]), axis=1)
    else:
        df["HWE_P"] = 1.0
    return df[(df["EMAC"] >= min_emac) & (df["HWE_P"] >= min_hwe)]

def prep_munge(df):
    df["BETA"] = df["Info"].apply(lambda x: parse_info(x, "BETA")).astype(float)
    df["SE"] = df["Info"].apply(lambda x: parse_info(x, "SE")).astype(float)
    df["Z"] = df["BETA"] / df["SE"]
    out = df[["Name", "Ref", "Alt", "Z", "Pval", "BETA", "SE", "Chr", "Pos", "AAF", "EMAC"]].copy()
    out.columns = ["SNP", "A1", "A2", "Z", "P", "BETA", "SE", "CHR", "BP", "A2F", "EMAC"]
    return out
