#!/usr/bin/env python2.7
from __future__ import print_function
import sys
import csv

"""
Usage:
  # 1) Without binner label (no 'binner' column in output)
  python2.7 summarize_checkm.py quality_report.tsv > sample.stats.txt

  # 2) With binner label (adds trailing 'binner' column)
  python2.7 summarize_checkm.py quality_report.tsv BINSET > sample.stats.txt

Input (CheckM2 TSV) must contain at least these headers:
  Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size

Output columns (tab-separated):
  bin  completeness  contamination  GC  lineage  N50  size  [binner]

Notes:
  - CheckM2 does not provide lineage -> we set 'lineage' to "NA".
  - To mimic the original script's appearance, numeric strings for
    completeness/contamination/GC are truncated to 5 characters.
  - N50 and size are printed as-is (no truncation), like the original.
"""

def fmt5(x):
    """Mimic the old script's simple 5-char truncation for floats/strings."""
    if x is None:
        return ""
    s = str(x)
    return s[:5]

def main():
    if len(sys.argv) not in (2, 3):
        sys.stderr.write("Usage:\n  {} quality_report.tsv\n  {} quality_report.tsv BINNER_LABEL\n".format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    in_path = sys.argv[1]
    have_binner = (len(sys.argv) == 3)
    binner_label = sys.argv[2] if have_binner else None

    # Build and print header
    base_cols = ["bin", "completeness", "contamination", "GC", "lineage", "N50", "size"]
    if have_binner:
        print("\t".join(base_cols + ["binner"]))
    else:
        print("\t".join(base_cols))

    # Parse CheckM2 quality_report.tsv
    with open(in_path, "r") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        # We expect these columns in the header:
        # Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size
        for row in rdr:
            name = row.get("Name", "")
            comp = row.get("Completeness", "")
            cont = row.get("Contamination", "")
            gc   = row.get("GC_Content", "")
            n50  = row.get("Contig_N50", "")
            size = row.get("Genome_Size", "")
            lineage = "NA"  # CheckM2 doesn't provide lineage

            out = [name, fmt5(comp), fmt5(cont), fmt5(gc), lineage, str(n50), str(size)]
            if have_binner:
                out.append(binner_label)
            print("\t".join(out))

if __name__ == "__main__":
    main()