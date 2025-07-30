#!/usr/bin/env python3
"""
MagTrans – Magnetic Transition Estimator

MATE is a unified framework that:
  • Enumerates collinear magnetic configurations,
  • Performs ab initio relaxations, static and SOC calculations,
  • Fits a Heisenberg + anisotropy Hamiltonian, and
  • Runs Monte Carlo simulations to determine magnetic transition temperatures 
    (Curie and Néel) in 1D, 2D, and 3D systems.

Author:
    Chinedu Ekuma
    Department of Physics, Lehigh University, Bethlehem, PA, USA
    Emails: cekuma1@gmail.com, che218@lehigh.edu

Copyright (c) 2025, Lehigh University, Department of Physics.  
All rights reserved.

License: [Insert License Here: e.g., MIT, BSD, GPL, etc.]

This module defines the ExchangeFileGenerator class that:
  1. Parses a parameter file (params.txt) for exchange constants and lattice repeat.
  2. Reads a structure file (CIF or VASP POSCAR) using pymatgen, converts it to its primitive
     cell and then to a conventional standard cell.
  3. Writes out structure information (unit cell size, normalized unit cell vectors, and atomic
     positions) to an output file.
  4. Appends a bond (exchange) list (in UC.ucf style) to the same output file.
  
The final output file (Jij.txt) has the following format:

# Unit cell size:
a   b   c
# Unit cell vectors:
1.0 0.0 0.0
0.0 1.0 0.0
0.0 0.0 1.0

# Atoms num, id cx cy cz mat lc hc
<number of atoms>
0   cx   cy   cz   mat   lc   hc
1   cx   cy   cz   mat   lc   hc
...

# -------------------------------------------
# Exchange interactions
<number_of_bonds> <exchangeT>
<bond line 0>
<bond line 1>
...

"""

import re
import sys
import warnings
import numpy as np
from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# Suppress CIF parsing warnings from pymatgen
warnings.filterwarnings("ignore", category=UserWarning, module="pymatgen.io.cif")


class ExchangeFileGenerator:
    """
    Generates an output file containing structure information and exchange interactions.
    """
    def __init__(self, input_mc_file="input_MC", rep_DFT=[1,1,1], structure_file="POSCAR", exch_type = 'isotropic', outfile="Jij.txt"):
        self.input_mc_file = input_mc_file
        self.rep_DFT = rep_DFT
        self.structure_file = structure_file
        self.outfile = outfile
        self.params = self.parse_input_mc(self.input_mc_file)
        self.EV_TO_J = 1.602176634e-19
        self.exch_type = exch_type.lower()

    def parse_input_mc(self, filename):
        """
        Parses key = value pairs from the input_MC file.
        Expected keys include:
          J1 (eV/link), J2 (eV/link), J3 (eV/link), J4 (eV/link),
          K1x (eV/link), K1y (eV/link), K1z (eV/link),
          K2x (eV/link), K2y (eV/link), K2z (eV/link),
          K3x (eV/link), K3y (eV/link), K3z (eV/link),
          K4x (eV/link), K4y (eV/link), K4z (eV/link),
          Ax (eV/mag_atom), Ay (eV/mag_atom), Az (eV/mag_atom),
          exchangeT (optional, default "tensorial")
        """
        params = {}
        float_pattern = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    left, right = line.split('=', 1)
                    # Remove any parenthesized units from key
                    key = re.sub(r"\(.*?\)", "", left).strip()
                    val_str = right.strip()
                    found = float_pattern.findall(val_str)
                    if len(found) == 1:
                        try:
                            val = float(found[0])
                        except:
                            val = val_str
                    elif len(found) > 1:
                        val = [float(x) for x in found]
                    else:
                        val = val_str
                    params[key] = val
        return params

    def build_neighbor_offsets_2D(self, J1, J2, J3, J4, K1, K2, K3, K4):
        """Build 2D neighbor offsets for a square lattice."""
        offsets = {}
        if (abs(J1) > 1e-30) or (abs(K1['Kx']) > 1e-30 or abs(K1['Ky']) > 1e-30 or abs(K1['Kz']) > 1e-30):
            offsets[1] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if (abs(J2) > 1e-30) or (abs(K2['Kx']) > 1e-30 or abs(K2['Ky']) > 1e-30 or abs(K2['Kz']) > 1e-30):
            offsets[2] = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        if (abs(J3) > 1e-30) or (abs(K3['Kx']) > 1e-30 or abs(K3['Ky']) > 1e-30 or abs(K3['Kz']) > 1e-30):
            offsets[3] = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        if (abs(J4) > 1e-30) or (abs(K4['Kx']) > 1e-30 or abs(K4['Ky']) > 1e-30 or abs(K4['Kz']) > 1e-30):
            offsets[4] = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                          (1, 2), (1, -2), (-1, 2), (-1, -2)]
        return offsets

    def build_neighbor_offsets_3D(self, J1, J2, J3, J4, K1, K2, K3, K4):
        """Build 3D neighbor offsets for a simple cubic lattice."""
        offsets = {}
        if (abs(J1) > 1e-30) or (abs(K1['Kx']) > 1e-30 or abs(K1['Ky']) > 1e-30 or abs(K1['Kz']) > 1e-30):
            offsets[1] = [(1, 0, 0), (-1, 0, 0),
                          (0, 1, 0), (0, -1, 0),
                          (0, 0, 1), (0, 0, -1)]
        if (abs(J2) > 1e-30) or (abs(K2['Kx']) > 1e-30 or abs(K2['Ky']) > 1e-30 or abs(K2['Kz']) > 1e-30):
            off2 = []
            off2 += [(1, 1, 0), (1, -1, 0), (-1, 1, 0), (-1, -1, 0)]
            off2 += [(1, 0, 1), (1, 0, -1), (-1, 0, 1), (-1, 0, -1)]
            off2 += [(0, 1, 1), (0, 1, -1), (0, -1, 1), (0, -1, -1)]
            offsets[2] = off2
        if (abs(J3) > 1e-30) or (abs(K3['Kx']) > 1e-30 or abs(K3['Ky']) > 1e-30 or abs(K3['Kz']) > 1e-30):
            off3 = []
            for sx in [1, -1]:
                for sy in [1, -1]:
                    for sz in [1, -1]:
                        off3.append((sx, sy, sz))
            offsets[3] = off3
        if (abs(J4) > 1e-30) or (abs(K4['Kx']) > 1e-30 or abs(K4['Ky']) > 1e-30 or abs(K4['Kz']) > 1e-30):
            offsets[4] = [(2, 0, 0), (-2, 0, 0),
                          (0, 2, 0), (0, -2, 0),
                          (0, 0, 2), (0, 0, -2)]
        return offsets

    def write_structure_info(self):
        """
        Reads the structure file, converts to primitive then conventional structure,
        and writes the structure information to the output file.
        """
        try:
            struct = Structure.from_file(self.structure_file)
        except Exception as e:
            print(f"Error reading structure from {self.structure_file}: {e}")
            sys.exit(1)
        
        # Convert to primitive and then to conventional standard structure.
        prim_struct = struct.get_primitive_structure(use_site_props=True)
        sga = SpacegroupAnalyzer(prim_struct, symprec=0.01)
        standard_struct = sga.get_conventional_standard_structure()
        
        # Extract lattice parameters and vectors.
        a_val = standard_struct.lattice.a
        b_val = standard_struct.lattice.b
        c_val = standard_struct.lattice.c
        lattice_vectors = standard_struct.lattice.matrix  # 3x3 matrix

        tol = 1e-3
        is_cubic = np.isclose(a_val, b_val, atol=tol) and np.isclose(b_val, c_val, atol=tol)
        if is_cubic:
            out_vectors = np.array([[1.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0],
                                    [0.0, 0.0, 1.0]])
        else:
            out_vectors = lattice_vectors
        
        with open(self.outfile, "w") as f:
            f.write("# Data has been obtained using Curie2D Software. Please cite the main paper if you have used this code \n")
            f.write("# Unit cell size:\n")
            f.write(f"{a_val:.8f} {b_val:.8f} {c_val:.8f}\n")
            f.write("# Unit cell vectors:\n")
            for vec in out_vectors:
                f.write(f"{vec[0]:.8f} {vec[1]:.8f} {vec[2]:.8f}\n")
            f.write("# Atoms num, id cx cy cz mat lc hc\n")
            num_atoms = len(standard_struct)
            f.write(f"{num_atoms}\n")
            for i, site in enumerate(standard_struct):
                cx, cy, cz = site.frac_coords
                if i == 0:
                    mat, lc, hc = 0, 1, 0
                else:
                    mat, lc, hc = 1, 0, 1
                f.write(f"{i:<8d} {cx:<17.15f} {cy:<17.15f} {cz:<17.15f} {mat:<8d} {lc:<8d} {hc:<8d}\n")

    def write_exchange_file(self, shell_data, neighbor_offsets):
        """
        Appends the exchange bond list to the structure information in the outfile.
        """
        self.write_structure_info()

        with open(self.outfile, "a") as f:
            f.write("#Interactions n exctype, id i j dx dy   dz        Jij \n")

        # Use rep_DFT dimensions
        rep = self.rep_DFT
        Nx, Ny = int(rep[0]), int(rep[1])
        Nz = int(rep[2]) if len(rep) >= 3 else 1

        def site_index(x, y, z=0):
            return x + Nx * (y + Ny * z)
        def pbc_x(x): return x % Nx
        def pbc_y(y): return y % Ny
        def pbc_z(z): return z % Nz

        bond_lines = []
        line_index = 0
        exchangeT = self.exch_type
        if Nz == 1:
            # 2D system
            for n, offsets_list in neighbor_offsets.items():
                J_val = shell_data[n]['J']
                Kx_val = shell_data[n]['Kx']
                Ky_val = shell_data[n]['Ky']
                Kz_val = shell_data[n]['Kz']
                for x in range(Nx):
                    for y in range(Ny):
                        i = site_index(x, y)
                        for (dx, dy) in offsets_list:
                            x2 = pbc_x(x+dx)
                            y2 = pbc_y(y+dy)
                            j = site_index(x2, y2)
                            if j <= i: continue
                            if exchangeT.lower() == "isotropic":
                                bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t0\t{J_val:e}")
                                line_index += 1
                            elif exchangeT.lower() == "tensorial":
                                if abs(Kx_val) > 1e-30:
                                    bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t0\t{Kx_val:e}")
                                    line_index += 1
                                if abs(Ky_val) > 1e-30:
                                    bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t0\t{Ky_val:e}")
                                    line_index += 1
                                if abs(Kz_val) > 1e-30:
                                    bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t0\t{Kz_val:e}")
                                    line_index += 1
                            else:
                                raise ValueError("exchangeT must be 'isotropic' or 'tensorial'")
        else:
            # 3D system (similar logic, including dz)
            for n, offsets_list in neighbor_offsets.items():
                J_val = shell_data[n]['J']
                Kx_val = shell_data[n]['Kx']
                Ky_val = shell_data[n]['Ky']
                Kz_val = shell_data[n]['Kz']
                for x in range(Nx):
                    for y in range(Ny):
                        for z in range(Nz):
                            i = site_index(x, y, z)
                            for (dx, dy, dz) in offsets_list:
                                x2 = pbc_x(x+dx)
                                y2 = pbc_y(y+dy)
                                z2 = pbc_z(z+dz)
                                j = site_index(x2, y2, z2)
                                if j <= i: continue
                                if exchangeT.lower() == "isotropic":
                                    bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t{dz}\t{J_val:e}")
                                    line_index += 1
                                elif exchangeT.lower() == "tensorial":
                                    if abs(Kx_val) > 1e-30:
                                        bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t{dz}\t{Kx_val:e}")
                                        line_index += 1
                                    if abs(Ky_val) > 1e-30:
                                        bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t{dz}\t{Ky_val:e}")
                                        line_index += 1
                                    if abs(Kz_val) > 1e-30:
                                        bond_lines.append(f"{line_index}\t{i}\t{j}\t{dx}\t{dy}\t{dz}\t{Kz_val:e}")
                                        line_index += 1
                                else:
                                    raise ValueError("exchangeT must be 'isotropic' or 'tensorial'")
        
        total_lines = len(bond_lines)
        with open(self.outfile, 'a') as f:
            f.write(f"{total_lines} {exchangeT.lower()}\n")
            for line in bond_lines:
                f.write(line + "\n")
    
    def process_exchange(self):
        """
        Main workflow: computes exchange constants (from input_MC parameters),
        determines neighbor offsets based on 2D or 3D supercell dimensions (rep_DFT),
        and writes the combined structure/exchange file.
        """
        exchangeT = self.exch_type #self.params.get('exchangeT', "tensorial")
        rep = self.rep_DFT
        Nx, Ny = int(rep[0]), int(rep[1])
        Nz = int(rep[2]) if len(rep) >= 3 else 1

        # Read exchange shells (in eV) from input_MC
        J1_eV = self.params.get('J1', 0.01)
        J2_eV = self.params.get('J2', 0.005)
        J3_eV = self.params.get('J3', 0.0)
        J4_eV = self.params.get('J4', 0.0)
        
        K1x_eV = self.params.get('K1x', 0.002)
        K1y_eV = self.params.get('K1y', 0.002)
        K1z_eV = self.params.get('K1z', 0.0)
        K2x_eV = self.params.get('K2x', 0.0)
        K2y_eV = self.params.get('K2y', 0.0)
        K2z_eV = self.params.get('K2z', 0.0)
        K3x_eV = self.params.get('K3x', 0.0)
        K3y_eV = self.params.get('K3y', 0.0)
        K3z_eV = self.params.get('K3z', 0.0)
        K4x_eV = self.params.get('K4x', 0.0)
        K4y_eV = self.params.get('K4y', 0.0)
        K4z_eV = self.params.get('K4z', 0.0)
        
        Ax_eV  = self.params.get('Ax', 0.0)
        Ay_eV  = self.params.get('Ay', 0.0)
        Az_eV  = self.params.get('Az', 0.0)
        
        # Convert to Joules
        J1 = J1_eV * self.EV_TO_J
        J2 = J2_eV * self.EV_TO_J
        J3 = J3_eV * self.EV_TO_J
        J4 = J4_eV * self.EV_TO_J

        K1 = {
            'Kx': K1x_eV * self.EV_TO_J,
            'Ky': K1y_eV * self.EV_TO_J,
            'Kz': K1z_eV * self.EV_TO_J
        }
        K2 = {
            'Kx': K2x_eV * self.EV_TO_J,
            'Ky': K2y_eV * self.EV_TO_J,
            'Kz': K2z_eV * self.EV_TO_J
        }
        K3 = {
            'Kx': K3x_eV * self.EV_TO_J,
            'Ky': K3y_eV * self.EV_TO_J,
            'Kz': K3z_eV * self.EV_TO_J
        }
        K4 = {
            'Kx': K4x_eV * self.EV_TO_J,
            'Ky': K4y_eV * self.EV_TO_J,
            'Kz': K4z_eV * self.EV_TO_J
        }
        shell_data = {
            1: {'J': J1, 'Kx': K1['Kx'], 'Ky': K1['Ky'], 'Kz': K1['Kz']},
            2: {'J': J2, 'Kx': K2['Kx'], 'Ky': K2['Ky'], 'Kz': K2['Kz']},
            3: {'J': J3, 'Kx': K3['Kx'], 'Ky': K3['Ky'], 'Kz': K3['Kz']},
            4: {'J': J4, 'Kx': K4['Kx'], 'Ky': K4['Ky'], 'Kz': K4['Kz']}
        }
        
        if Nz == 1:
            neighbor_offsets = self.build_neighbor_offsets_2D(J1, J2, J3, J4, K1, K2, K3, K4)
        else:
            neighbor_offsets = self.build_neighbor_offsets_3D(J1, J2, J3, J4, K1, K2, K3, K4)
        
        self.write_exchange_file(shell_data, neighbor_offsets)
        print(f"File '{self.outfile}' written successfully.")
        
    def run(self):
        """Convenience method to process and generate the exchange file."""
        self.process_exchange()

# Uncomment to run as a standalone
#def main():
#    generator = ExchangeFileGenerator()
#    generator.run()


#if __name__ == "__main__":
#    main()

