"""
AudreyLab-GWAS_PostQC - CLI Tool for post-GWAS quality control of Regenie output

Author: Etienne Ntumba
Affiliation: Research Assistant at Audrey Grant Lab, McGill University
Contact: etienne.ntumba@mail.mcgill.ca

This tool performs quality control on Regenie step 2 output files across multiple chromosomes,
including filters for EMAC, HWE, and INFO score, and prepares outputs for FUMA and other post-GWAS platforms.
"""

import argparse
import os
import sys
import pandas as pd
from .core import merge_files, filter_df, prep_munge, prepare_fuma

def main():
    parser = argparse.ArgumentParser(
        description="AudreyLab-GWAS_PostQC: Post-GWAS QC tool for Regenie output"
    )
    parser.add_argument("--input-dir", required=True, help="Directory with Regenie result files")
    parser.add_argument("--pattern", default="Step_2_chr_*.regenie", help="Glob pattern for Regenie files")
    parser.add_argument("--out", required=True, help="Output file prefix (no extension)")
    parser.add_argument("--pheno-name", default="", help="Optional phenotype name to include in output")
    parser.add_argument("--min-emac", type=float, default=100, help="Minimum EMAC threshold")
    parser.add_argument("--min-hwe", type=float, default=1e-12, help="Minimum HWE p-value")
    parser.add_argument("--min-info-score", type=float, default=None, help="Minimum INFO score if available")
    parser.add_argument("--drop-na", action="store_true", help="Drop rows with NA in key columns")
    parser.add_argument("--save-intermediate", action="store_true", help="Save intermediate filtered file")
    parser.add_argument("--force", action="store_true", help="Overwrite output files if they exist")
    parser.add_argument("--fuma", action="store_true", help="Generate FUMA-compatible output")
    parser.add_argument("--format", default="tsv", choices=["tsv", "csv", "parquet"], help="Output format")
    parser.add_argument("--log", action="store_true", help="Save processing log")

    args = parser.parse_args()

    # Prepare output paths
    ext_map = {"tsv": ".tsv.gz", "csv": ".csv.gz", "parquet": ".parquet"}
    ext = ext_map[args.format]

    merged_path = f"{args.out}.regenie.merged{ext}"
    qc_path = f"{args.out}.regenie.qc{ext}"
    munged_path = f"{args.out}.pre-munged{ext}"
    fuma_path = f"{args.out}.fuma.tsv"

    # Safety check
    for path in [merged_path, qc_path, munged_path, fuma_path]:
        if os.path.exists(path) and not args.force:
            print(f"❌ Output file {path} already exists. Use --force to overwrite.")
            sys.exit(1)

    log_lines = []

    df = merge_files(args.input_dir, args.pattern)
    log_lines.append(f"🔍 Loaded {len(df)} variants from {args.input_dir}")
    df.to_csv(merged_path, sep="\t", index=False, compression="gzip")
    
    df_qc = filter_df(df, args.min_emac, args.min_hwe, args.min_info_score, drop_na=args.drop_na)
    log_lines.append(f"✅ {len(df_qc)} variants passed QC")

    if args.save_intermediate:
        df_qc.to_csv(qc_path, sep="\t", index=False, compression="gzip")

    df_munged = prep_munge(df_qc)
    df_munged.to_csv(munged_path, sep="\t", index=False, compression="gzip")
    log_lines.append(f"📦 Saved munged file to {munged_path}")

    if args.fuma:
        fuma_df = prepare_fuma(df_qc)
        fuma_df.to_csv(fuma_path, sep="\t", index=False)
        log_lines.append(f"🧠 FUMA file saved to {fuma_path}")

    if args.log:
        with open(f"{args.out}.log", "w") as f:
            for line in log_lines:
                f.write(line + "\n")
        print("📝 Log written.")

    print("\n".join(log_lines))
