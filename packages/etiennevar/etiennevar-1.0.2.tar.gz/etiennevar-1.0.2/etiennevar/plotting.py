# etiennevar/plotting.py
import matplotlib.pyplot as plt
import gzip
from collections import Counter
import os
import numpy as np

def open_vcf(vcf_path):
    if vcf_path.endswith(".gz"):
        return gzip.open(vcf_path, "rt")
    return open(vcf_path, "r")

def save_variant_distribution_plot(vcf_file, output_file="variant_distribution.png"):
    """
    Compte les variants par chromosome et sauvegarde un histogramme dans un fichier image.
    """
    try:
        chrom_counts = Counter()

        with open_vcf(vcf_file) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                chrom = line.strip().split("\t")[0]
                chrom_counts[chrom] += 1

        chromosomes = sorted(chrom_counts.keys(), key=lambda x: (len(x), x))
        counts = [chrom_counts[c] for c in chromosomes]

        mean_count = np.mean(counts)
        median_count = np.median(counts)

        plt.figure(figsize=(10, 6))
        bars = plt.bar(chromosomes, counts)
        plt.axhline(mean_count, color='red', linestyle='--', label=f"Moyenne: {mean_count:.0f}")
        plt.axhline(median_count, color='green', linestyle=':', label=f"Médiane: {median_count:.0f}")
        plt.xlabel("Chromosome")
        plt.ylabel("Nombre de variants")
        plt.title("Distribution des variants par chromosome")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(output_file)
        plt.close()
        print(f"[✓] Histogramme sauvegardé dans : {output_file}")

    except Exception as e:
        print(f"[Erreur] Impossible de générer le graphique : {e}")

