#!/usr/bin/env python2.7
from __future__ import print_function
import sys
import csv
import os

"""
Usage:
  # 1) No binner column:
  python2.7 summarize_checkm.py quality_report.tsv > sample.stats.txt

  # 2) Fixed binner label (adds trailing 'binner' column on all rows):
  python2.7 summarize_checkm.py quality_report.tsv BINSET > sample.stats.txt

  # 3) Source map TSV (adds trailing 'binner' column from map's 8th column,
  #    keyed by bin name in col 1; the 2nd arg (e.g. 'manual') is ignored):
  python2.7 summarize_checkm.py quality_report.tsv manual binsM.stats > binsO.stats

Input (CheckM2 TSV) must contain at least these headers:
  Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size

Output columns (tab-separated):
  bin  completeness  contamination  GC  lineage  N50  size  [binner]

Notes:
  - CheckM2 does not provide lineage -> lineage is set to "NA".
  - For compatibility with the original formatting, completeness/contamination/GC
    are truncated to 5 chars. N50 and size are printed as-is.
"""

def fmt5(x):
    if x is None:
        return ""
    s = str(x)
    return s[:5]

def load_source_map(path):
    """Return {bin_name: binner_label} from TSV: col1=name, col8=binner."""
    src = {}
    with open(path, "r") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts:
                continue
            name = parts[0]
            label = parts[7] if len(parts) >= 8 else ""
            src[name] = label
    return src

def main():
    argc = len(sys.argv)
    if argc not in (2, 3, 4):
        sys.stderr.write(
            "Usage:\n"
            "  {} quality_report.tsv\n"
            "  {} quality_report.tsv BINNER_LABEL\n"
            "  {} quality_report.tsv manual SOURCE_MAP_TSV\n".format(sys.argv[0], sys.argv[0], sys.argv[0])
        )
        sys.exit(1)

    in_path = sys.argv[1]

    mode = "plain"       # 1 arg → no binner col
    binner_fixed = None  # 2 args → fixed label
    binner_map = None    # 3 args → map from file (ignore argv[2])

    if argc == 3:
        mode = "fixed"
        binner_fixed = sys.argv[2]
    elif argc == 4:
        mode = "map"
        binner_map = load_source_map(sys.argv[3])  # ignore sys.argv[2] (e.g., 'manual')

    # Header
    base = ["bin", "completeness", "contamination", "GC", "lineage", "N50", "size"]
    if mode in ("fixed", "map"):
        print("\t".join(base + ["binner"]))
    else:
        print("\t".join(base))

    # Parse CheckM2 quality_report.tsv
    with open(in_path, "r") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            name = row.get("Name", "")
            comp = row.get("Completeness", "")
            cont = row.get("Contamination", "")
            gc   = row.get("GC_Content", "")
            n50  = row.get("Contig_N50", "")
            size = row.get("Genome_Size", "")
            lineage = "NA"

            out = [name, fmt5(comp), fmt5(cont), fmt5(gc), lineage, str(n50), str(size)]
            if mode == "fixed":
                out.append(binner_fixed)
            elif mode == "map":
                out.append(binner_map.get(name, ""))
            print("\t".join(out))

if __name__ == "__main__":
    main()