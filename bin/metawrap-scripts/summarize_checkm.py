#!/usr/bin/env python2.7
from __future__ import print_function
import sys
import csv

"""
Usage:
  python2.7 quality_to_stats.py quality_report.tsv > sample.stats.txt

Input (TSV) must contain at least these headers:
  Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size

Output columns (tab-separated):
  bin  completeness  contamination  GC  lineage  N50  size

Notes:
  - Checkm2 does not provide lineage. The lineage column is always set to "NA" to keep structure of original CheckM.
  - To mimic the original scrip's appearance, numeric fields
    for completeness/contamination/GC are truncated to 5 chars.
  - N50 and size are printed as-is (no truncation), like the original.
"""

def fmt5(x):
    """Mimic old script's simple 5-char truncation for floats."""
    if x is None:
        return ""
    s = str(x)
    return s[:5]  # crude truncation (e.g., "96.176" -> "96.17")

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: {} quality_report.tsv\n".format(sys.argv[0]))
        sys.exit(1)

    in_path = sys.argv[1]

    # Print header exactly as expected by downstream tools
    print("bin\tcompleteness\tcontamination\tGC\tlineage\tN50\tsize")

    with open(in_path, "r") as f:
        rdr = csv.DictReader(f, delimiter="\t")
        for row in rdr:
            # Pull required fields (use empty string if missing)
            name = row.get("Name", "")
            comp = row.get("Completeness", "")
            cont = row.get("Contamination", "")
            gc   = row.get("GC_Content", "")
            n50  = row.get("Contig_N50", "")
            size = row.get("Genome_Size", "")

            # lineage is fixed to "NA"
            lineage = "NA"

            out = [
                name,
                fmt5(comp),
                fmt5(cont),
                fmt5(gc),
                lineage,
                str(n50),
                str(size),
            ]
            print("\t".join(out))

if __name__ == "__main__":
    main()