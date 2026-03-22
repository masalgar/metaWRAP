#!/usr/bin/env python2.7
from __future__ import print_function
import sys
import csv
import os

"""
Usage:
  # 1) No binner column:
  python2.7 summarize_checkm.py quality_report.tsv > sample.stats.txt

  # 2) Fixed binner label (adds trailing 'binner' column with same label on all rows):
  python2.7 summarize_checkm.py quality_report.tsv BINNER_LABEL > sample.stats.txt

  # 3) Source map TSV (adds trailing 'binner' column from map's 8th column, keyed by bin name in col 1):
  python2.7 summarize_checkm.py quality_report.tsv source_map.tsv > sample.stats.txt

Input (CheckM2 TSV) must contain at least these headers:
  Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size

Output columns (tab-separated):
  bin  completeness  contamination  GC  lineage  N50  size  [binner]

Notes:
  - CheckM2 does not provide lineage -> 'lineage' is set to "NA".
  - To mimic the original script's appearance, numeric strings for
    completeness/contamination/GC are truncated to 5 characters.
  - N50 and size are printed as-is (no truncation).
"""

def fmt5(x):
    """Mimic the old script's simple 5-char truncation for floats/strings."""
    if x is None:
        return ""
    s = str(x)
    return s[:5]

def load_source_map(path):
    """Return {bin_name: binner_label} from a TSV whose 1st col is bin, 8th col is binner."""
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
    if len(sys.argv) not in (2, 3):
        sys.stderr.write(
            "Usage:\n"
            "  {} quality_report.tsv\n"
            "  {} quality_report.tsv BINNER_LABEL\n"
            "  {} quality_report.tsv SOURCE_MAP_TSV\n".format(sys.argv[0], sys.argv[0], sys.argv[0])
        )
        sys.exit(1)

    in_path = sys.argv[1]

    # Determine binner mode:
    have_binner = False
    binner_fixed = None
    binner_map = None

    if len(sys.argv) == 3:
        arg2 = sys.argv[2]
        # Heuristic: if arg2 is an existing file, treat as source map; otherwise a fixed label
        if os.path.isfile(arg2):
            binner_map = load_source_map(arg2)
            have_binner = True
        else:
            binner_fixed = arg2
            have_binner = True

    # Print header
    base_cols = ["bin", "completeness", "contamination", "GC", "lineage", "N50", "size"]
    if have_binner:
        print("\t".join(base_cols + ["binner"]))
    else:
        print("\t".join(base_cols))

    # Parse CheckM2 quality_report.tsv
    with open(in_path, "r") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        # Expected headers:
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
            if binner_fixed is not None:
                out.append(binner_fixed)
            elif binner_map is not None:
                out.append(binner_map.get(name, ""))
            print("\t".join(out))

if __name__ == "__main__":
    main()