#!/usr/bin/env python2.7
from __future__ import print_function
import sys
import csv
import os

"""
Contract (matches original metaWRAP usage):

1) summarize_checkm.py quality_report.tsv
   -> prints: bin  completeness  contamination  GC  lineage  N50  size

2) summarize_checkm.py quality_report.tsv BINSET
   -> prints the same + trailing 'binner' column with BINSET for all rows

3) summarize_checkm.py quality_report.tsv manual binsM.stats
   -> ignores the 2nd arg ('manual'); uses binsM.stats as a source map:
      key = bin name (col 1), value = binner label (col 8)
      If binsM.stats has a header and includes a 'binner' column, that column
      is used instead of col 8. Missing keys yield empty binner (no crash).

Input: CheckM2 quality_report.tsv (tab-delimited) with columns similar to:
  Name, Completeness, Contamination, GC_Content, Contig_N50, Genome_Size
Column names are matched case-insensitively with common synonyms.
"""

# ---- helpers ----

def fmt5(x):
    if x is None:
        return ""
    s = str(x)
    return s[:5]  # mimic legacy 5-char truncation

def index_of(header, candidates):
    """Return first matching index in header (case-insensitive), else -1."""
    lower = [h.strip().lower() for h in header]
    for cand in candidates:
        cl = cand.strip().lower()
        if cl in lower:
            return lower.index(cl)
    return -1

def detect_indices(header):
    """
    Build a dict of required column indices from a CheckM2 header.
    Robust to small naming variations.
    """
    need = {
        'name':      ['Name', 'Bin', 'bin', 'name'],
        'comp':      ['Completeness', 'completeness', 'Completeness (%)', 'Completeness_%'],
        'cont':      ['Contamination', 'contamination', 'Contamination (%)', 'Contamination_%'],
        'gc':        ['GC_Content', 'GC Content', 'GC', 'gc_content', 'gc'],
        'n50':       ['Contig_N50', 'N50', 'Contig N50'],
        'size':      ['Genome_Size', 'Genome Size', 'Genome_size', 'Genome size', 'GenomeSize', 'Genome Size (bp)'],
    }
    idx = {}
    for key, cands in need.items():
        i = index_of(header, cands)
        if i < 0:
            return None
        idx[key] = i
    return idx

def load_source_map(path):
    """
    Return {bin_name: binner_label} from TSV.
    Primary behavior (original): use column 8 (index 7).
    Graceful header handling: if header row has a 'binner' column, use that index.
    """
    src = {}
    if not os.path.isfile(path):
        return src

    with open(path, 'r') as f:
        first = f.readline()
        if not first:
            return src
        cols = first.rstrip('\n').split('\t')

        # Detect header and binner column
        is_header = (cols and cols[0].strip().lower() == 'bin')
        binner_col = 7  # original behavior: 8th column
        if is_header:
            # if header has 'binner', use that; else keep 7 if present
            b_idx = index_of(cols, ['binner'])
            if b_idx >= 0:
                binner_col = b_idx

        # If first line was header, continue; else process it too
        if not is_header:
            if len(cols) > 0:
                name = cols[0]
                label = cols[binner_col] if len(cols) > binner_col else ''
                src[name] = label

        # Remaining lines
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if not parts:
                continue
            name = parts[0]
            label = parts[binner_col] if len(parts) > binner_col else ''
            src[name] = label

    return src

# ---- main ----

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

    mode = 'plain'       # 1 arg -> no binner
    binner_fixed = None  # 2 args -> fixed label
    binner_map   = None  # 3 args -> per-bin map (ignore argv[2])

    if argc == 3:
        mode = 'fixed'
        binner_fixed = sys.argv[2]
    elif argc == 4:
        mode = 'map'
        # ignore sys.argv[2] (e.g. 'manual'), use sys.argv[3] as mapping file
        binner_map = load_source_map(sys.argv[3])

    # Read header to detect columns robustly
    with open(in_path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader, None)
        if header is None:
            sys.stderr.write("ERROR: empty quality report: {}\n".format(in_path))
            sys.exit(2)
        idx = detect_indices(header)
        if idx is None:
            sys.stderr.write("ERROR: could not locate required columns in quality report header:\n  {}\n".format('\t'.join(header)))
            sys.exit(2)

        # Print header
        base = ["bin", "completeness", "contamination", "GC", "lineage", "N50", "size"]
        if mode in ('fixed', 'map'):
            print("\t".join(base + ["binner"]))
        else:
            print("\t".join(base))

        # Stream rows
        for row in reader:
            if not row:
                continue
            try:
                name = row[idx['name']]
            except IndexError:
                # malformed line; skip
                continue

            comp = row[idx['comp']] if idx['comp'] < len(row) else ''
            cont = row[idx['cont']] if idx['cont'] < len(row) else ''
            gc   = row[idx['gc']]   if idx['gc']   < len(row) else ''
            n50  = row[idx['n50']]  if idx['n50'] < len(row) else ''
            size = row[idx['size']] if idx['size'] < len(row) else ''

            out = [name, fmt5(comp), fmt5(cont), fmt5(gc), "NA", str(n50), str(size)]
            if mode == 'fixed':
                out.append(binner_fixed)
            elif mode == 'map':
                out.append(binner_map.get(name, ''))
            print("\t".join(out))

if __name__ == '__main__':
    main()