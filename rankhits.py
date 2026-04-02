#!/usr/bin/env python3
import re, csv, sys

SCORE_KEYS = [
    "Continuous_Score",
    "Footprint_Similarity_Score",
    "Hungarian_Matching_Similarity_Score",
    "Property_Volume_Score",
]
HIGHER_IS_BETTER = {"Property_Volume_Score"}

def parse_mol2(filepath):
    with open(filepath) as f:
        content = f.read()
    blocks = content.split("@<TRIPOS>MOLECULE")
    molecules = []
    for block in blocks[1:]:
        mol = {"_raw": "@<TRIPOS>MOLECULE" + block}
        lines = block.strip().split("\n")
        mol["name"] = lines[0].strip()
        for line in lines:
            if line.strip().startswith("##"):
                match = re.match(r"#+\s+(.+?):\s+(.+)", line.strip())
                if match:
                    key = match.group(1).strip()
                    val = match.group(2).strip()
                    try:
                        mol[key] = float(val)
                    except ValueError:
                        mol[key] = val
        molecules.append(mol)
    return molecules

if len(sys.argv) < 2:
    print("Usage: python rankhits.py <input.mol2>")
    sys.exit(1)

filepath = sys.argv[1]
print(f"Parsing {filepath}...")
mols = parse_mol2(filepath)
print(f"Found {len(mols)} molecules\n")

available = []
for key in SCORE_KEYS:
    if key in mols[0]:
        available.append(key)
        print(f"  Found: {key}")
    else:
        print(f"  WARNING: {key} not found! Skipping.")

print(f"\nRanking by: {available}")

for key in available:
    reverse = key in HIGHER_IS_BETTER
    sorted_mols = sorted(mols, key=lambda m: m.get(key, 9999), reverse=reverse)
    direction = "higher=better" if reverse else "lower=better"
    print(f"\n{'='*70}")
    print(f"TOP 20 by {key} ({direction})")
    print(f"{'='*70}")
    print(f"  {'Rank':<6}{'Name':<25}{key:>25}")
    print(f"  {'-'*56}")
    for i, mol in enumerate(sorted_mols[:20], 1):
        val = mol.get(key, "N/A")
        if isinstance(val, float):
            print(f"  {i:<6}{mol['name'][:23]:<25}{val:>25.3f}")

print(f"\n{'='*70}")
print("COMBINED RANKING")
print(f"{'='*70}")

for key in available:
    reverse = key in HIGHER_IS_BETTER
    sorted_indices = sorted(range(len(mols)),
                            key=lambda i: mols[i].get(key, 9999),
                            reverse=reverse)
    for rank, idx in enumerate(sorted_indices, 1):
        mols[idx][f"_rank_{key}"] = rank

for mol in mols:
    ranks = [mol[f"_rank_{key}"] for key in available]
    mol["_avg_rank"] = sum(ranks) / len(ranks)

mols.sort(key=lambda m: m["_avg_rank"])

header = f"  {'#':<4}{'Name':<22}{'AvgRank':>8}"
for k in available:
    short = k[:18]
    header += f"  {short:>18}"
print(header)
print(f"  {'-'*(len(header)-2)}")

for i, mol in enumerate(mols[:30], 1):
    row = f"  {i:<4}{mol['name'][:20]:<22}{mol['_avg_rank']:>8.1f}"
    for k in available:
        val = mol.get(k, "N/A")
        if isinstance(val, float):
            row += f"  {val:>18.3f}"
    print(row)

TOP_N = 10
out_mol2 = "selected_mols.mol2"
with open(out_mol2, "w") as f:
    for mol in mols[:TOP_N]:
        f.write(mol["_raw"])
        if not mol["_raw"].endswith("\n"):
            f.write("\n")

print(f"\nTop {TOP_N} molecules written to: {out_mol2}")

out_csv = "all_molecules_ranked.csv"
fields = ["avg_rank", "name"] + available + [f"rank_{k}" for k in available]
with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(fields)
    for mol in mols:
        row = [mol["_avg_rank"], mol["name"]]
        row += [mol.get(k, "") for k in available]
        row += [mol.get(f"_rank_{k}", "") for k in available]
        writer.writerow(row)

print(f"Full rankings saved to: {out_csv}")
print(f"\nNext: open selected_mols.mol2 in ChimeraX with the receptor to visually check poses")
