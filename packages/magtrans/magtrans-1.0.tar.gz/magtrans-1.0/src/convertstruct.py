#!/usr/bin/env python
"""
This script reads a structure file (CIF or VASP format) using pymatgen,
converts it to its primitive structure and then to a conventional standard cell,
and writes out a text file ("teststruct.txt") in the format:

# Unit cell size:
a   b   c
# Unit cell vectors:
v1_x v1_y v1_z
v2_x v2_y v2_z
v3_x v3_y v3_z

# Atoms num, id cx cy cz mat lc hc 
<number of atoms>
0       cx cy cz  mat lc hc
1       cx cy cz  mat lc hc
...

For cubic structures the lattice vectors are normalized to [1,0,0],
[0,1,0], and [0,0,1]. For non-cubic cells the full lattice vectors
(as determined by the conventional cell) are written.
 
"""

import sys
import warnings
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import numpy as np

# Suppress CIF parsing warnings from pymatgen
warnings.filterwarnings("ignore", category=UserWarning, module="pymatgen.io.cif")

def main():
    if len(sys.argv) < 2:
        print("Usage: python write_teststruct.py <structure_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        struct = Structure.from_file(input_file)
    except Exception as e:
        print(f"Error reading structure from {input_file}: {e}")
        sys.exit(1)
    
    # Convert to primitive cell to avoid redundancy.
    prim_struct = struct.get_primitive_structure(use_site_props=True)
    
    # Get the conventional standard structure.
    sga = SpacegroupAnalyzer(prim_struct, symprec=0.01)
    standard_struct = sga.get_conventional_standard_structure()
    
    # Extract lattice parameters and lattice vectors.
    a = standard_struct.lattice.a
    b = standard_struct.lattice.b
    c = standard_struct.lattice.c
    lattice_vectors = standard_struct.lattice.matrix  # 3x3 matrix

    # Check if the cell is cubic (within a tolerance)
    tol = 1e-3
    is_cubic = np.isclose(a, b, atol=tol) and np.isclose(b, c, atol=tol)
    
    if is_cubic:
        # For cubic cells, we output the normalized lattice vectors.
        out_vectors = np.array([[1.0, 0.0, 0.0],
                                [0.0, 1.0, 0.0],
                                [0.0, 0.0, 1.0]])
    else:
        # For non-cubic cells, output the full conventional lattice vectors.
        out_vectors = lattice_vectors

    output_file = "teststruct.txt"
    with open(output_file, "w") as f:
        # Write the unit cell size.
        f.write("# Unit cell size:\n")
        f.write(f"{a:.6f}   {b:.6f}   {c:.6f}\n")
        # Write the unit cell vectors.
        f.write("# Unit cell vectors:\n")
        for vec in out_vectors:
            f.write(f"{vec[0]:.6f} {vec[1]:.6f} {vec[2]:.6f}\n")
        f.write("\n")
        
        # Write atomic positions.
        # We'll use the conventional structure's sites.
        f.write("# Atoms num, id cx cy cz mat lc hc\n")
        num_atoms = len(standard_struct)
        f.write(f"{num_atoms}\n")
        for i, site in enumerate(standard_struct):
            cx, cy, cz = site.frac_coords
            # Here we mimic the sample: for the first atom, assign mat=0, lc=1, hc=0;
            # for subsequent atoms, assign mat=1, lc=0, hc=1.
            if i == 0:
                mat, lc, hc = 0, 1, 0
            else:
                mat, lc, hc = 1, 0, 1
            f.write(f"{i:<8d} {cx:<8.6f} {cy:<8.6f} {cz:<8.6f} {mat:<8d} {lc:<8d} {hc:<8d}\n")
    
    print(f"Structure information written to {output_file}")

if __name__ == "__main__":
    main()

