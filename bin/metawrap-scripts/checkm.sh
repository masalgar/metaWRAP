#!/bin/bash -l
#
#SBATCH
#SBATCH --partition=lrgmem
#SBATCH --job-name=CheckM
#SBATCH --time=72:0:0
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=48
#SBATCH --cpus-per-task=1
#SBATCH --mem=800G

threads=48
mem=800

comm () { ${SOFT}/print_comment.py "$1" "-"; }
error () { ${SOFT}/print_comment.py "$1" "*"; exit 1; }
warning () { ${SOFT}/print_comment.py "$1" "*"; }
announcement () { ${SOFT}/print_comment.py "$1" "#"; }


source config-metawrap

# runs CheckM2 mini-pipeline on a single folder of bins
if [[ -d ${1}.checkm ]]; then rm -r ${1}.checkm; fi
comm "Running CheckM2 on $1 bins"
mkdir ${1}.tmp
conda run -n checkm2-env checkm2 predict -x fa -i $1 -o ${1}.checkm -t $threads --tmpdir ${1}.tmp
if [[ ! -s ${1}.checkm/quality_report.tsv ]]; then error "Something went wrong with running CheckM2. Exiting..."; fi
rm -r ${1}.tmp

comm "Finalizing CheckM2 stats..."
${SOFT}/summarize_checkm.py ${1}.checkm/quality_report.tsv > ${1}.stats

#comm "Making CheckM plot of $1 bins"
#checkm bin_qa_plot -x fa ${1}.checkm $1 ${1}.plot
#if [[ ! -s ${1}.plot/bin_qa_plot.png ]]; then warning "Something went wrong with making the CheckM plot. Exiting."; fi
#mv ${1}.plot/bin_qa_plot.png ${1}.png
#rm -r ${1}.plot


announcement "CheckM2 pipeline finished"
