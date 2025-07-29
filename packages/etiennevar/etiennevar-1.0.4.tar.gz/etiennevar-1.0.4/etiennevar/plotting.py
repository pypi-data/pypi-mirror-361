# etiennevar/plotting.py
import matplotlib.pyplot as plt
import gzip
from collections import Counter
import os
import numpy as np
import seaborn as sns

def open_vcf(vcf_path):
    return gzip.open(vcf_path, "rt") if vcf_path.endswith(".gz") else open(vcf_path, "r")

def save_variant_distribution_plot(vcf_file, output_file="variant_distribution.png", plot_type="histo", show_stats=False):
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

        if show_stats:
            print("===== Statistiques des variants =====")
            print(f"Nombre total de chromosomes : {len(chromosomes)}")
            print(f"Nombre total de variants : {sum(counts)}")
            print(f"Moyenne : {mean_count:.2f}")
            print(f"Médiane : {median_count:.2f}")
            print(f"Min : {min(counts)}, Max : {max(counts)}")

        plt.figure(figsize=(10, 6))
        if plot_type == "histo":
            plt.bar(chromosomes, counts)
            plt.axhline(mean_count, color='red', linestyle='--', label=f"Moyenne: {mean_count:.0f}")
            plt.axhline(median_count, color='green', linestyle=':', label=f"Médiane: {median_count:.0f}")
        elif plot_type == "circle":
            plt.pie(counts, labels=chromosomes, autopct='%1.1f%%', startangle=90)
        elif plot_type == "boxplot":
            plt.boxplot(counts)
            plt.xticks([1], ["Chromosomes"])
        elif plot_type == "violin":
            sns.violinplot(data=counts)
            plt.xticks([0], ["Chromosomes"])
        else:
            raise ValueError(f"Type de graphique non reconnu : {plot_type}")

        plt.title("Distribution des variants par chromosome")
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
        print(f"[✓] Graphique sauvegardé dans : {output_file}")

    except Exception as e:
        print(f"[Erreur] Impossible de générer le graphique : {e}")

