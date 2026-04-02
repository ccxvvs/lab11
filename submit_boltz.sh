#!/bin/bash
#SBATCH --job-name=boltz2
#SBATCH --account=bioinf595w26_class
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=boltz2_%j.log

cd /nfs/turbo/dcmb-class/bioinf595/sec001/parikhnn/bioinf_595_hit_picking_lab/boltz_2_runs

eval "$(conda shell.bash hook)"
conda activate boltz2

if ! command -v boltz &> /dev/null; then
    echo "ERROR: boltz command not found"
    exit 1
fi

echo "boltz found at: $(which boltz)"

for yaml in boltz_ZINC*.yaml; do
    name=$(basename "$yaml" .yaml | sed 's/boltz_//')
    echo "Running $name..."
    boltz predict "$yaml" --out_dir "results_${name}" --use_msa_server
    echo "Done with $name"
done
