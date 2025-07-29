# -*- coding: utf-8 -*-
import argparse
import gzip
import sys
from etiennevar.plotting import save_variant_distribution_plot

__version__ = "1.0.4"

def open_vcf(vcf_path):
    """Ouvre un fichier VCF compressé ou non."""
    return gzip.open(vcf_path, "rt") if vcf_path.endswith(".gz") else open(vcf_path, "r")

def summarize_vcf(vcf_file, chr_filter=None, range_filter=None):
    try:
        with open_vcf(vcf_file) as f:
            variant_count = 0
            chromosomes = set()

            for line in f:
                if line.startswith("#"):
                    continue

                parts = line.strip().split("\t")
                if len(parts) < 5:
                    continue

                chrom = parts[0]
                pos = int(parts[1])

                # Filtrage par chromosome
                if chr_filter and chrom not in chr_filter:
                    continue

                # Filtrage par intervalle
                if range_filter:
                    start, end = range_filter
                    if not (start <= pos <= end):
                        continue

                chromosomes.add(chrom)
                variant_count += 1

        print("===== Résumé du fichier VCF =====")
        print(f"Nombre de variants : {variant_count}")
        print(f"Chromosomes présents : {', '.join(sorted(chromosomes))}")

    except FileNotFoundError:
        print(f"Erreur : le fichier '{vcf_file}' n'existe pas.")
    except Exception as e:
        print(f"Erreur lors du traitement du fichier : {e}")

def main():
    parser = argparse.ArgumentParser(
        prog="etiennevar",
        description="🧬 etiennevar : Outil simple pour résumer et visualiser des fichiers VCF.\n"
                    "Utilisez --summary pour résumer, --plot pour un graphique.\n"
                    "Filtrage possible par chromosome (--chr) et/ou position (--range).",
        epilog="Développé par Etienne Kabongo • Version 1.0.3"
    )

    parser.add_argument("vcf_file", nargs="?", help="Chemin vers le fichier VCF (.vcf ou .vcf.gz)")
    parser.add_argument("--summary", action="store_true", help="Afficher un résumé du fichier VCF")
    parser.add_argument("--plot", action="store_true", help="Générer un graphique des variants")
    parser.add_argument("--plot-type", default="histo", choices=["histo", "circle", "boxplot", "violin"],
                        help="Type de graphique à générer (par défaut: histo)")
    parser.add_argument("--summary-stat", action="store_true", help="Afficher les statistiques lors du tracé")
    parser.add_argument("--output", default="variant_distribution.png",
                        help="Nom du fichier de sortie pour le graphique (par défaut: variant_distribution.png)")
    parser.add_argument("--version", action="store_true", help="Afficher la version de l'outil")
    parser.add_argument("--chr", nargs="+", help="Filtrer par un ou plusieurs chromosomes (ex: --chr 1 2 X)")
    parser.add_argument("--range", nargs=2, metavar=("START", "END"), type=int,
                        help="Filtrer les variants par position (ex: --range 1000 5000)")

    args = parser.parse_args()

    if args.version:
        print(f"etiennevar version {__version__}")
        sys.exit(0)

    if not args.vcf_file:
        parser.error("Le fichier VCF est requis sauf si --version est utilisé.")

    if args.summary:
        summarize_vcf(args.vcf_file, chr_filter=args.chr, range_filter=args.range)
    elif args.plot:
        save_variant_distribution_plot(
            args.vcf_file,
            output_file=args.output,
            plot_type=args.plot_type,
            show_stats=args.summary_stat
        )
    else:
        print("Utilisez --summary pour le résumé ou --plot pour le graphique.")

if __name__ == "__main__":
    main()

