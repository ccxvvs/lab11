#!/usr/bin/env python3
import re, os

PROTEIN_SEQ = "YELPEDPRWELPRDRLVLGKPLGEGAFGQVVLAEAIGLDKDKPNRVTKVAVKMLKSDATEKDLSDLISEMEMMKMIGKHKNIINLLGACTQDGPLYVIVEYASKGNLREYLQARRPEQLSSKDLVSCAYQVARGMEYLASKKCIHRLAARNVLVTEDNVMKIADFGLARDHIDYYKKTTNGRLPVKWMAPEALFDRIYTHQSDVWSFGVLLWEIFTLGGSPYPGVPVEELFKLLKEGHRMDKPSNCTNELYMMMRDCWHAVPSQRPTFKQLVEDLDRIVALTS"

YAML_TEMPLATE = """sequences:
- protein:
    id: A
    sequence: {protein_seq}
- ligand:
    id: B
    smiles: '{smiles}'
properties:
- affinity:
    binder: B
"""

def extract_smiles_and_names(mol2_file):
    molecules = []
    with open(mol2_file) as f:
        content = f.read()
    blocks = content.split("@<TRIPOS>MOLECULE")
    for block in blocks[1:]:
        lines = block.strip().split("\n")
        name = lines[0].strip()
        smiles = None
        for line in lines:
            if "RD_SMILES" in line:
                match = re.match(r"#+\s+RD_SMILES:\s*(.+)", line.strip())
                if match:
                    smiles = match.group(1).strip()
                    break
        if smiles:
            molecules.append((name, smiles))
    return molecules

mol2_file = "selected_mols.mol2"
output_dir = "boltz_2_runs"
os.makedirs(output_dir, exist_ok=True)

molecules = extract_smiles_and_names(mol2_file)
print(f"Found {len(molecules)} molecules with SMILES\n")

for i, (name, smiles) in enumerate(molecules, 1):
    yaml_content = YAML_TEMPLATE.format(protein_seq=PROTEIN_SEQ, smiles=smiles)
    yaml_file = os.path.join(output_dir, f"boltz_{name}.yaml")
    with open(yaml_file, "w") as f:
        f.write(yaml_content)
    print(f"  {i}. {name}: {yaml_file}")
    print(f"     SMILES: {smiles}")

run_script = os.path.join(output_dir, "run_all_boltz.sh")
with open(run_script, "w") as f:
    f.write("#!/bin/bash\n")
    for name, smiles in molecules:
        f.write(f"echo 'Running Boltz-2 for {name}...'\n")
        f.write(f"boltz predict boltz_{name}.yaml --out_dir results_{name}\n\n")
    f.write("echo 'All done!'\n")
os.chmod(run_script, 0o755)

print(f"\nYaml files written to: {output_dir}/")
print(f"Run script: {run_script}")
