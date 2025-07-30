#!/usr/bin/env python
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

Version: 1.0

Description:
    This code provides a complete workflow for magnetic transition analysis by 
    combining enumeration of magnetic configurations, ab initio relaxations, 
    Hamiltonian fitting, and Monte Carlo simulation in systems of varying dimensionality.
"""


import os, pickle
import sys
import datetime
import math
import numpy as np
from time import time, sleep
from shutil import copyfile
from pickle import load, dump
import logging
import matplotlib.pyplot as plt
import ast
from itertools import product,islice
import glob
from scipy.spatial import KDTree
from multiprocessing import Pool, cpu_count
from functools import lru_cache
import tempfile
try:
    from scipy.spatial import cKDTree          # periodic support since 1.8
except (ImportError, AttributeError):          # fall back for older SciPy
    raise RuntimeError(
        "SciPy ≥ 1.8 is required for periodic cKDTree support. "
        "Please upgrade (e.g. `pip install --upgrade scipy`)."
    )


# Pymatgen
from pymatgen.core import Structure, Element
from pymatgen.analysis.structure_matcher import StructureMatcher,ElementComparator
from pymatgen.analysis.magnetism.analyzer import CollinearMagneticStructureAnalyzer #,MagneticStructureEnumerator
from pymatgen.io.vasp.sets import MPRelaxSet, MPStaticSet, MPSOCSet
from pymatgen.io.vasp.inputs import Incar, Kpoints, Poscar
from pymatgen.io.vasp.outputs import Vasprun, Oszicar, Outcar
from pymatgen.command_line.bader_caller import bader_analysis_from_path
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.core.operations import SymmOp





# Custodian
from custodian.custodian import Custodian
from custodian.vasp.handlers import (
    VaspErrorHandler, UnconvergedErrorHandler,
    FrozenJobErrorHandler, MeshSymmetryErrorHandler,
    PositiveEnergyErrorHandler, StdErrHandler,
    NonConvergingErrorHandler, PotimErrorHandler
)
from custodian.vasp.jobs import VaspJob
from custodian.vasp.validators import VasprunXMLValidator

# ASE
from ase.io import read, write
from ase.build import sort

# Sympy, numba
from sympy import Symbol, linsolve, expand
from numpy.linalg import lstsq
import random
from numba import jit, cuda


#
import warnings
from pymatgen.io.vasp.sets import BadInputSetWarning
warnings.filterwarnings("ignore", category=BadInputSetWarning)
warnings.filterwarnings("ignore", category=EncodingWarning)
logging.getLogger('custodian').setLevel(logging.CRITICAL)


kB = np.double(8.6173303e-5)  # eV/K

__author__    = "Chinedu Ekuma"
__copyright__ = "Copyright 2025, Department of Physics, Lehigh University, Bethlehem, PA, USA"
__credits__   = ["Arnab Kabiraj"]  

###############################################################################
#               Global / Default Parameters
###############################################################################
root_path = os.getcwd()
start_time_global = time()

potential_symlink = "POT_GGA_PAW_PBE_54"

xc = 'PBE'
vacuum = 25
rep_DFT = [2, 2, 1]
strain = []
mag_prec = 0.1
enum_prec = 0.001
max_neigh = 4
randomise_cmd = False
mag_from = 'OSZICAR'
relx = True
GPU_accel = False
padding = True
dump_spins = True
nsim = 4
kpar = 1
npar = 1
ncore = 1
ismear = -5
sigma = 0.05
isif = 4
iopt = 3
system_dimension = '2D'
exchange_type = 'isotropic'
nccl = False
d_thresh = 0.05
d_buff = 0.01
acc = 'default'
LDAUJ_provided = {}
LDAUU_provided = {}
LDAUL_provided = {}
potcar_provided = {}
ldautype = 2
log_file = 'log'
skip = []
kpt_den_relx = None
kpt_den_stat = None
ltol = 0.4
stol = 0.6
atol = 5
mc_method = 1
encut = 520
lvdw = False
dftu = True
no_magstruct = 4

###############################################################################
# Utilities: replace_text, log, sanitize, etc.
###############################################################################
def replace_text(fileName,toFind,replaceWith):
    """Simple text replacement in fileName."""
    s = open(fileName).read()
    s = s.replace(toFind, replaceWith)
    with open(fileName,'w') as f:
        f.write(s)


def replace_or_add_input_tag(file, tag, new_value):
    import re
    found = False
    with open(file, 'r') as f:
        lines = f.readlines()

    with open(file, 'w') as f:
        for line in lines:
            if re.match(fr'^\s*{tag}\s*=', line):
                f.write(f'{tag} = {new_value}\n')
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f'{tag} = {new_value}\n')



def safe_symlinkold(src, dest):
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.lexists(dest):  # handles both files and broken symlinks
            os.remove(dest)

        os.symlink(src, dest)
        log(f"Linked: {dest} → {src}")

    except OSError as e:
        log(f"Symlink failed for {dest} → {src}: {e}. Attempting to copy instead...")
        try:
            copyfile(src, dest)
            log(f"Copied: {dest} ← {src}")
        except Exception as copy_err:
            log(f"Failed to copy {src} to {dest}: {copy_err}")
            sys.exit(1)
    except Exception as e:
        log(f"Unexpected error for {dest}: {e}")
        sys.exit(1)
        

def safe_symlink(src, dest, backup_dir=None, use_temp_copy=False):
    """
    Create a symbolic link from src to dest.

    - If dest exists, it is removed.
    - If use_temp_copy is True:
        • If backup_dir is specified, backup is created inside src's directory (as a subfolder).
        • If not specified, a temporary directory is used.
    - Falls back to copying if symlinking fails.
    """

    if not hasattr(safe_symlink, "_backup_map"):
        safe_symlink._backup_map = {}

    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        if use_temp_copy:
            abs_src = os.path.abspath(src)
            if abs_src in safe_symlink._backup_map:
                # Reuse the existing backup path
                backup_path = safe_symlink._backup_map[abs_src]
                log(f"Reusing existing backup for {src}: {backup_path}")
            else:
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_filename = f"{os.path.basename(src)}_{timestamp}"

                if backup_dir:
                    src_dir = os.path.dirname(abs_src)
                    full_backup_dir = os.path.join(src_dir, backup_dir)
                    os.makedirs(full_backup_dir, exist_ok=True)
                    backup_path = os.path.join(full_backup_dir, backup_filename)
                else:
                    temp_dir = tempfile.mkdtemp(prefix="backup_")
                    backup_path = os.path.join(temp_dir, backup_filename)

                copyfile(src, backup_path)
                safe_symlink._backup_map[abs_src] = backup_path
                log(f"Created backup for {src} → {backup_path}")

            src_for_link = backup_path
        else:
            src_for_link = src

        if os.path.lexists(dest):
            os.remove(dest)

        os.symlink(src_for_link, dest)
        log(f"Linked: {dest} → {src_for_link}")

    except OSError as e:
        log(f"Symlink failed for {dest} → {src_for_link}: {e}. Attempting to copy instead...")
        try:
            copyfile(src_for_link, dest)
            log(f"Copied: {dest} ← {src_for_link}")
        except Exception as copy_err:
            log(f"Failed to copy {src_for_link} to {dest}: {copy_err}")
            sys.exit(1)
    except Exception as e:
        log(f"Unexpected error for {dest}: {e}")
        sys.exit(1)





def safe_remove(path):
    try:
        if os.path.islink(path) or os.path.exists(path):
            os.remove(path)
            log(f"Removed {path}")
    except Exception as e:
        log(f"Could not remove {path}: {e}")


def log(string):
    """Write messages to stdout and a log file with timestamp."""
    debug_path = os.path.join(root_path, log_file) 
    string = str(string)
    with open(debug_path,'a+') as f:
        now = datetime.datetime.now()
        f.write('>>> '+str(now)+'    '+string+'\n')
    print('>>> '+string)



def sanitize(path):
    """
    Check if vasprun.xml in `path` is converged. If not, remove old input files
    so a new input can be prepared. Return True if converged or no problem, else False.
    """
    try:
        run = Vasprun(os.path.join(path,'vasprun.xml'))
        if run.converged:
            msg = f'Converged VASP run detected in {path}, no sanitization needed.'
            log(msg)
            return True
        else:
            #raise ValueError
            log(f"Warning: The VASP run in {path} did not converge.")
    except Exception as e:
        msg = str(e)
        log(msg)
        msg = ('Found unconverged, nonexistent or damaged VASP run in '+path
               +', starting sanitization')
        log(msg)
        try:
            # backup
            st_temp = Structure.from_file(os.path.join(path,'CONTCAR'))
            copyfile(os.path.join(path,'CONTCAR'), os.path.join(path,'CONTCAR.bk'))
            log('backed up CONTCAR')
        except Exception as e2:
            log(str(e2))
            log(f'no valid CONTCAR found in {path}')
        for ffile in [
            'INCAR','INCAR.orig','KPOINTS','KPOINTS.orig','POTCAR','POTCAR.orig'
        ]:
            try:
                os.remove(os.path.join(path, ffile))
            except:
                pass
        log('removed old INCAR, KPOINTS and POTCAR')
        return False


def dist_neighbors(struct):
    """
    For a 2D structure, replicate 20x20 in-plane, then find unique distances from site 0
    up to the first 15. Return them. Also do a small merging to handle numeric noise.
    """
    struct_l = struct.copy()
    struct_l.make_supercell([20,20,1])
    # distance_matrix[0] => distances from site 0 to all
    distances = np.unique(np.sort(np.around(struct_l.distance_matrix[0],2)))[0:15]
    dr_max = 0.01
    for i in range(len(distances)):
        for j in range(len(distances)):
            dr = abs(distances[i]-distances[j])
            if distances[j]<distances[i] and dr<d_thresh:
                distances[i] = distances[j]
                if dr>dr_max:
                    dr_max = dr
    distances = np.unique(distances)
    msg = f'neighbor distances are: {distances} ang'
    log(msg)
    msg = f'treating {dr_max} ang separated atoms as same neighbors'
    log(msg)
    distances[0] = dr_max + d_buff
    return distances


def find_max_len(lst):
    return max(len(sub) for sub in lst)

def make_homogenous(lst):
    """Pad each sublist to have the same length by appending '100000' sentinel."""
    max_len = find_max_len(lst)
    for i, sub in enumerate(lst):
        if len(sub)<max_len:
            sub += [100000]*(max_len - len(sub))
            lst[i] = sub


def Nfinder(struct_mag, site, d_N, dr):
    """
    CPU-based neighbor finder: return indices of neighbors of 'site' within
    [d_N - dr, d_N + dr].
    """
    N = len(struct_mag)
    coord_site = struct_mag.cart_coords[site]
    Ns = struct_mag.get_neighbors_in_shell(coord_site, d_N, dr)
    candidates = []
    for nbr in Ns:
        c_wrapped = nbr[0].to_unit_cell()
        for j in range(N):
            if struct_mag[j].distance(c_wrapped)<0.01:
                candidates.append(j)
                break
    return candidates

@cuda.jit
def my_kernel(all_coords, coord_N, index):
    """
    GPU kernel to find which site in all_coords is ~0.01 from coord_N.
    Store that site index in index[0].
    """
    pos = cuda.grid(1)
    if pos <= all_coords.size - 3:
        dx = (all_coords[pos]   - coord_N[0])**2
        dy = (all_coords[pos+1] - coord_N[1])**2
        dz = (all_coords[pos+2] - coord_N[2])**2
        if math.sqrt(dx+dy+dz)<0.01:
            index[0] = pos//3

def Nfinder_GPU(struct_mag, site, d_N, dr, all_coords):
    """
    GPU-based neighbor finder. 
    `all_coords` is a flatten (N*3,) array of site coords.
    """
    Ns = struct_mag.get_neighbors_in_shell(struct_mag[site].coords, d_N, dr)
    candidates = []
    for nbr in Ns:
        c_wrapped = nbr[0].to_unit_cell()
        coord_N = np.array([c_wrapped.x, c_wrapped.y, c_wrapped.z], dtype='float32')
        index = np.array([-5], dtype=np.int32)
        threadsperblock = 128
        blockspergrid = math.ceil(all_coords.shape[0]/threadsperblock)
        my_kernel[blockspergrid, threadsperblock](all_coords, coord_N, index)
        candidates.append(int(index[0]))
    return candidates


###############################################################################
#  Enumeration of collinear magnetic configurations
###############################################################################

# =============================================================================
# Helper Class for Processing a Single Spin Configuration
# =============================================================================
class MagConfigProcessor:
    """
    Helper class that holds all data needed to process a single spin configuration.
    Its __call__ method is equivalent to the old process_combo function.
    """
    def __init__(self, base_structure, mag_indices, default_spins, frac_coords, kdtree, symm_ops, symprec):
        self.base_structure = base_structure      # The original structure
        self.mag_indices = mag_indices            # Indices of magnetic sites
        self.default_spins = default_spins        # Default spin values (0.0 for non-magnetic sites)
        self.frac_coords = frac_coords            # Fractional coordinates of all sites (as a NumPy array)
        self.kdtree = kdtree                      # KDTree built on fractional coordinates
        self.symm_ops = symm_ops                  # List of symmetry operations
        self.symprec = symprec                    # Tolerance for mapping

    def get_symmetrically_reordered_spinsold(self, spin_array, symmop):
        """
        Applies the symmetry operation to all sites and remaps the spins via the KDTree.
        Instead of assuming symmop.operate can handle an array, we apply it to each coordinate individually.
        """
        new_fracs = np.array([np.mod(symmop.operate(coord), 1.0) for coord in self.frac_coords])
        distances, indices = self.kdtree.query(new_fracs)
        if np.any(distances > self.symprec):
            raise ValueError("Mapping error: a site mapping exceeded tolerance.")
        spin_array_np = np.array(spin_array)
        new_spins = np.zeros_like(spin_array_np)
        new_spins[indices] = spin_array_np
        return new_spins.tolist()


    def get_symmetrically_reordered_spins(self, spin_array, symmop):
        """
        Applies the symmetry operation to all sites and remaps the spins via KDTree.
        """
        # Apply symmetry op and wrap into unit cell
        new_fracs = np.mod([symmop.operate(coord) for coord in self.frac_coords], 1.0)
        new_fracs = np.where(new_fracs >= 1.0 - self.symprec, 0.0, new_fracs)

        # Query KDTree to find closest original sites
        distances, indices = self.kdtree.query(new_fracs)

        # Raise detailed error if mismatch occurs
        if np.any(distances > self.symprec):
            max_dist = np.max(distances)
            offending_index = np.argmax(distances)
            offending_site = new_fracs[offending_index]
            raise ValueError(f"Mapping error: a site mapping exceeded tolerance. "
                            f"Max dist = {max_dist:.6e} at site {offending_index}: {offending_site}")

        # Reorder spins
        spin_array_np = np.array(spin_array)
        new_spins = np.zeros_like(spin_array_np)
        new_spins[indices] = spin_array_np
        return new_spins.tolist()


    def canonical_spin_label(self, spin_array):
        """
        For a given spin configuration, apply all symmetry operations and return
        the lexicographically smallest configuration as the canonical label.
        """
        candidates = [
            tuple(self.get_symmetrically_reordered_spins(spin_array, op))
            for op in self.symm_ops
        ]
        return min(candidates)

    def __call__(self, combo):
        """
        Process a single spin combination:
          - Multiply the default spin array at magnetic indices by the combo values.
          - Compute the canonical spin label.
          - Return a tuple of (label, spin configuration).
        """
        spin_arr = list(self.default_spins)
        for i_combo, i_mag_site in enumerate(self.mag_indices):
            spin_arr[i_mag_site] *= combo[i_combo]
        label = self.canonical_spin_label(spin_arr)
        return label, spin_arr

# =============================================================================
# Global Variable and Top-Level Worker Function
# =============================================================================
_global_processor = None

def process_combo(combo):
    """
    Top-level worker function that wraps the global processor instance.
    This function is defined at the module level and is picklable.
    """
    if _global_processor is None:
        raise RuntimeError("Global processor has not been initialized.")
    return _global_processor(combo)

# =============================================================================
# Main Function: Optimized Enumeration of Magnetic Configurations
# =============================================================================
def enum_collinear_mag_config_optimized(
    base_structure,
    magnetic_elements,
    default_mag_dict=None,
    symprec=1e-5,
    angle_tolerance=2.0,
    max_structures=None,
    n_processes=None
):
    """
    Enumerates unique collinear spin configurations with full space-group symmetry reduction.

    Steps:
      1. Identify magnetic sites and assign default spins.
      2. Build a KDTree for rapid site mapping.
      3. Retrieve full space-group symmetry operations via pymatgen's SpacegroupAnalyzer.
      4. Enumerate spin combinations (with randomized sampling for diversity).
      5. Process configurations in parallel using the top-level worker (process_combo).
      6. Deduplicate configurations based on canonical spin labels.
      7. Force the FM configuration (all magnetic sites set to +1) to be the first element.

    Parameters:
      base_structure (Structure): The pymatgen structure.
      magnetic_elements (list of Element): Elements considered magnetic.
      default_mag_dict (dict, optional): Map element symbols to default spin values.
      symprec (float): Tolerance for symmetry mapping.
      angle_tolerance (float): Angular tolerance for symmetry detection.
      max_structures (int, optional): Maximum number of unique structures to return.
      n_processes (int, optional): Number of processes for parallel computation.

    Returns:
      List[Structure]: Unique structures with a site property "magmom", with the FM
                       configuration always as the first element.
    """
    if default_mag_dict is None:
        default_mag_dict = {}

    # --- Step A: Identify Magnetic Sites ---
    mag_indices = []
    default_spins = []
    for i, site in enumerate(base_structure):
        sp = site.specie.element if not isinstance(site.specie, Element) else site.specie
        if sp in magnetic_elements:
            mag_val = default_mag_dict.get(sp.symbol, 2.0)
            default_spins.append(mag_val)
            mag_indices.append(i)
        else:
            default_spins.append(0.0)
    if len(mag_indices) == 0:
        s0 = base_structure.copy()
        s0.add_site_property("magmom", default_spins)
        return [s0]
    N = len(mag_indices)
    total_combos = 2 ** N

    # --- Step B: Build KDTree for Fast Site Mapping ---
    frac_coords = np.array(base_structure.frac_coords)
    kdtree = cKDTree(frac_coords, boxsize=1.0)

    # --- Step C: Get Symmetry Operations ---
    sga = SpacegroupAnalyzer(base_structure, symprec=symprec, angle_tolerance=angle_tolerance)
    symm_ops = sga.get_symmetry_operations(cartesian=False)

    # --- Step D: Create the Processor Instance and Set Global Variable ---
    global _global_processor
    _global_processor = MagConfigProcessor(
        base_structure, mag_indices, default_spins, frac_coords, kdtree, symm_ops, symprec
    )

    # --- Step E: Enumerate Spin Combinations with Randomized Sampling for Diversity ---
    if total_combos <= 1000000:
        combos_list = list(product([+1, -1], repeat=N))
        random.shuffle(combos_list)
        # Increase sampling factor to boost the chance of diverse unique orbits.
        combos_iter = islice(combos_list, (max_structures * 10) if max_structures else None)
    else:
        def random_combos(n, count):
            for _ in range(count):
                yield tuple(np.random.choice([+1, -1], size=n))
        combos_iter = random_combos(N, (max_structures * 10) if max_structures else 10000)

    # --- Step F: Process Configurations in Parallel ---
    n_proc = n_processes if n_processes else min(cpu_count(), 4)
    with Pool(processes=n_proc) as pool:
        results = pool.map(process_combo, combos_iter)

    # --- Step G: Deduplicate Configurations Using Canonical Labels ---
    unique_label_map = {}
    unique_structs = []
    for label, spin_arr in results:
        if label not in unique_label_map:
            unique_label_map[label] = True
            new_struct = base_structure.copy()
            new_struct.add_site_property("magmom", spin_arr)
            unique_structs.append(new_struct)
        if max_structures and len(unique_structs) >= max_structures:
            break

    # --- Step H: Force FM Configuration as config_0 ---
    # Compute FM configuration explicitly: all magnetic sites are +1.
    fm_combo = tuple([+1] * N)
    fm_label, fm_spin_arr = _global_processor(fm_combo)
    fm_struct = base_structure.copy()
    fm_struct.add_site_property("magmom", fm_spin_arr)
    # Remove any structure with the same canonical label as FM from unique_structs.
    unique_structs = [struct for struct in unique_structs 
                      if _global_processor.canonical_spin_label(struct.site_properties["magmom"]) != fm_label]
    # Insert the FM structure at the beginning.
    unique_structs.insert(0, fm_struct)

    log(f"Enumerated ~{len(results)} raw spin patterns.")
    log(f"Found {len(unique_structs)} unique patterns after space-group merging.")
    return unique_structs
    

###############################################################################
#  Plot results: E, M, Cv, Chi vs T
###############################################################################
def plot_results(
    T_list, E_list, E_err_list,
    M_list, M_err_list,
    Cv_list, Cv_err_list,
    Chi_list, Chi_err_list, matName,
    plot_errors=True
):
    """
    2x2 figure: 
      1) E vs T
      2) M vs T
      3) Cv vs T
      4) Chi vs T
    """
    plt.figure(figsize=(10,8))

    # (1) Energy
    plt.subplot(2,2,1)
    if plot_errors:
        plt.errorbar(T_list, E_list, yerr=E_err_list, fmt='o-', capsize=5, label='Energy')
    else:
        plt.plot(T_list, E_list, 'o-', label='Energy')
    plt.xlabel('T (K)')
    plt.ylabel('E (eV/site)')
    plt.legend()

    # (2) Magnetization
    plt.subplot(2,2,2)
    if plot_errors:
        plt.errorbar(T_list, M_list, yerr=M_err_list, fmt='o-', capsize=5, label='M')
    else:
        plt.plot(T_list, M_list, 'o-', label='M')
    plt.xlabel('T (K)')
    plt.ylabel('M (per site)')
    plt.legend()

    # (3) Specific Heat
    plt.subplot(2,2,3)
    if plot_errors:
        plt.errorbar(T_list, Cv_list, yerr=Cv_err_list, fmt='o-', capsize=5, label='Cv')
    else:
        plt.plot(T_list, Cv_list, 'o-', label='Cv')
    plt.xlabel('T (K)')
    plt.ylabel('Cv (eV/(kB.site))')
    plt.legend()

    # (4) Susceptibility
    plt.subplot(2,2,4)
    if plot_errors:
        plt.errorbar(T_list, Chi_list, yerr=Chi_err_list, fmt='o-', capsize=5, label='Chi')
    else:
        plt.plot(T_list, Chi_list, 'o-', label='Chi')
    plt.xlabel('T (K)')
    plt.ylabel('Chi (1/eV)')
    plt.legend()

    plt.tight_layout()
    plot_filename = f"{matName}_Heisenberg_mc.png"
    plt.savefig(plot_filename, dpi=150)
    #plt.show()
    log(f"Plot saved as '{plot_filename}' in directory {os.getcwd()}")
    


def plot_spin_dump(filename, figname):
    """
    Reads a spins dump file with blocks formatted as:
    
        T = <temperature> K

        Sx = 
        [list of Sx values]

        Sy = 
        [list of Sy values]

        Sz = 
        [list of Sz values]

        --------------------------------------------------------------------------------
    
    For each block, plots Sx, Sy, and Sz versus site index in a 3-panel plot.
    """
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split the file into blocks using the dashed line as separator.
    blocks = content.split("-" * 100)
    # Remove empty blocks and strip whitespace.
    blocks = [block.strip() for block in blocks if block.strip()]
    
    # Parse each block.
    data_blocks = []
    for block in blocks:
        lines = block.splitlines()
        # Extract temperature:
        T_val = None
        for line in lines:
            if line.startswith("T ="):
                try:
                    # Expected format: "T = <value> K"
                    T_val = float(line.split("=")[1].split("K")[0].strip())
                except Exception as e:
                    print("Error parsing T:", e)
                break
        # Find indices for Sx, Sy, Sz markers:
        try:
            idx_Sx = lines.index("Sx =")
            idx_Sy = lines.index("Sy =")
            idx_Sz = lines.index("Sz =")
        except ValueError:
            continue  # skip block if not all markers are present
        
        try:
            Sx = ast.literal_eval(lines[idx_Sx + 1].strip())
            Sy = ast.literal_eval(lines[idx_Sy + 1].strip())
            Sz = ast.literal_eval(lines[idx_Sz + 1].strip())
        except Exception as e:
            print("Error parsing spin arrays:", e)
            continue
        
        data_blocks.append({"T": T_val, "Sx": Sx, "Sy": Sy, "Sz": Sz})
    
    # Plot each block in a separate figure.
    for data in data_blocks:
        T = data["T"]
        Sx = data["Sx"]
        Sy = data["Sy"]
        Sz = data["Sz"]
        
        # Create a figure with 3 subplots (one per spin component)
        fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
        axs[0].plot(Sx, 'r-o')
        axs[0].set_ylabel("Sx")
        axs[1].plot(Sy, 'g-o')
        axs[1].set_ylabel("Sy")
        axs[2].plot(Sz, 'b-o')
        axs[2].set_ylabel("Sz")
        axs[2].set_xlabel("Site index")
        
        fig.suptitle(f"Spin Components at T = {T:.2f} K")
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plot_filename = f"{figname}_Heisenberg_spins.png"
        plt.savefig(plot_filename, dpi=150)
        log(f"Plot saved as '{plot_filename}' in directory {os.getcwd()}")
        


def parse_input():
    global struct_file, skip, rep_DFT, vacuum, strain, xc, cmd, cmd_ncl, randomise_cmd, exchange_type
    global relx, mag_prec, enum_prec, ltol, stol, atol, max_neigh, mag_from, GPU_accel
    global padding, dump_spins, ismear, sigma, nsim, kpar, npar, ncore, isif, iopt, nccl 
    global LDAUJ_provided, LDAUU_provided, LDAUL_provided, ldautype, potcar_provided, d_thresh 
    global d_buff, acc, log_file, kpt_den_relx, kpt_den_stat, potential_directory, potential_symlink
    global spin_axes, system_dimension, mc_method, encut, lvdw, dftu, root_path,no_magstruct

    #msg = '*'*150
    #log(msg)
               
    #log("*** Starting Curie2D workflow (prior log file cleared).")
        
    with open('input') as f:
        for line in f:
            row = line.split()
            if 'structure_file' in line:
                struct_file = row[-1]
            elif 'DFT_supercell_size' in line:
                rep_z = int(row[-1])
                rep_y = int(row[-2])
                rep_x = int(row[-3])
                rep_DFT = [rep_x, rep_y, rep_z]
            elif 'vacuum' in line:
                vacuum = float(row[-1])
            elif 'strain' in line:
                strain_values = [float(x) for x in row[-3:]]
                strain_a, strain_b, strain_c = strain_values
                strain = [strain_a, strain_b, strain_c]
            elif 'XC_functional' in line:
                xc = row[-1]
            elif 'VASP_command_std' in line:
                cmd = line[len('VASP_command_std =')+1:-1].split()
            elif 'VASP_command_ncl' in line:
                cmd_ncl = line[len('VASP_command_ncl =')+1:-1].split()
            elif 'randomise_VASP_command' in line:
                randomise_cmd = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'skip_configurations' in line:
                skip = line[len('skip_configurations =')+1:-1].split()
            elif 'relax_structures' in line:
                relx = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'exchange_type' in line:
                exchange_type = row[-1]
            elif 'mag_prec' in line:
                mag_prec = float(row[-1])
            elif 'enum_prec' in line:
                enum_prec = float(row[-1])
            elif 'ltol' in line:
                ltol = float(row[-1])
            elif 'stol' in line:
                stol = float(row[-1])
            elif 'atol' in line:
                atol = float(row[-1])
            elif 'max_neighbors' in line:
                max_neigh = int(row[-1])
            elif 'mag_from' in line:
                mag_from = row[-1]
            elif 'GPU_accel' in line:
                GPU_accel = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'more_than_2_metal_layers' in line:
                padding = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'dump_spins' in line:
                dump_spins = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'ISMEAR' in line:
                ismear = int(row[-1])
            elif 'SIGMA' in line:
                sigma = float(row[-1])
            elif 'NSIM' in line:
                nsim = int(row[-1])
            elif 'KPAR' in line:
                kpar = int(row[-1])
            elif 'NPAR' in line:
                npar = int(row[-1])
            elif 'ENCUT' in line:
                encut = float(row[-1])
            elif 'LVDW' in line:
               lvdw = row[-1].strip().lower() in ['true', '1', 'yes']   
            elif 'dftu' in line:
               dftu = row[-1].strip().lower() in ['true', '1', 'yes']                           
            elif 'NCORE' in line:
                ncore = int(row[-1])
            elif 'ISIF' in line:
                isif = int(row[-1])
            elif 'IOPT' in line:
                iopt = int(row[-1])
            elif 'LUSENCCL' in line:
                nccl = row[-1].strip().lower() in ['true', '1', 'yes']
            elif 'LDAUJ' in line:
                num_spec = len(row)-2
                for i2 in range(2, num_spec+1, 2):
                    LDAUJ_provided[row[i2]] = float(row[i2+1])
            elif 'LDAUU' in line:
                num_spec = len(row)-2
                for i2 in range(2, num_spec+1, 2):
                    LDAUU_provided[row[i2]] = float(row[i2+1])
            elif 'LDAUL' in line:
                num_spec = len(row)-2
                for i2 in range(2, num_spec+1, 2):
                    LDAUL_provided[row[i2]] = float(row[i2+1])
            elif 'LDAUTYPE' in line:
                ldautype = int(row[-1])
            elif 'POTCAR' in line:
                num_spec = len(row)-2
                for i2 in range(2, num_spec+1, 2):
                    potcar_provided[row[i2]] = row[i2+1]
            elif 'same_neighbor_thresh' in line:
                d_thresh = float(row[-1])
            elif 'same_neighbor_thresh_buffer' in line:
                d_buff = float(row[-1])
            elif 'accuracy' in line:
                acc = row[-1]
            elif 'log_filename' in line:
                log_file = row[-1]
            elif 'kpoints_density_relax' in line:
                kpt_den_relx = float(row[-1])
            elif 'kpoints_density_static' in line:
                kpt_den_stat = float(row[-1])
            elif 'potential_directory' in line:
                potential_directory = row[-1]
            elif 'mc_method' in line:
                mc_method = int(line.split('=')[-1].strip())
            elif 'no_magstruct' in line:
                no_magstruct = int(line.split('=')[-1].strip())
            elif line.startswith("spin_axes"):
                spin_axes_str = line.split("=")[1].strip()
                spin_axes = parse_spin_axes(spin_axes_str)
            elif line.startswith("system_dimension"):
                system_dimension = line.split("=")[1].strip().upper()
                if system_dimension not in ["2D", "3D", "1D"]:
                    system_dimension = "2D"  # Default
    
    if 'spin_axes' not in globals():
        if system_dimension == "2D":
            spin_axes = parse_spin_axes("100;001;010")
        else:
            spin_axes = parse_spin_axes("100;001;111")
            
    if not potential_directory:
         msg = "Error: 'potential_directory' must be provided in the input file. Please add it and restart the run."
         log(msg)
         sys.exit()
        
    if not os.path.isdir(potential_directory):
        raise ValueError(f"Error: The provided potential_directory '{potential_directory}' does not exist or is not a directory.")
        
    if not potcar_provided:
        potcar_provided = None
    
    # Return a dictionary containing all parsed values
    return {
        "struct_file": struct_file,
        "skip": skip,
        "rep_DFT": rep_DFT,
        "vacuum": vacuum,
        "strain": strain,
        "xc": xc,
        "cmd": cmd,
        "cmd_ncl": cmd_ncl,
        "randomise_cmd": randomise_cmd,
        "exchange_type": exchange_type,
        "relx": relx,
        "mag_prec": mag_prec,
        "enum_prec": enum_prec,
        "ltol": ltol,
        "stol": stol,
        "atol": atol,
        "max_neigh": max_neigh,
        "mag_from": mag_from,
        "GPU_accel": GPU_accel,
        "padding": padding,
        "dump_spins": dump_spins,
        "ismear": ismear,
        "sigma": sigma,
        "nsim": nsim,
        "kpar": kpar,
        "npar": npar,
        "ncore": ncore,
        "isif": isif,
        "iopt": iopt,
        "nccl": nccl,
        "LDAUJ_provided": LDAUJ_provided,
        "LDAUU_provided": LDAUU_provided,
        "LDAUL_provided": LDAUL_provided,
        "ldautype": ldautype,
        "potcar_provided": potcar_provided,
        "d_thresh": d_thresh,
        "d_buff": d_buff,
        "acc": acc,
        "log_file": log_file,
        "kpt_den_relx": kpt_den_relx,
        "kpt_den_stat": kpt_den_stat,
        "potential_directory": potential_directory,
        "potential_symlink": potential_symlink,
        "spin_axes": spin_axes,
        "system_dimension": system_dimension,
        "mc_method": mc_method,
        "no_magstruct":no_magstruct,
        "encut": encut,
        "lvdw": lvdw,
        "dftu": dftu,
        "root_path": root_path
    }


def disable_dftu(params_dicts):
    for d in params_dicts:
        d['LDAU'] = False
        for key in ['LDAUU', 'LDAUL', 'LDAUJ', 'LDAUPRINT', 'LDAUTYPE']:
            d.pop(key, None)
            


def read_structure_adaptively(struct_file):
    """
    Attempts to read a structure file using ASE, supporting VASP (POSCAR/CONTCAR) and CIF formats.
    Automatically tries both formats regardless of extension if necessary.
    """
    tried_formats = []

    ext = os.path.splitext(struct_file)[1].lower()
    if ext == '.cif':
        try:
            cell_ase = read(struct_file, format='cif')
            return sort(cell_ase)
        except Exception:
            tried_formats.append('cif')
    elif ext == '':
        pass  # Fall through to try both formats below
    else:
        # Non-cif extension — assume VASP format first
        try:
            cell_ase = read(struct_file, format='vasp')
            return sort(cell_ase)
        except Exception:
            tried_formats.append('vasp')

    # Second: try both formats blindly
    for fmt in ['vasp', 'cif']:
        if fmt not in tried_formats:
            try:
                cell_ase = read(struct_file, format=fmt)
                return sort(cell_ase)
            except Exception:
                tried_formats.append(fmt)

    # If all attempts fail
    raise ValueError(
        f"Failed to read structure file '{struct_file}' as any of the supported formats: {tried_formats}"
    )
            
###############################################################################
# Full function for Optimization and Magnetic Calculations
###############################################################################

def run_full_workflow():
    global struct_file, skip, rep_DFT, vacuum, strain, xc, cmd, cmd_ncl, randomise_cmd, exchange_type 
    global relx, mag_prec, enum_prec, ltol, stol, atol, max_neigh, mag_from, GPU_accel, padding
    global dump_spins, ismear, sigma, nsim, kpar, npar, ncore, isif, iopt, nccl, LDAUJ_provided, LDAUU_provided
    global LDAUL_provided, ldautype, potcar_provided, d_thresh, d_buff, acc, log_file, kpt_den_relx, kpt_den_stat
    global potential_directory, potential_symlink, struct_mag_stable, ds_stable,encut,lvdw, dftu,no_magstruct

    """
    1) Read 'input'
    2) Build structure from ASE => Pymatgen
    3) Pure-Python enumeration of collinear spins
    4) Perform VASP relax + static + SOC
    5) Fit Heisenberg + anisotropy
    """
   

    # ---------------------------------------------------------------------------------------
    # 0) Link potentials, logging
    # ---------------------------------------------------------------------------------------
    if os.path.lexists(potential_symlink):
        os.remove(potential_symlink)
        log(f"Removed existing file or link at {potential_symlink}.")
    os.symlink(potential_directory, potential_symlink)
    log(f"Created symbolic link: {potential_symlink} -> {potential_directory}")


    if acc=='high':
        msg = 'High accuracy => smaller EDIFF, larger k‐mesh => slower calculations.'
        log(msg)


    cell_ase = read_structure_adaptively(struct_file) # read(struct_file)   # ASE Atoms
    ase_adopt = AseAtomsAdaptor()
    struct0 = ase_adopt.get_structure(cell_ase)
    if vacuum > 1e-3 or struct0.lattice.c < 12.0:
        z_coords = [site.z for site in struct0]
        thick = max(z_coords) - min(z_coords)
        c0 = struct0.lattice.c
        current_vac = c0 - thick
        if current_vac < vacuum:
            extra = vacuum - current_vac
            cell_ase.center(extra, axis=2)
            struct0 = ase_adopt.get_structure(cell_ase)
            log(f"Added {extra:.3f} Å vacuum in z")
        else:
            log("Sufficient vacuum found. No changes made to z dimension.")
        
    ase_adopt = AseAtomsAdaptor()
    
    struct = ase_adopt.get_structure(cell_ase)
    struct = Structure(
        struct.lattice,
        struct.species,
        struct.frac_coords,
        to_unit_cell=True,
        coords_are_cartesian=False,
        site_properties=struct.site_properties,
    )


    if strain:
        struct.apply_strain(strain)
        msg = f"The structure is being strained with {strain}"
        log(msg)
        
                

    # -------------------------------------------------------------------------
    # VASP relaxation, static runs, SOC.
    # -------------------------------------------------------------------------

    # (1) Build user_incar_settings for relaxation
    LDAUJ_dict = {
        'Co':0.70, 'Cr':0.70, 'Fe':0.70, 'Mn':0.70, 'Mo':0.70, 'Ni':0.70, 'V':0.70, 'W':0.70,
        'Nb':0.70, 'Sc':0.70, 'Ru':0.70, 'Rh':0.70, 'Pd':0.70, 'Cu':0.70, 'Y':0.70, 'Os':0.70,
        'Ti':0.70, 'Zr':0.70, 'Re':0.70, 'Hf':0.70, 'Pt':0.70, 'La':0.70
    }
    if LDAUJ_provided:
        LDAUJ_dict.update(LDAUJ_provided)

    LDAUU_dict = {
        'Co':3.32, 'Cr':3.7, 'Fe':5.3, 'Mn':3.9, 'Mo':4.38, 'Ni':6.2, 'V':3.25, 'W':6.2,
        'Nb':1.45,'Sc':4.18,'Ru':4.29,'Rh':4.17,'Pd':2.96,'Cu':7.71,'Y':3.23,'Os':2.47,
        'Ti':5.89,'Zr':5.55,'Re':1.28,'Hf':4.77,'Pt':2.95,'La':5.3
    }
    if LDAUU_provided:
        LDAUU_dict.update(LDAUU_provided)

    LDAUL_dict = {
        'Co':2, 'Cr':2, 'Fe':2, 'Mn':2, 'Mo':2, 'Ni':2, 'V':2, 'W':2,
        'Nb':2, 'Sc':2, 'Ru':2, 'Rh':2, 'Pd':2, 'Cu':2, 'Y':2, 'Os':2,
        'Ti':2, 'Zr':2, 'Re':2, 'Hf':2, 'Pt':2,'La':2
    }
    if LDAUL_provided:
        LDAUL_dict.update(LDAUL_provided)


    relx_dict = {
        'ALGO':'Normal','ISMEAR':0,'SIGMA':0.01,'EDIFF':1E-5,'EDIFFG':-0.02, 'ENCUT':encut,
        'KPAR':kpar, 'NPAR':npar, 'NCORE':ncore, 'NSIM':nsim,'ISTART':0, 'LCHARG':False, 'ICHARG':2,'LREAL':False,
        'LDAU':True, 'LDAUJ':LDAUJ_dict, 'LDAUL':LDAUL_dict, 'LDAUU':LDAUU_dict, 'LWAVE':False,'ISYM':2, 'NSW':200,
        'LDAUPRINT':1, 'LDAUTYPE':ldautype, 'LASPH':True, 'LMAXMIX':4, 'PSTRESS': 0.001,'IALGO':48,'ADDGRID':True,
        'ISIF':isif, 'IBRION':2, 'POTIM':0.1, 'IOPT':iopt, 'LTWODIM':True, 'LUSENCCL':nccl,'LPLANE':True
    }
    
    
    scf_dict = {
        'ALGO': 'Normal',
        'ISMEAR': 0,
        'SIGMA': 0.02,
        'EDIFF': 1E-6,
        'ENCUT': encut,
        'KPAR': kpar,
        'NPAR': npar,
        'NCORE': ncore,
        'NSIM': nsim,
        'PREC': 'Accurate',
        "NSW": 0,
        'ISTART': 0,
        'ICHARG': 2,
        'LCHARG': False,    
        'LWAVE': False,
        'LREAL': False,
        'ISYM': -1,
        'IALGO': 48,
        'LDAU': True,
        'LDAUJ': LDAUJ_dict,
        'LDAUL': LDAUL_dict,
        'LDAUU': LDAUU_dict,
        'LDAUPRINT': 1,
        'LDAUTYPE': ldautype,
        'LASPH': True,
        'NELM': 150,
        'LMAXMIX': 4,
        'PSTRESS': 0.001,
        'LTWODIM': True,
        'LUSENCCL': nccl,
        'LPLANE': True,
        'ADDGRID': True
    }



    scf_dictold = {
        # General settings
        'ALGO': 'Normal',
        'ISMEAR': 0,
        'SIGMA': 0.02,
        'EDIFF': 1E-5,
        'EDIFFG': -0.02,
        'ENCUT': encut,
        'ICHARG': 2,
        'LCHARG': False,
        'LWAVE': False,
        'LREAL': False,

        # DFT+U parameters
        'LDAU': True,
        'LDAUL': LDAUL_dict,
        'LDAUU': LDAUU_dict,
        'LDAUJ': LDAUJ_dict,
        'LDAUTYPE': ldautype,
        'LDAUPRINT': 1,
        'LASPH': True,
        'LMAXMIX': 4,
        'NELMDL': 6,

        # Relaxation control
        'ISIF': 2,       # Stress/force relaxation setting
        'IBRION': 3,        # FIRE algorithm
        'IOPT': iopt,       # Optimization strategy
        'POTIM': 0,         # Timestep (0 lets VASP choose for IOPT)

        # Dimensionality and environment
        'LTWODIM': True,
        'LUSENCCL': nccl,   # NCCL GPU support (if applicable)

        # Parallelization
        'KPAR': kpar,
        'NPAR': npar,
        'NCORE': ncore,
        'NSIM': nsim,
        'LPLANE': True,
        'ADDGRID': True
    }
    

    stat_dict = {
        'ISMEAR':ismear, 'EDIFF':1E-6, 'ENCUT':encut, 'KPAR':kpar, 'NPAR':npar,'NCORE':ncore, 'NSIM':nsim, 'LORBMOM':True,
        'LAECHG':True, 'LREAL':False, 'LDAU':True, 'LDAUJ':LDAUJ_dict, 'LDAUL':LDAUL_dict,
        'LDAUU':LDAUU_dict, 'NELMIN':6, 'NELM':250, 'LVHAR':False, 'SIGMA':sigma,
        'LDAUPRINT':1, 'LDAUTYPE':ldautype, 'LASPH':True, 'LMAXMIX':4, 'LCHARG':True,
        'LWAVE':True, 'ICHARG':2, 'ISYM':-1, 'LVTOT':False, 'LUSENCCL':nccl, 'ADDGRID':True
    }
    
    
    relx_handlers = [
        VaspErrorHandler(), UnconvergedErrorHandler(),
        FrozenJobErrorHandler(timeout=900), MeshSymmetryErrorHandler(),
        PositiveEnergyErrorHandler(), StdErrHandler(),
        NonConvergingErrorHandler(nionic_steps=5), PotimErrorHandler(dE_threshold=0.5)
    ]



    stat_handlers = [
        VaspErrorHandler(), UnconvergedErrorHandler(),
        FrozenJobErrorHandler(timeout=3600), MeshSymmetryErrorHandler(),
        PositiveEnergyErrorHandler(), StdErrHandler()
    ]
    
    scf_handlers = [
        VaspErrorHandler(), UnconvergedErrorHandler(),
        FrozenJobErrorHandler(timeout=1800), MeshSymmetryErrorHandler(),
        PositiveEnergyErrorHandler(), StdErrHandler()
    ]
    
    validator = [VasprunXMLValidator()]


    if xc=='PBE':
        pot = 'PBE_54'
    elif xc=='LDA':
        pot = 'LDA_54'
    elif xc=='SCAN':
        pot = 'PBE_54'
        scf_dict['METAGGA']='SCAN'
        scf_dict['LMIXTAU']=True
        scf_dict['LDAU']=False
        scf_dict['ALGO']='All'
        stat_dict['METAGGA']='SCAN'
        stat_dict['LMIXTAU']=True
        stat_dict['LDAU']=False
        stat_dict['ALGO']='All'
        relx_dict['METAGGA']='SCAN'
        relx_dict['LMIXTAU']=True
        relx_dict['LDAU']=False
        relx_dict['ALGO']='All'
    elif xc=='R2SCAN':
        pot = 'PBE_54'
        scf_dict['METAGGA']='R2SCAN'
        scf_dict['LMIXTAU']=True
        scf_dict['LDAU']=False
        scf_dict['ALGO']='All'
        stat_dict['METAGGA']='R2SCAN'
        stat_dict['LMIXTAU']=True
        stat_dict['LDAU']=False
        stat_dict['ALGO']='All'
        relx_dict['METAGGA']='R2SCAN'
        relx_dict['LMIXTAU']=True
        relx_dict['LDAU']=False
        relx_dict['ALGO']='All'
    elif xc=='SCAN+RVV10':
        pot = 'PBE_54'
        scf_dict['METAGGA']='SCAN'
        scf_dict['LMIXTAU']=True
        scf_dict['LDAU']=False
        scf_dict['ALGO']='All'
        scf_dict['LUSE_VDW']=True
        scf_dict['BPARAM']=6.3
        scf_dict['CPARAM']=0.0093
        stat_dict['METAGGA']='SCAN'
        stat_dict['LMIXTAU']=True
        stat_dict['LDAU']=False
        stat_dict['ALGO']='All'
        stat_dict['LUSE_VDW']=True
        stat_dict['BPARAM']=6.3
        stat_dict['CPARAM']=0.0093
        relx_dict['METAGGA']='SCAN'
        relx_dict['LMIXTAU']=True
        relx_dict['LDAU']=False
        relx_dict['ALGO']='All'
        relx_dict['LUSE_VDW']=True
        relx_dict['BPARAM']=6.3
        relx_dict['CPARAM']=0.0093
    elif xc=='R2SCAN+RVV10':
        pot = 'PBE_54'
        scf_dict['METAGGA']='R2SCAN'
        scf_dict['LMIXTAU']=True
        scf_dict['LDAU']=False
        scf_dict['ALGO']='All'
        scf_dict['LUSE_VDW']=True
        scf_dict['BPARAM']=6.3
        scf_dict['CPARAM']=0.0093
        stat_dict['METAGGA']='R2SCAN'
        stat_dict['LMIXTAU']=True
        stat_dict['LDAU']=False
        stat_dict['ALGO']='All'
        stat_dict['LUSE_VDW']=True
        stat_dict['BPARAM']=6.3
        stat_dict['CPARAM']=0.0093
        relx_dict['METAGGA']='R2SCAN'
        relx_dict['LMIXTAU']=True
        relx_dict['LDAU']=False
        relx_dict['ALGO']='All'
        relx_dict['LUSE_VDW']=True
        relx_dict['BPARAM']=6.3
        relx_dict['CPARAM']=0.0093
    elif xc=='PBEsol':
        pot = 'PBE_54'
        scf_dict['GGA']='PS'
        stat_dict['GGA']='PS'
        relx_dict['GGA']='PS'

    if acc=='high':
        relx_dict['EDIFF']=1E-5
        scf_dict['EDIFF']=1E-6
        stat_dict['EDIFF']=1E-7
        if kpt_den_relx is None:
            kpt_den_relx=100
        if kpt_den_stat is None:
            kpt_den_stat=300
    else:
        if kpt_den_relx is None:
            kpt_den_relx=150
        if kpt_den_stat is None:
            kpt_den_stat=300

    if not relx:
        relx_dict['EDIFFG'] = -10.0
        msg='No structural relaxation => big EDIFFG => quick run.'
        log(msg)

    if strain:
        relx_dict['ISIF']=2

    if kpt_den_relx==None and acc!='high':
        kpt_den_relx = 150
    if kpt_den_stat==None and acc!='high':
        kpt_den_stat = 300

    if lvdw and system_dimension == "2D" and xc != 'SCAN+RVV10':
       relx_dict['IVDW']=12
       scf_dict['IVDW']=12
       stat_dict['IVDW']=12

       relx_dict['LVDW']=True
       scf_dict['LVDW']=True
       stat_dict['LVDW']=True
       
       
    # Define magnetic list, default spins
    magnetic_list_local = [
        # Transition metals
        Element("Sc"), Element("Ti"), Element("V"), Element("Cr"), Element("Mn"), Element("Fe"),
        Element("Co"), Element("Ni"), Element("Cu"), Element("Zn"), Element("Y"), Element("Zr"),
        Element("Nb"), Element("Mo"), Element("Tc"), Element("Ru"), Element("Rh"), Element("Pd"),
        Element("Ag"), Element("Cd"), Element("Hf"), Element("Ta"), Element("W"), Element("Re"),
        Element("Os"), Element("Ir"), Element("Pt"), Element("Au"),
        
        # Lanthanides
        Element("Ce"), Element("Pr"), Element("Nd"), Element("Sm"), Element("Gd"),
        Element("Tb"), Element("Dy"), Element("Ho"), Element("Er"), Element("Tm"),
        Element("Yb"), Element("Lu"), Element("La"),Element("Eu"),

        # Actinides (select cases)
        Element("U"), Element("Np"), Element("Pu"),
        
        # p-block (common magnetic nonmetals in molecules and defects)
        Element("O"), Element("N"), Element("F"), Element("C"), Element("B"),
        
        # Others (edge cases with occasional moment pickup)
        Element("Ge"), Element("Sn"), Element("Sb"), Element("Te")
    ]

    magmom_defaults = {
        # 3d TM
        "Sc": 1.0, "Ti": 2.0, "V": 3.0, "Cr": 3.0, "Mn": 5.0, "Fe": 4.0,
        "Co": 3.0, "Ni": 2.0, "Cu": 0.0, "Zn": 0.0,

        # 4d TM
        "Y": 1.0, "Zr": 2.0, "Nb": 2.0, "Mo": 2.0, "Tc": 2.0, "Ru": 2.0,
        "Rh": 1.0, "Pd": 1.0, "Ag": 0.0, "Cd": 0.0,

        # 5d TM
        "Hf": 2.0, "Ta": 2.0, "W": 1.0, "Re": 2.0, "Os": 2.0,
        "Ir": 1.0, "Pt": 1.0, "Au": 0.0,

        # Lanthanides (note: values vary, these are rough ground-state spins)
        "Ce": 1.0, "Pr": 3.0, "Nd": 3.0, "Sm": 1.0, "Gd": 7.0, "Tb": 6.0,
        "Dy": 5.0, "Ho": 4.0, "Er": 3.0, "Tm": 2.0, "Yb": 1.0, "Lu": 0.0,
        "La": 0.0, "Eu": 7.0,

        # Actinides
        "U": 3.0, "Np": 3.0, "Pu": 2.0,

        # Light nonmetals
        "O": 0.0, "N": 0.0, "F": 0.0, "C": 0.0, "B": 0.0,

        # Semimetals / p-block edge cases
        "Ge": 0.0, "Sn": 0.0, "Sb": 0.0, "Te": 0.0
    }


    


    #for key in ['LDAU', 'LDAUL', 'LDAUU', 'LDAUJ', 'LDAUPRINT', 'LDAUTYPE']:
    #    relx_dict.pop(key, None)
        
    
    if not dftu:
        disable_dftu([relx_dict, scf_dict, stat_dict])
       
    #Parent structure relaxation

    if os.path.exists("input_MC"):
        params = read_mc_params("input_MC")
        restart_mode = int(params.get("restart", 0))
    else:
        restart_mode = 0
    
    if restart_mode == 0:    
        parent_relax_path = root_path+'/parent_relaxation'
        clean = sanitize(parent_relax_path)
        struct = struct.get_primitive_structure(use_site_props=True) 
        
        if not clean:
            relx_obj = MPRelaxSet(
                struct,
                user_incar_settings=relx_dict,
                user_kpoints_settings={'reciprocal_density':kpt_den_relx},
                force_gamma=True,
                user_potcar_functional=pot,
                sort_structure=False,
                user_potcar_settings=potcar_provided
            )
            relx_obj.write_input(parent_relax_path)
            if xc=='SCAN+RVV10' or xc=='R2SCAN+RVV10':
                #copyfile(root_path+'/vdw_kernel.bindat', parent_relax_path+'/vdw_kernel.bindat')
                safe_symlink(root_path + '/vdw_kernel.bindat', parent_relax_path + '/vdw_kernel.bindat')

            try:
                try_struct = Structure.from_file(parent_relax_path+'/CONTCAR.bk')
                try_struct.to(filename=parent_relax_path+'/POSCAR')
                msg = 'Copied backed-up CONTCAR to POSCAR'
            except Exception as e:
                msg = 'No back-up CONTCAR found'
            log(msg)

            # Adjust KPOINTS if 2D
            kpts = Kpoints.from_file(parent_relax_path+'/KPOINTS')
            if system_dimension == '2D':
                kpt_temp = list(kpts.kpts[0])
                kpt_temp[2] = 1
                kpts.kpts[0] = tuple(kpt_temp)
                kpts.write_file(parent_relax_path+'/KPOINTS')

            if randomise_cmd:
                cmd_rand = cmd[:]
                cmd_rand[-1] = cmd_rand[-1]+'_'+str(np.random.randint(0,9999))
                final_cmd = cmd_rand
            else:
                final_cmd = cmd

            os.chdir(parent_relax_path)
            job = [VaspJob(final_cmd)]
            cust = Custodian(
                relx_handlers, job, validator, max_errors=20, polling_time_step=5,
                monitor_freq=10, gzipped_output=False, checkpoint=False
            )
            msg = 'Running structural relaxation for the parent structure'
            log(msg)
            
            done = 0
            for j3 in range(3):
                try:
                    cust.run()
                    done = 1
                    sleep(10)
                    break
                except:
                    sleep(10)
                    continue

            os.chdir(parent_relax_path)

            if done == 1:
                msg = 'Relaxation finished successfully for the parent structure.'
                log(msg)
            else:
                msg = 'Relaxation failed after several attempts, exiting'
                log(msg)
                sys.exit()
        log('Parent-structure relaxation has finished gracefully.')
    

    os.chdir(root_path)

    struct_path = None  # For error reporting

    try:
        if restart_mode == 1:
            if 'struct_file' not in locals() and 'struct_file' not in globals():
                raise ValueError("Restart mode is enabled, but 'struct_file' is undefined.")

            if not os.path.isfile(struct_file):
                raise FileNotFoundError(f"Structure file not found at: {struct_file}")

            opt_struct = Structure.from_file(struct_file)
            log("Restart mode active. Using the original parent structure from struct_file.")

        else:
            if not parent_relax_path:
                raise ValueError("The variable 'parent_relax_path' is not set or is empty.")

            struct_path = os.path.join(parent_relax_path, 'CONTCAR')
            if not os.path.isfile(struct_path):
                raise FileNotFoundError(f"Structure file not found at: {struct_path}")

            opt_struct = Structure.from_file(struct_path)
            log("Using optimized structure from CONTCAR.")

        # Common processing
        opt_struct.make_supercell(rep_DFT)
        if restart_mode == 0: log("Building magnetic configurations with the selected structure.")

    except Exception as e:
        msg = "[Error] Failed to read or process structure"
        if struct_path:
            msg += f" from '{struct_path}'"
        msg += f": {e}"
        log(msg)
        sys.exit(1)





    # 0) Pre-compute these so we can use them in both modes:
    #    (we’ll overwrite material/struct_for_orth after reload if needed)
    material        = opt_struct.composition.reduced_formula
    s1              = opt_struct.copy()
    struct_for_orth = s1.lattice

    # 1) Prepare restart directory exactly as before
    restart_dir = os.path.join(root_path, "mag_spins")
    pkl_file    = os.path.join(restart_dir, f"{material}_magdata.pkl")

    if restart_mode == 0:
        # ─── fresh run ───
        # remove old VASP files
        for old in glob.glob(f"{material}_config_*.vasp"):
            os.remove(old)
        # rotate or make the folder
        if os.path.exists(restart_dir):
            os.rename(restart_dir, restart_dir + "_" + str(time()))
        os.makedirs(restart_dir)

    elif restart_mode == 1:
        if not os.path.exists(restart_dir):
            log("Restart requested but no spin directory found. Exiting.")
            sys.exit(1)

    # 2) Branch on restart_mode
    if restart_mode == 0:
        # ─── enumerate + match ───
        mag_enum_structs = enum_collinear_mag_config_optimized(
            base_structure    = opt_struct,
            magnetic_elements = magnetic_list_local,
            default_mag_dict  = magmom_defaults,
            symprec           = enum_prec,
            angle_tolerance   = 2.0,
            max_structures    = 40,
            n_processes       = 4,
        )

        # reset reference if you need it
        struct_for_orth = mag_enum_structs[0].lattice
        s1              = mag_enum_structs[0].copy()

        matcher = StructureMatcher(
            scale=True, primitive_cell=False,
            attempt_supercell=True,
            ltol=ltol, stol=stol, angle_tol=atol,
            comparator=ElementComparator(),
        )

        mag_structs   = []
        spins_configs = []
        count         = 0

        for i, st in enumerate(mag_enum_structs):
            if not matcher.fit(s1, st):
                continue

            s2    = matcher.get_s2_like_s1(s1, st)
            spins = [0.0 if x is None else x
                    for x in s2.site_properties["magmom"]]

            if i > 0 and np.sum(spins) != 0:
                continue

            mag_cell = ase_adopt.get_atoms(s2, magmoms=spins)
            mag_cell.center(vacuum/2, 2)
            s2 = ase_adopt.get_structure(mag_cell)
            s2.add_spin_by_site(spins)

            fname = os.path.join(restart_dir, f"{material}.config_{count}.vasp")
            s2.to(fmt="poscar", filename=fname)

            if count < no_magstruct:
                mag_structs.append(s2)
                spins_configs.append(spins)
                count += 1
            else:
                if os.path.exists(fname):
                    os.remove(fname)
                continue

        if skip:
            skip2 = [int(x) for x in skip]
            skip2.sort(reverse=True)
            for sk in skip2:
                if sk < len(mag_structs):
                    mag_structs.pop(sk)
                    spins_configs.pop(sk)
                    log(f"skipping config_{sk} on user request.")

        # 3) build the “super” list
        spins_configs_super = [s.site_properties["magmom"] for s in mag_structs]

        # 4) dump everything in one file
        with open(pkl_file, "wb") as f:
            pickle.dump({
                "mag_structs":         mag_structs,
                "spins_configs":       spins_configs,
                "spins_configs_super": spins_configs_super
            }, f)
        log(f"Saved {len(mag_structs)} configs + spin data to {pkl_file}")

    elif restart_mode == 1:
        # ─── restart: load the single pickle ───
        if not os.path.exists(pkl_file):
            log("Restart mode but no data pickle found; exiting.")
            sys.exit(1)

        #data = pickle.load(open(pkl_file, "rb"))
        with open(pkl_file, "rb") as fh:
            data = pickle.load(fh)


        if isinstance(data, dict):
            try:
                mag_structs         = data["mag_structs"]
                spins_configs       = data["spins_configs"]
                spins_configs_super = data["spins_configs_super"]
            except KeyError as err:
                log(f"Restart pickle (dict) is missing the key {err}; aborting.")
                sys.exit(1)

        # ---------- format B: legacy plain list of structures ----------------
        elif isinstance(data, (list, tuple)) and \
            len(data) > 0 and hasattr(data[0], "site_properties"):
            mag_structs   = list(data)
            spins_configs = [s.site_properties["magmom"] for s in mag_structs]
            spins_configs_super = spins_configs

        # ---------- format C: legacy `[mag_structs, spins, spins_super]` -----
        elif isinstance(data, (list, tuple)) and len(data) == 3:
            mag_structs, spins_configs, spins_configs_super = data


        # ---------- format D: list of pure spin arrays -------------------------
        elif isinstance(data, (list, tuple)) and len(data) > 0 \
            and all(isinstance(x, (list, tuple)) for x in data):
            # (1) read all VASP files that belong to this job
            vasp_paths = sorted(glob.glob(os.path.join(restart_dir,
                                                      f"{material}.config_*.vasp")))
            if len(vasp_paths) != len(data):
                log("Spin-only pickle but the number of .vasp files "
                    "does not match; aborting.")
                sys.exit(1)

            mag_structs = []
            for vp in vasp_paths:
                st = Structure.from_file(vp)          # pymatgen
                mag_structs.append(st)

            spins_configs       = [list(sp) for sp in data]
            spins_configs_super = spins_configs  # no extra info available


        # ---------- otherwise: unknown / corrupt -----------------------------
        else:
            log("Unrecognised data format in restart pickle; aborting.")
            sys.exit(1)


            sys.exit(1)

        # re-derive convenience variables
        material        = mag_structs[0].composition.reduced_formula
        struct_for_orth = mag_structs[0].lattice



        log(f"Restart mode: loaded {len(mag_structs)} configs + spin data from {pkl_file}")



    log(f"We have {len(mag_structs)} configs for {material}")

    num_struct = len(mag_structs)




    num_atoms = []
    for struct in mag_structs:
        num_atoms.append(len(struct))
        num_atoms = [int(len(struct)) for struct in mag_structs if struct is not None]
    lcm_atoms = np.lcm.reduce(num_atoms)

    if num_struct<2:
        msg = ('*** Only one or zero configs => cannot fit Heisenberg. '
              'Try bigger supercell or different tolerances. Exiting.')
        log(msg)
        sys.exit()
    elif num_struct==2:
        msg = ('** Only two configs => can only fit first neighbor interaction. '
              'Consider more. **')
        log(msg)
        
        
        
    if restart_mode == 1:
        try:
            with open(pkl_file, "rb") as f:
                spins_configs_super = load(f)
            log(f"Loaded spins_configs_super from {pkl_file} for restart.")
        except Exception as e:
            log("Error loading spins_configs_super in restart mode: " + str(e))
            sys.exit(1)
    else:
        # Just store the site_properties for each enumerated config
        spins_configs_super = []
        for s in mag_structs:
            spins_configs_super.append(s.site_properties["magmom"])
        with open(pkl_file, "wb") as f:
            dump(spins_configs_super, f)
        log(f"Saved spins_configs_super to {pkl_file}.")
        

    saxes = spin_axes if spin_axes else []
    ortho_ab = None

    if system_dimension == "3D":
        if len(saxes) != 3:
            log("Warning: For a 3D system, it is recommended to supply three spin axes. Using defaults (100;001;111).")
            saxes = [(1, 0, 0), (0, 0, 1), (1, 1, 1)]
        ortho_ab = True
        log("3D system — using spin axes (saxes): " + str(saxes))

    elif system_dimension == "2D":
        if len(saxes) == 2:
            ortho_ab = False
        elif len(saxes) >= 3:
            ortho_ab = True
        else:
            saxes = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
            ortho_ab = True
        log("2D system — using spin axes (saxes): " + str(saxes))

    else:
        log("Unrecognized system dimension ('{}'). Using default spin axes.".format(system_dimension))
        saxes = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
        ortho_ab = True
        log("Default spin axes (saxes): " + str(saxes))

    # If spin_axes input is absent or ambiguous, and ortho_ab wasn't determinable, fall back to structure
    if ortho_ab is None:
        gamma = struct_for_orth.gamma
        a_b_ratio = struct_for_orth.a / struct_for_orth.b if struct_for_orth.b != 0 else 1.0
        ortho_ab = (88 < gamma < 92) and (a_b_ratio < 0.9 or a_b_ratio > 1.1)
        log("Fallback to lattice detection: gamma = {:.2f}, a/b = {:.2f}".format(gamma, a_b_ratio))
        log("Structure-based ortho_ab set to: " + str(ortho_ab))


    log("System dimension: " + system_dimension + "  --> ortho_ab = " + str(ortho_ab))
        
    
    start_time_dft = time()
    energies_relx = []


    log("Performing magnetic structure calculations")
    for i in range(num_struct):
        spins = spins_configs[i]
        struct_current = mag_structs[i].copy()
        factor = float(lcm_atoms)/len(struct_current)
        if factor!=int(factor):
            msg = '*** Factor is float, '+str(factor)+', exiting'
            log(msg)
            sys.exit()

        relx_path = root_path+'/mag_cal'+'/config_'+str(i)
        clean = sanitize(relx_path)
        if not clean:
            relx_obj = MPRelaxSet(
                struct_current,
                user_incar_settings=scf_dict,
                user_kpoints_settings={'reciprocal_density':kpt_den_relx},
                force_gamma=True,
                user_potcar_functional=pot,
                sort_structure=False,
                user_potcar_settings=potcar_provided
            )
            relx_obj.write_input(relx_path)
            if xc=='SCAN+RVV10' or xc=='R2SCAN+RVV10':
                #copyfile(root_path+'/vdw_kernel.bindat', relx_path+'/vdw_kernel.bindat')
                safe_symlink(root_path + '/vdw_kernel.bindat', relx_path + '/vdw_kernel.bindat')
            try:
                try_struct = Structure.from_file(relx_path+'/CONTCAR.bk')
                try_struct.to(filename=relx_path+'/POSCAR')
                msg = 'Copied backed up CONTCAR to POSCAR'
            except Exception as e:
                msg = 'No back up CONTCAR found'
            log(msg)
            kpts = Kpoints.from_file(relx_path+'/KPOINTS')
            if system_dimension == '2D':
                kpt_temp = list(kpts.kpts[0])
                kpt_temp[2] = 1
                kpts.kpts[0] = tuple(kpt_temp)
                kpts.write_file(relx_path+'/KPOINTS')

            if randomise_cmd:
                cmd_rand = cmd[:]
                cmd_rand[-1] = cmd_rand[-1]+'_'+str(np.random.randint(0,9999))
                final_cmd = cmd_rand #[VaspJob(cmd_rand)]
            else:
                final_cmd = cmd

            os.chdir(relx_path)
            
            job = [VaspJob(final_cmd)]
            cust = Custodian(
                scf_handlers, job, validator, max_errors=20, polling_time_step=5,
                monitor_freq=10, gzipped_output=False, checkpoint=False
            )
            msg = 'Running magnetic calculation for configuration '+str(i)
            log(msg)
            done = 0

            
            #print(f"Running structural relaxtion in directory: {os.getcwd()}")
            for j3 in range(3):
                try:
                    cust.run()
                    done = 1
                    sleep(10)
                    break
                except:
                    sleep(10)
                    continue
            os.chdir(root_path)

            if done == 1:
                msg = 'Magnetic SCF finished successfully for config '+str(i)
                log(msg)
            else:
                msg = 'Magnetic SCF failed for config '+str(i)+' after several attempts, exiting'
                log(msg)
                sys.exit()

        run = Vasprun(relx_path+'/vasprun.xml', parse_dos=False, parse_eigen=False)
        energy = float(run.final_energy)
        energy = energy*factor
        energies_relx.append(energy)

    msg = 'All magnetic calculations have finished gracefully'
    log(msg)
    msg = 'Configuration-wise, SCF energies (in eV) are: '+str(energies_relx)
    log(msg)
    most_stable = np.argmin(energies_relx)
    msg = '### The most stable configuration = config_'+str(most_stable)
    log(msg)

    s_mag = Structure.from_file(root_path + '/mag_cal/config_' + str(most_stable) + '/CONTCAR')
    struct_ground_super = s_mag
    
    log("All magnetic configuration SCF completed!")


    msg = 'Performing Collinear Spin Enumeration on the magnetic structures...'
    log(msg)
        
    mag_structsX = []
    for i2 in range(num_struct):
        
        mag_struct_temp = struct_ground_super.copy()
        mag_struct_temp.add_spin_by_site(spins_configs_super[i2])
        mag_structsX.append(mag_struct_temp)

    if most_stable<=max_neigh:
        mag_structsX = mag_structsX[:max_neigh+1]
    num_struct = len(mag_structsX)

    for i2 in range(num_struct):
        spins = spins_configs[i2]
        stat_struct = mag_structsX[i2].copy()

        stat_path = root_path+'/static_runs'+'/config_'+str(i2)
        clean2 = sanitize(stat_path)
        if not clean2:
            stat_inp = MPStaticSet(
                stat_struct,
                user_incar_settings=stat_dict,
                reciprocal_density=kpt_den_stat,
                force_gamma=True,
                user_potcar_functional=pot,
                sort_structure=False,
                user_potcar_settings=potcar_provided
            )
            stat_inp.write_input(stat_path)
            if xc=='SCAN+RVV10' or xc=='R2SCAN+RVV10':
                #copyfile(root_path+'/vdw_kernel.bindat', stat_path+'/vdw_kernel.bindat')
                safe_symlink(root_path + '/vdw_kernel.bindat', stat_path + '/vdw_kernel.bindat')
            kptsY = Kpoints.from_file(stat_path+'/KPOINTS')
            if system_dimension == '2D':
                temp_list = list(kptsY.kpts)
                temp_elem = list(temp_list[0])
                temp_elem[2] = 1                # Modify the third component
                temp_list[0] = tuple(temp_elem) # Convert it back to a tuple
                kptsY.kpts = temp_list
                kptsY.write_file(stat_path+'/KPOINTS')


            if randomise_cmd:
                cmd_rand2 = cmd[:]
                cmd_rand2[-1] = cmd_rand2[-1]+'_'+str(np.random.randint(0,9999))
                final_cmd2 = cmd_rand #[VaspJob(cmd_rand)]
            else:
                final_cmd2 = cmd
            
            os.chdir(stat_path)
            
            job = [VaspJob(final_cmd2)]
           
            custY = Custodian(
                stat_handlers, job, validator, max_errors=7, polling_time_step=5,
                monitor_freq=10, gzipped_output=False, checkpoint=False
            )

            msg = 'Running static run for config '+str(i2)
            log(msg)
            done2=0

            #os.chdir(stat_path)
            for j4 in range(3):
                try:
                    custY.run()
                    done2=1
                    sleep(10)
                    break
                except:
                    sleep(10)
                    continue
            os.chdir(root_path)

            if done2==1:
                msg = 'Static run finished successfully for config '+str(i2)
                log(msg)
            else:
                msg = 'Static run failed for config '+str(i2)
                log(msg)
                sys.exit()

        for axis in saxes:
            mae_path = root_path+'/MAE/config_'+str(i2)+'/'+str(axis).replace(' ','')
            cclean = sanitize(mae_path)
            if not cclean:                   
                soc_set = MPSOCSet.from_prev_calc(
                    stat_path, saxis=axis, nbands_factor=2,
                    reciprocal_density=kpt_den_stat, force_gamma=True,
                    user_potcar_functional=pot, sort_structure=False,
                    user_potcar_settings=potcar_provided,
                    user_incar_settings={"ENCUT": encut} if encut is not None else {}
                )
                soc_set.write_input(mae_path)
                if xc=='SCAN+RVV10' or xc=='R2SCAN+RVV10':
                    #copyfile(root_path+'/vdw_kernel.bindat', mae_path+'/vdw_kernel.bindat')
                    safe_symlink(root_path + '/vdw_kernel.bindat', mae_path + '/vdw_kernel.bindat')
                #replace_text(mae_path+'/INCAR','LCHARG = True','LCHARG = False')
                #replace_text(mae_path+'/INCAR','LWAVE = True','LWAVE = False')
                #replace_text(mae_path+'/INCAR','LAECHG = True','LAECHG = False')
                #replace_text(mae_path+'/INCAR','ICHARG = 2','ICHARG = 11')
                #replace_text(mae_path+'/INCAR','ISTART = 0','ISTART = 1')
                #replace_text(mae_path+'/INCAR','EDIFF = 1e-06','EDIFF = 1e-07')

                replace_or_add_input_tag(mae_path+'/INCAR', 'LCHARG', 'False')
                replace_or_add_input_tag(mae_path+'/INCAR', 'LWAVE', 'False')
                replace_or_add_input_tag(mae_path+'/INCAR', 'LAECHG', 'False')
                replace_or_add_input_tag(mae_path+'/INCAR', 'ICHARG', '11')
                replace_or_add_input_tag(mae_path+'/INCAR', 'ISTART', '1')
                replace_or_add_input_tag(mae_path+'/INCAR', 'EDIFF', '1e-07')

                
                
                
                if 'SCAN' in xc:
                    #replace_text(mae_path+'/INCAR','ICHARG = 11','ICHARG = 1')
                    replace_or_add_input_tag(mae_path+'/ICHARG', 'ICHARG', '1')
                    
                with open(mae_path+'/INCAR','a') as inc_d:
                    inc_d.write('\nKPAR = '+str(kpar)+'\nNPAR = '+str(npar)+'\nNCORE = '+str(ncore)+'\nLUSENCCL = '+str(nccl))
                kptsZ = Kpoints.from_file(mae_path+'/KPOINTS')
                if system_dimension == '2D':
                    temp_list = list(kptsZ.kpts)          # Convert the kpts tuple to a list
                    temp_elem = list(temp_list[0])         # Convert the first k-point (a tuple) to a list
                    temp_elem[2] = 1                       # Modify the third element
                    temp_list[0] = tuple(temp_elem)        # Convert it back to a tuple
                    kptsZ.kpts = temp_list                 # Reassign the modified list back to kpts
                    kptsZ.write_file(stat_path+'/KPOINTS')


                try:
                    safe_symlink(stat_path + '/WAVECAR', mae_path + '/WAVECAR',backup_dir= 'backup', use_temp_copy=True)
                    safe_symlink(stat_path + '/CHGCAR', mae_path + '/CHGCAR',backup_dir= 'backup', use_temp_copy=True)
                    
                    
                except FileNotFoundError as e:
                    msg = f'*** Required file not found: {e.filename}. Ensure both WAVECAR and CHGCAR are generated in the static run.'
                    log(msg)
                    sys.exit()
                except Exception as e:
                    msg = f'*** Unexpected error while copying WAVECAR/CHGCAR: {str(e)}'
                    log(msg)
                    sys.exit()

                    
                if randomise_cmd:
                    cmd_rand3 = cmd_ncl[:]
                    cmd_rand3[-1] = cmd_rand3[-1]+'_'+str(np.random.randint(0,9999))
                    final_cmd3 = cmd_rand3 #[VaspJob(cmd_rand3)]
                else:
                    final_cmd3 = cmd_ncl
                    
                os.chdir(mae_path)
                
                job = [VaspJob(final_cmd3)]
                                    
                custZ = Custodian(
                    stat_handlers, job, validator,
                    max_errors=7, polling_time_step=5,
                    monitor_freq=10, gzipped_output=False, checkpoint=False
                )
                msg = f'Executing a non-collinear run for config {i2} along the {axis} direction'
                log(msg)
                done3=0
                
                for j5 in range(3):
                    try:
                        custZ.run()
                        done3=1
                        sleep(10)
                        break
                    except:
                        sleep(10)
                        continue
                os.chdir(root_path)

                if done3==1:
                    msg = f'Non-collinear run finished successfully for config {i2} and direction {axis}'
                    log(msg)
                else:
                    msg = f'Non-collinear run failed for config {i2} and direction {axis}'
                    log(msg)
                    sys.exit()

                #os.remove(mae_path+'/CHGCAR')
                #os.remove(mae_path+'/WAVECAR')
                safe_remove(mae_path + '/WAVECAR')
                safe_remove(mae_path + '/CHGCAR')

    end_time_dft = time()
    time_dft = np.around(end_time_dft - start_time_dft, 2) 

    msg = f"All static and non-collinear anisotropy runs completed successfully. DFT energy calculations for all configurations took {time_dft:.2f} s."
    log(msg)


    msg = 'Attempting to collect data and fit the Hamiltonian now'
    log(msg)


    ###########################################################################
    # 5) collecting data from the final runs, fitting Hamiltonian, as original
    ###########################################################################
    global semifinal_list
    semifinal_list = []
    num_neigh2 = min([max_neigh, num_struct-1])
    msg = 'total '+str(num_struct)+' valid FM/AFM configs have been detected, including '
    msg += str(num_neigh2)+' nearest-neighbors in the fitting'
    log(msg)

    for i2 in range(num_struct):
        msg = f"Checking status of static and non-collinear calculations for config_{i2}"
        log(msg)
        config_info = []
        stat_path = root_path+'/static_runs'+'/config_'+str(i2)
        struct2 = Structure.from_file(root_path+'/static_runs/config_'+str(i2)+'/POSCAR')
        inc2 = Incar.from_file(root_path+'/static_runs/config_'+str(i2)+'/INCAR')
        struct2.add_spin_by_site(inc2.as_dict()['MAGMOM'])
        run2 = Vasprun(stat_path+'/vasprun.xml',parse_dos=False,parse_eigen=False)
        if not run2.converged_electronic:
            msg = f"*** Static calculation failed to converge for config_{i2}. Exiting. ***"
            log(msg)
            sys.exit()
        else:
            msg = f"Static run successfully converged for config_{i2}."
            log(msg)

        energy2 = float(run2.final_energy)
        config_info.append(i2)
        config_info.append(struct2)
        config_info.append(energy2)

        for axis in saxes:
            mae_path = root_path+'/MAE/config_'+str(i2)+'/'+str(axis).replace(' ','')
            run_mae = Vasprun(mae_path+'/vasprun.xml',parse_dos=False,parse_eigen=False)
            struct3 = Structure.from_file(mae_path+'/POSCAR')
            if not run_mae.converged_electronic:
                msg = f"❌ Non-collinear run failed to converge for config_{i2}, axis: {axis}. Exiting."
                log(msg)
                sys.exit()
            else:
                msg = 'Found converged non-collinear run'
                log(msg)
            energy3 = float(run_mae.final_energy)
            config_info.append(energy3)
            if not ortho_ab and axis==(1,0,0):
                config_info.append(energy3)

        semifinal_list.append(config_info)

    semifinal_list = sorted(semifinal_list, key = lambda x : x[2])
    most_stable2 = semifinal_list[0][0]

    msg = f"✅ Most stable configuration → config_{most_stable2}"
    log(msg)


    num_spin_axes = len(spin_axes)
    energies_ncl = semifinal_list[0][3:3+num_spin_axes]
    #energies_ncl = semifinal_list[0][3:]
    global EMA
    EMA = np.argmin(energies_ncl)
    #saxes2 = [(1,0,0),(0,1,0),(0,0,1)]
    msg = '### The easy magnetization axis (EMA) = '+str(saxes[EMA])
    log(msg)


    num_spin_axes = len(saxes)
    if num_spin_axes < 2:
        log("Error: At least two spin axes are needed to compute anisotropy energies.")
    else:
        # Slice exactly the number of non-collinear energies corresponding to the spin axes.
        #energies_ncl = semifinal_list[0][3:3+num_spin_axes]
        analyzer2 = CollinearMagneticStructureAnalyzer(
            semifinal_list[0][1],
            overwrite_magmom_mode='replace_all_if_undefined',
            make_primitive=False
        )
        num_mag_atoms = analyzer2.number_of_magnetic_sites

        ref_axis = saxes[-1]
        log("### Magnetocrystalline anisotropic energies (MAE) are:")
        for i, axis in enumerate(saxes):
            if i == num_spin_axes - 1:
                continue  # Skip the reference axis itself.
            # Compute the energy difference per magnetic atom.
            E_diff = (energies_ncl[i] - energies_ncl[-1]) / num_mag_atoms
            log(f"E[{axis}]-E[{ref_axis}] = {E_diff*1e6:.3f} ueV/magnetic_atom")

    global S_stable
    global magmom_stable
    S_stable = 0.0
    magmom_stable = 0.0

    for i3 in range(len(semifinal_list)):
        config_id = semifinal_list[i3][0]
        spath = root_path+'/static_runs'+'/config_'+str(config_id)
        if mag_from=='Bader' and config_id==most_stable2:
            if not os.path.exists(spath+'/bader.dat'):
                msg = 'starting bader analysis for config_'+str(config_id)
                log(msg)
                ba = bader_analysis_from_path(spath)
                msg = 'Finished bader analysis successfully'
                log(msg)
                with open(spath+'/bader.dat','wb') as f_b:
                    dump(ba,f_b)
            else:
                with open(spath+'/bader.dat','rb') as f_b:
                    ba = load(f_b)
                msg = 'Reading magmoms from bader file'
                log(msg)
            magmom_stable = max(ba['magmom'])
            S_stable = magmom_stable/2.0
        elif mag_from=='OSZICAR' and config_id==0:
            osz = Oszicar(spath+'/OSZICAR')
            config_magmom = float(osz.ionic_steps[-1]['mag'])
            analyzer3 = CollinearMagneticStructureAnalyzer(
                semifinal_list[i3][1],
                overwrite_magmom_mode='replace_all_if_undefined', make_primitive=False
            )
            n_mg_at = analyzer3.number_of_magnetic_sites
            magmom_stable = config_magmom/n_mg_at
            S_stable = magmom_stable/2.0

    E0 = Symbol('E0')
    global J1,J2,J3,J4
    J1 = Symbol('J1')
    J2 = Symbol('J2')
    J3 = Symbol('J3')
    J4 = Symbol('J4')
    global K1x,K1y,K1z
    K1x = Symbol('K1x')
    K1y = Symbol('K1y')
    K1z = Symbol('K1z')
    global K2x,K2y,K2z
    K2x = Symbol('K2x')
    K2y = Symbol('K2y')
    K2z = Symbol('K2z')
    global K3x,K3y,K3z
    K3x = Symbol('K3x')
    K3y = Symbol('K3y')
    K3z = Symbol('K3z')
    global K4x,K4y,K4z
    K4x = Symbol('K4x')
    K4y = Symbol('K4y')
    K4z = Symbol('K4z')
    global Ax,Ay,Az
    Ax = Symbol('Ax')
    Ay = Symbol('Ay')
    Az = Symbol('Az')

    ###############################################################################
    # 5) Fit the Heisenberg + anisotropy Hamiltonian using the final (static + SOC) data
    ###############################################################################

    # Suppose we have:
    # - semifinal_list: a list of [config_id, structure, E_static, E_soc_axis1, E_soc_axis2, E_soc_axis3, ...]
    # - most_stable2: index of the “most stable” config
    # - We already defined E0, J1, J2, J3, J4, K1x...K4z, Ax, Ay, Az as sympy Symbols
    # - We have also done: 'magmom_stable' and 'ds_stable' from the most stable structure
    # - We have 'ortho_ab' as a bool controlling whether to do x,y,z or x,z only
    # - We have 'num_neigh2 = min([max_neigh, num_struct-1])' from above

    fitted = False
    num_neigh_used = num_neigh2  # e.g. num_neigh2 = min([max_neigh, num_struct - 1])

    while num_neigh_used > 0:
        final_list = semifinal_list[: (num_neigh_used + 1)]
        num_config = len(final_list)

        eqn_set_iso = [0] * num_config
        eqn_set_x   = [0] * num_config
        eqn_set_y   = [0] * num_config
        eqn_set_z   = [0] * num_config

        # For logging average coordination numbers:
        CN1s, CN2s, CN3s, CN4s = [], [], [], []

        # -------------------------------------------------------------------------
        # 1) Build the symbolic equations for each configuration
        # -------------------------------------------------------------------------
        for i in range(num_config):
            config_id   = final_list[i][0]
            struct      = final_list[i][1]
            energy_iso  = final_list[i][2]       # collinear E
            energies_ncl= final_list[i][3:]      # spin-axis energies, e.g. [Ex, Ey, Ez]
            stat_path   = os.path.join(root_path, "static_runs", f"config_{config_id}")
            out = Outcar(os.path.join(stat_path, "OUTCAR"))

            # (a) Collect only magnetic sites
            sites_mag = []
            magmoms_mag = []
            magmoms_out = []
            for j in range(len(struct)):
                elem = struct[j].specie.element
                if elem in magnetic_list_local:
                    sign_magmom = np.sign(struct[j].specie.spin)
                    # Use the stable magnitude for each site
                    magmom = sign_magmom * magmom_stable
                    magmoms_mag.append(magmom)
                    sites_mag.append(struct[j])
                    # read actual OUTCAR magmom
                    magmoms_out.append(out.magnetization[j]["tot"])

            # (b) Build smaller structures with only those sites
            struct_mag = Structure.from_sites(sites_mag)
            struct_mag_out = Structure.from_sites(sites_mag)
            struct_mag.remove_spin()
            struct_mag.add_site_property("magmom", magmoms_mag)

            struct_mag_out.add_site_property("magmom", magmoms_out)

            N = len(struct_mag)
            log(f"config_{config_id} (magnetic atoms only) =>")
            log(struct_mag)
            log("Magmoms from OUTCAR =>")
            log(struct_mag_out)

            ds = dist_neighbors(struct_mag)
            dr = ds[0]

            # eqn_iso = (E0) - (energy_iso)
            eqn_iso = E0 - energy_iso
            # eqn_x   = energy_iso - energies_ncl[0], etc.
            eqn_x = energy_iso - energies_ncl[0]
            eqn_y = energy_iso - energies_ncl[1]
            eqn_z = energy_iso - energies_ncl[2]

            # (c) Build neighbor-based J + K terms
            for j in range(N):
                S_site = struct_mag.site_properties["magmom"][j] / 2.0

                # Decide how many neighbor shells we actually consider
                if num_config == 2:
                    N1s = Nfinder(struct_mag, j, ds[1], dr)
                    N2s, N3s, N4s = [], [], []
                elif num_config == 3:
                    N1s = Nfinder(struct_mag, j, ds[1], dr)
                    N2s = Nfinder(struct_mag, j, ds[2], dr)
                    N3s, N4s = [], []
                elif num_config == 4:
                    N1s = Nfinder(struct_mag, j, ds[1], dr)
                    N2s = Nfinder(struct_mag, j, ds[2], dr)
                    N3s = Nfinder(struct_mag, j, ds[3], dr)
                    N4s = []
                else:  # num_config==5
                    N1s = Nfinder(struct_mag, j, ds[1], dr)
                    N2s = Nfinder(struct_mag, j, ds[2], dr)
                    N3s = Nfinder(struct_mag, j, ds[3], dr)
                    N4s = Nfinder(struct_mag, j, ds[4], dr)

                # J1 / K1
                for nb in N1s:
                    S_nb = struct_mag.site_properties["magmom"][nb] / 2.0
                    eqn_iso += -0.5 * J1 * S_site * S_nb
                    eqn_x   += -0.5 * K1x * S_site * S_nb
                    eqn_y   += -0.5 * K1y * S_site * S_nb
                    eqn_z   += -0.5 * K1z * S_site * S_nb

                # J2 / K2
                for nb in N2s:
                    S_nb = struct_mag.site_properties["magmom"][nb] / 2.0
                    eqn_iso += -0.5 * J2 * S_site * S_nb
                    eqn_x   += -0.5 * K2x * S_site * S_nb
                    eqn_y   += -0.5 * K2y * S_site * S_nb
                    eqn_z   += -0.5 * K2z * S_site * S_nb

                # J3 / K3
                for nb in N3s:
                    S_nb = struct_mag.site_properties["magmom"][nb] / 2.0
                    eqn_iso += -0.5 * J3 * S_site * S_nb
                    eqn_x   += -0.5 * K3x * S_site * S_nb
                    eqn_y   += -0.5 * K3y * S_site * S_nb
                    eqn_z   += -0.5 * K3z * S_site * S_nb

                # J4 / K4
                for nb in N4s:
                    S_nb = struct_mag.site_properties["magmom"][nb] / 2.0
                    eqn_iso += -0.5 * J4 * S_site * S_nb
                    eqn_x   += -0.5 * K4x * S_site * S_nb
                    eqn_y   += -0.5 * K4y * S_site * S_nb
                    eqn_z   += -0.5 * K4z * S_site * S_nb

                # single-ion anisotropy
                eqn_x += -Ax * (S_site**2)
                eqn_y += -Ay * (S_site**2)
                eqn_z += -Az * (S_site**2)

                CN1s.append(len(N1s))
                CN2s.append(len(N2s))
                CN3s.append(len(N3s))
                CN4s.append(len(N4s))

            eqn_set_iso[i] = eqn_iso
            eqn_set_x[i]   = eqn_x
            eqn_set_y[i]   = eqn_y
            eqn_set_z[i]   = eqn_z

            # If this config is the most stable, store struct + ds
            if config_id == most_stable2:
                struct_mag_stable = struct_mag
                ds_stable = ds

        log(f"### mu = {magmom_stable} bohr magnetron/magnetic atom")
        log("eqns are:")

        for eqn in eqn_set_iso:
            log(str(eqn) + " = 0")
        for eqn in eqn_set_x:
            log(str(eqn) + " = 0")
        if ortho_ab:
            for eqn in eqn_set_y:
                log(str(eqn) + " = 0")
        for eqn in eqn_set_z:
            log(str(eqn) + " = 0")

        # -------------------------------------------------------------------------
        # 2) Symbolic solve
        # -------------------------------------------------------------------------
        if num_config == 2:
            soln_iso_raw = linsolve(eqn_set_iso, E0, J1)
            soln_x_raw   = linsolve(eqn_set_x,   K1x, Ax)
            if ortho_ab:
                soln_y_raw = linsolve(eqn_set_y, K1y, Ay)
            else:
                soln_y_raw = []
            soln_z_raw   = linsolve(eqn_set_z,   K1z, Az)

        elif num_config == 3:
            soln_iso_raw = linsolve(eqn_set_iso, E0, J1, J2)
            soln_x_raw   = linsolve(eqn_set_x,   K1x, K2x, Ax)
            if ortho_ab:
                soln_y_raw = linsolve(eqn_set_y, K1y, K2y, Ay)
            else:
                soln_y_raw = []
            soln_z_raw   = linsolve(eqn_set_z,   K1z, K2z, Az)

        elif num_config == 4:
            soln_iso_raw = linsolve(eqn_set_iso, E0, J1, J2, J3)
            soln_x_raw   = linsolve(eqn_set_x,   K1x, K2x, K3x, Ax)
            if ortho_ab:
                soln_y_raw = linsolve(eqn_set_y, K1y, K2y, K3y, Ay)
            else:
                soln_y_raw = []
            soln_z_raw   = linsolve(eqn_set_z,   K1z, K2z, K3z, Az)
        else:  # num_config==5
            soln_iso_raw = linsolve(eqn_set_iso, E0, J1, J2, J3, J4)
            soln_x_raw   = linsolve(eqn_set_x,   K1x, K2x, K3x, K4x, Ax)
            if ortho_ab:
                soln_y_raw = linsolve(eqn_set_y, K1y, K2y, K3y, K4y, Ay)
            else:
                soln_y_raw = []
            soln_z_raw   = linsolve(eqn_set_z,   K1z, K2z, K3z, K4z, Az)

        # Convert symbolic solution sets to lists
        soln_iso = list(soln_iso_raw)
        soln_x   = list(soln_x_raw)
        soln_y   = list(soln_y_raw)
        soln_z   = list(soln_z_raw)

        log("Symbolic solutions =>")
        log(soln_iso)
        log(soln_x)
        log(soln_y)
        log(soln_z)

        def is_symbolic_ok():
            """Check if the symbolic solutions are non-empty and < 5e3 in magnitude."""
            try:
                # Each solution is typically a single tuple. We check none are empty
                have_iso = (soln_iso and len(soln_iso[0]) > 0)
                have_x   = (soln_x   and len(soln_x[0])   > 0)
                have_y   = (soln_y   and len(soln_y[0])   > 0) if ortho_ab else True
                have_z   = (soln_z   and len(soln_z[0])   > 0)
                if not (have_iso and have_x and have_y and have_z):
                    return False

                # Also check magnitude
                if np.max(np.abs(soln_iso[0])) > 5e3: return False
                if np.max(np.abs(soln_x[0]))   > 5e3: return False
                if ortho_ab and np.max(np.abs(soln_y[0])) > 5e3: return False
                if np.max(np.abs(soln_z[0]))   > 5e3: return False
                return True
            except:
                return False

        if is_symbolic_ok():
            fitted = True
            log("Symbolic solution accepted.")
            break
        else:
            log("Symbolic solve failed or unphysical. Attempting numeric least-squares now.")

            # ---------------------------------------------------------------------
            # 3) Numeric fallback with possible random noise
            # ---------------------------------------------------------------------
            all_eqns = eqn_set_iso + eqn_set_x
            if ortho_ab:
                all_eqns += eqn_set_y
            all_eqns += eqn_set_z

            # 3a) Define the unknowns in a consistent order
            if num_config == 2:
                if ortho_ab:
                    unknowns = [E0, J1, K1x, Ax, K1y, Ay, K1z, Az]
                else:
                    unknowns = [E0, J1, K1x, Ax, K1z, Az]

            elif num_config == 3:
                if ortho_ab:
                    unknowns = [E0, J1, J2, K1x, K2x, Ax, K1y, K2y, Ay, K1z, K2z, Az]
                else:
                    unknowns = [E0, J1, J2, K1x, K2x, Ax, K1z, K2z, Az]

            elif num_config == 4:
                if ortho_ab:
                    unknowns = [
                        E0, J1, J2, J3, K1x, K2x, K3x, Ax,
                        K1y, K2y, K3y, Ay, K1z, K2z, K3z, Az
                    ]
                else:
                    unknowns = [
                        E0, J1, J2, J3, K1x, K2x, K3x, Ax,
                        K1z, K2z, K3z, Az
                    ]
            else:  # num_config==5
                if ortho_ab:
                    unknowns = [
                        E0, J1, J2, J3, J4,
                        K1x, K2x, K3x, K4x, Ax,
                        K1y, K2y, K3y, K4y, Ay,
                        K1z, K2z, K3z, K4z, Az
                    ]
                else:
                    unknowns = [
                        E0, J1, J2, J3, J4,
                        K1x, K2x, K3x, K4x, Ax,
                        K1z, K2z, K3z, K4z, Az
                    ]

            # 3b) Convert eqns => A x = b
            A_rows = []
            b_rows = []
            for eqn_expr in all_eqns:
                expr = expand(eqn_expr)
                row_coeffs = []
                for symb in unknowns:
                    c = float(expr.diff(symb))
                    row_coeffs.append(c)
                const_val = float(expr.subs({v: 0 for v in unknowns}))
                A_rows.append(row_coeffs)
                b_rows.append(-const_val)

            A = np.array(A_rows, dtype=float)
            b = np.array(b_rows, dtype=float)

            # 3c) Attempt numeric solve
            try:
                x_sol, residuals, rank, sing_vals = lstsq(A, b, rcond=None)

                if rank < len(unknowns):
                    log(
                        f"Numeric solve is rank-deficient (rank={rank}, unknowns={len(unknowns)}). "
                        "Attempting Tikhonov regularization."
                    )

                    # Tikhonov regularization
                    lambda_reg = 1e-4  # tunable regularization parameter
                    A_reg = np.vstack([A, lambda_reg * np.identity(len(unknowns))])
                    b_reg = np.concatenate([b, np.zeros(len(unknowns))])

                    x_sol_reg, residuals_reg, rank_reg, sing_vals_reg = lstsq(A_reg, b_reg, rcond=None)

                    # Check if regularization addressed the issue
                    if rank_reg < len(unknowns):
                        log(
                            f"Regularization still rank-deficient (rank={rank_reg}/{len(unknowns)}). "
                            "Attempting random noise injection."
                        )

                        # Random noise injection (as final fallback)
                        noise_level = 1e-4
                        b_perturbed = b + np.random.normal(0.0, noise_level, b.shape)
                        x_sol_noise, residuals_noise, rank_noise, _ = lstsq(A, b_perturbed, rcond=None)

                        if rank_noise < len(unknowns):
                            log("Noise injection failed to fix rank deficiency; using best effort solution.")
                        else:
                            log("Noise injection successfully improved rank; using perturbed solution.")
                            x_sol = x_sol_noise
                            residuals = residuals_noise
                            rank = rank_noise
                    else:
                        log("Regularization successfully addressed rank deficiency; using regularized solution.")
                        x_sol = x_sol_reg
                        residuals = residuals_reg
                        rank = rank_reg

                log(f"LSQ solution: residual={residuals}, rank={rank}/{len(unknowns)}")
                log("Numeric solution vector (x_sol):")
                log(x_sol)
                fitted = True
                break

            except Exception as e:
                log(f"Exception encountered during least squares fitting: {e}")
                fitted = False

            if not fitted:
                num_neigh_used -= 1
                log(
                    "No success even after random noise injection. "
                    f"Reducing neighbor shells => {num_neigh_used}"
                )

        # Final fallback => If we STILL do not have a solution, set everything to zero
        if not fitted:
            log("We STILL have no solution after all attempts. Setting J=K=A=0 as final fallback.")
            fitted = True

    semifinal_list = final_list

        
        # e.g. E0_val = 0, J1_val=0, etc.

    # Logging average coordination #s
    CN1 = np.mean(CN1s) if CN1s else 0
    CN2 = np.mean(CN2s) if CN2s else 0
    CN3 = np.mean(CN3s) if CN3s else 0
    CN4 = np.mean(CN4s) if CN4s else 0

    if ortho_ab:
        log("Orthogonal a/b => we can do full XYZ model.")
    else:
        log("Non-orthogonal => merging Y into X => an XXZ approach.")

    log("Fitting is done. 'fitted' = True => carrying on to MC step...")

    ###############################################################################
    #             UNPACK THE FINAL SOLUTIONS FOR num_config = 2,3,4,5
    ###############################################################################
    # We show how to read the final (E0, J, K, A) from either the symbolic
    # arrays soln_iso, soln_x, etc. OR from the numeric array x_sol.

    if num_config == 2:
        # Check if we used symbolic
        if soln_iso and len(soln_iso) > 0:
            # e.g. soln_iso[0] = (E0_val, J1_val)
            E0_val, J1_val = soln_iso[0]
            K1x_val, Ax_val = soln_x[0]
            if ortho_ab and soln_y and len(soln_y) > 0:
                K1y_val, Ay_val = soln_y[0]
            else:
                K1y_val, Ay_val = 0.0, 0.0
            K1z_val, Az_val = soln_z[0]
        else:
            # numeric => read from x_sol in the order we assigned
            if ortho_ab:
                # unknowns = [E0, J1, K1x, Ax, K1y, Ay, K1z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                K1x_val = x_sol[2]
                Ax_val  = x_sol[3]
                K1y_val = x_sol[4]
                Ay_val  = x_sol[5]
                K1z_val = x_sol[6]
                Az_val  = x_sol[7]
            else:
                # unknowns = [E0, J1, K1x, Ax, K1z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                K1x_val = x_sol[2]
                Ax_val  = x_sol[3]
                K1y_val = 0.0
                Ay_val  = 0.0
                K1z_val = x_sol[4]
                Az_val  = x_sol[5]

        # We do not have J2, J3, J4 => set them 0
        J2_val, J3_val, J4_val = 0, 0, 0
        # Build K1 => [K1x, K1y, K1z], K2=K3=K4 => [0,0,0]
        K1 = np.array([K1x_val, K1y_val, K1z_val])
        K2 = np.zeros(3)
        K3 = np.zeros(3)
        K4 = np.zeros(3)
        A  = np.array([Ax_val, Ay_val, Az_val])

        # Logging
        msg = "NN coordinations for all configs: " + str(CN1s)
        log(msg)
        msg = "### The solutions are:"
        log(msg)
        msg = f"E0 = {E0_val} eV"
        log(msg)
        msg = (
            f"J1 = {J1_val*1e3:.3f} meV/link with d1={ds_stable[1]} Å; avg. CN1 = {CN1}"
        )
        log(msg)
        msg = f"K1 = {K1*1e3} meV/link"
        log(msg)
        msg = f"A = {A*1e3} meV/magnetic_atom"
        log(msg)

    elif num_config == 3:
        if soln_iso and len(soln_iso) > 0:
            E0_val, J1_val, J2_val = soln_iso[0]
            K1x_val, K2x_val, Ax_val = soln_x[0]
            if ortho_ab and soln_y and len(soln_y) > 0:
                K1y_val, K2y_val, Ay_val = soln_y[0]
            else:
                K1y_val, K2y_val, Ay_val = 0.0, 0.0, 0.0
            K1z_val, K2z_val, Az_val  = soln_z[0]
        else:
            # numeric => check if ortho
            if ortho_ab:
                # unknowns = [E0, J1, J2, K1x, K2x, Ax, K1y, K2y, Ay, K1z, K2z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                K1x_val = x_sol[3]
                K2x_val = x_sol[4]
                Ax_val  = x_sol[5]
                K1y_val = x_sol[6]
                K2y_val = x_sol[7]
                Ay_val  = x_sol[8]
                K1z_val = x_sol[9]
                K2z_val = x_sol[10]
                Az_val  = x_sol[11]
            else:
                # unknowns = [E0, J1, J2, K1x, K2x, Ax, K1z, K2z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                K1x_val = x_sol[3]
                K2x_val = x_sol[4]
                Ax_val  = x_sol[5]
                K1y_val, K2y_val, Ay_val = 0.0, 0.0, 0.0
                K1z_val = x_sol[6]
                K2z_val = x_sol[7]
                Az_val  = x_sol[8]

        # We do not have J3,J4 => 0
        J3_val = 0
        J4_val = 0
        # K1 => [K1x, K1y, K1z]; K2 => [K2x, K2y, K2z]; K3=K4 => 0
        K1 = np.array([K1x_val, K1y_val, K1z_val])
        K2 = np.array([K2x_val, K2y_val, K2z_val])
        K3 = np.zeros(3)
        K4 = np.zeros(3)
        A  = np.array([Ax_val, Ay_val, Az_val])

        # Log final solutions
        msg = "NN coordinations: " + str(CN1s)
        log(msg)
        msg = "NNN coordinations: " + str(CN2s)
        log(msg)
        msg = "### The solutions are:"
        log(msg)
        msg = f"E0 = {E0_val} eV"
        log(msg)
        msg = (
            f"J1 = {J1_val*1e3:.3f} meV/link with d1={ds_stable[1]} Å; J2={J2_val*1e3:.3f} meV/link with d2={ds_stable[2]} Å"
        )
        log(msg)
        msg = f"K1 = {K1*1e3} meV/link"
        log(msg)
        msg = f"K2 = {K2*1e3} meV/link"
        log(msg)
        msg = f"A = {A*1e3} meV/magnetic_atom"
        log(msg)

    elif num_config == 4:
        if soln_iso and len(soln_iso) > 0:
            E0_val, J1_val, J2_val, J3_val = soln_iso[0]
            K1x_val, K2x_val, K3x_val, Ax_val = soln_x[0]
            if ortho_ab and soln_y and len(soln_y) > 0:
                K1y_val, K2y_val, K3y_val, Ay_val = soln_y[0]
            else:
                K1y_val, K2y_val, K3y_val, Ay_val = 0.0, 0.0, 0.0, 0.0
            K1z_val, K2z_val, K3z_val, Az_val  = soln_z[0]
        else:
            # numeric
            if ortho_ab:
                # unknowns = [E0, J1, J2, J3, K1x, K2x, K3x, Ax, K1y, K2y, K3y, Ay, K1z, K2z, K3z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                J3_val  = x_sol[3]
                K1x_val = x_sol[4]
                K2x_val = x_sol[5]
                K3x_val = x_sol[6]
                Ax_val  = x_sol[7]
                K1y_val = x_sol[8]
                K2y_val = x_sol[9]
                K3y_val = x_sol[10]
                Ay_val  = x_sol[11]
                K1z_val = x_sol[12]
                K2z_val = x_sol[13]
                K3z_val = x_sol[14]
                Az_val  = x_sol[15]
            else:
                # unknowns = [E0, J1, J2, J3, K1x, K2x, K3x, Ax, K1z, K2z, K3z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                J3_val  = x_sol[3]
                K1x_val = x_sol[4]
                K2x_val = x_sol[5]
                K3x_val = x_sol[6]
                Ax_val  = x_sol[7]
                K1y_val, K2y_val, K3y_val, Ay_val = 0.0, 0.0, 0.0, 0.0
                K1z_val = x_sol[8]
                K2z_val = x_sol[9]
                K3z_val = x_sol[10]
                Az_val  = x_sol[11]

        # J4=0
        J4_val = 0
        # K1 => [K1x, K1y, K1z], etc.
        K1 = np.array([K1x_val, K1y_val, K1z_val])
        K2 = np.array([K2x_val, K2y_val, K2z_val])
        K3 = np.array([K3x_val, K3y_val, K3z_val])
        K4 = np.zeros(3)
        A  = np.array([Ax_val, Ay_val, Az_val])

        # Log
        msg = "### The solutions for num_config=4 are:"
        log(msg)
        msg = f"E0 = {E0_val} eV"
        log(msg)
        msg = (
            f"J1={J1_val*1e3:.3f} meV, J2={J2_val*1e3:.3f}, J3={J3_val*1e3:.3f}"
            f" with d1={ds_stable[1]} Å, d2={ds_stable[2]}, d3={ds_stable[3]}"
        )
        log(msg)
        msg = f"K1= {K1*1e3} meV/link"
        log(msg)
        msg = f"K2= {K2*1e3} meV/link"
        log(msg)
        msg = f"K3= {K3*1e3} meV/link"
        log(msg)
        msg = f"A= {A*1e3} meV/magnetic_atom"
        log(msg)

    else:  # num_config==5
        if soln_iso and len(soln_iso) > 0:
            E0_val, J1_val, J2_val, J3_val, J4_val = soln_iso[0]
            K1x_val, K2x_val, K3x_val, K4x_val, Ax_val = soln_x[0]
            if ortho_ab and soln_y and len(soln_y) > 0:
                K1y_val, K2y_val, K3y_val, K4y_val, Ay_val = soln_y[0]
            else:
                K1y_val, K2y_val, K3y_val, K4y_val, Ay_val = 0.0, 0.0, 0.0, 0.0, 0.0
            K1z_val, K2z_val, K3z_val, K4z_val, Az_val = soln_z[0]
        else:
            # numeric
            if ortho_ab:
                # unknowns = [E0, J1, J2, J3, J4, K1x, K2x, K3x, K4x, Ax, K1y, K2y, K3y, K4y, Ay, K1z, K2z, K3z, K4z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                J3_val  = x_sol[3]
                J4_val  = x_sol[4]
                K1x_val = x_sol[5]
                K2x_val = x_sol[6]
                K3x_val = x_sol[7]
                K4x_val = x_sol[8]
                Ax_val  = x_sol[9]
                K1y_val = x_sol[10]
                K2y_val = x_sol[11]
                K3y_val = x_sol[12]
                K4y_val = x_sol[13]
                Ay_val  = x_sol[14]
                K1z_val = x_sol[15]
                K2z_val = x_sol[16]
                K3z_val = x_sol[17]
                K4z_val = x_sol[18]
                Az_val  = x_sol[19]
            else:
                # unknowns = [E0, J1, J2, J3, J4, K1x, K2x, K3x, K4x, Ax, K1z, K2z, K3z, K4z, Az]
                E0_val  = x_sol[0]
                J1_val  = x_sol[1]
                J2_val  = x_sol[2]
                J3_val  = x_sol[3]
                J4_val  = x_sol[4]
                K1x_val = x_sol[5]
                K2x_val = x_sol[6]
                K3x_val = x_sol[7]
                K4x_val = x_sol[8]
                Ax_val  = x_sol[9]
                K1y_val, K2y_val, K3y_val, K4y_val, Ay_val = 0,0,0,0,0
                K1z_val = x_sol[10]
                K2z_val = x_sol[11]
                K3z_val = x_sol[12]
                K4z_val = x_sol[13]
                Az_val  = x_sol[14]

        # Build K1,K2,K3,K4 => each is [K?x_val, K?y_val, K?z_val]
        K1 = np.array([K1x_val, K1y_val, K1z_val])
        K2 = np.array([K2x_val, K2y_val, K2z_val])
        K3 = np.array([K3x_val, K3y_val, K3z_val])
        K4 = np.array([K4x_val, K4y_val, K4z_val])
        A  = np.array([Ax_val, Ay_val, Az_val])

        # Log
        msg = "### The solutions for num_config=5 are:"
        log(msg)
        msg = f"E0 = {E0_val} eV"
        log(msg)
        msg = (
            f"J1={J1_val*1e3:.3f} meV, J2={J2_val*1e3:.3f} meV, J3={J3_val*1e3:.3f} meV, J4={J4_val*1e3:.3f} meV"
            f" with d1={ds_stable[1]}, d2={ds_stable[2]}, d3={ds_stable[3]}, d4={ds_stable[4]}"
        )
        log(msg)
        msg = f"K1= {K1*1e3} meV/link"
        log(msg)
        msg = f"K2= {K2*1e3} meV/link"
        log(msg)
        msg = f"K3= {K3*1e3} meV/link"
        log(msg)
        msg = f"K4= {K4*1e3} meV/link"
        log(msg)
        msg = f"A= {A*1e3} meV/magnetic_atom"
        log(msg)

    # Finally do your “d1/d2 >= 0.8 => add 2nd neighbor” checks, etc.
    if ds_stable[1] / ds_stable[2] >= 0.8:
        msg = "** d1/d2 >= 0.8 => consider adding 2nd neighbor for accuracy"
        log(msg)
    elif ds_stable[1] / ds_stable[3] >= 0.7:
        msg = "** d1/d3 >= 0.7 => consider adding 3rd neighbor for accuracy"
        log(msg)

    msg = "Hamiltonian fitting procedure finished successfully, now starting the Monte-Carlo simulation."
    log(msg)



    ###########################################################################
    # EXACT chunk that writes "input_MC" if not found, or reads it, etc.
    # then does final MC: we do expansions for E, M, Cv, Chi, no placeholders.
    ###########################################################################

    if not os.path.exists(root_path+'/input_MC'):
        msg = 'No input_MC file detected, creating one!'
        log(msg)


        J1_eV = J1_val #* 1e-3
        J2_eV = J2_val #* 1e-3
        J3_eV = J3_val #* 1e-3
        J4_eV = J4_val #* 1e-3
        K1x_eV = K1[0] #* 1e-3
        K1y_eV = K1[1] #* 1e-3
        K1z_eV = K1[2] #* 1e-3
        K2x_eV = K2[0] #* 1e-3
        K2y_eV = K2[1] #* 1e-3
        K2z_eV = K2[2] #* 1e-3
        K3x_eV = K3[0] #* 1e-3
        K3y_eV = K3[1] #* 1e-3
        K3z_eV = K3[2] #* 1e-3
        K4x_eV = K4[0] #* 1e-3
        K4y_eV = K4[1] #* 1e-3
        K4z_eV = K4[2] #* 1e-3
        Ax_eV  = A[0]  #* 1e-3
        Ay_eV  = A[1]  #* 1e-3
        Az_eV  = A[2]  #* 1e-3

        J1 = J1_val
        J2 = J2_val
        J3 = J3_val
        J4 = J4_val
        

        # You can define T_MF (the MC end temperature) based on your fitted parameters:
#        T_MF = abs((S_stable*(S_stable+1)/(3*kB))*(J1*len(N1s)) +
#                  (S_stable*(S_stable+1)/(3*kB))*(J2*len(N2s)) +
#                  (S_stable*(S_stable+1)/(3*kB))*(J3*len(N3s)) +
#                  (S_stable*(S_stable+1)/(3*kB))*(J4*len(N4s)))
                  
        T_MF = (S_stable * (S_stable + 1) / (3 * kB)) * abs(sum(J * len(N) for J, N in zip([J1, J2, J3, J4], [N1s, N2s, N3s, N4s])))

        # Ensure T_MF is at least 100 if it falls below 50
        T_MF = max(T_MF, 100) if T_MF < 50 else T_MF
        
        
        temps = np.arange(1e-6, int(math.ceil(T_MF)) + 1, 1.0)
        div_T = temps.size




        with open('input_MC', 'w') as f_mc:
            f_mc.write("directory = MC_Heisenberg\n")
            f_mc.write("repeat = 25 25 1\n")
            f_mc.write("restart = 0\n")
            f_mc.write(f"J1 (eV/link) = {J1_eV:.9f}\n")
            f_mc.write(f"J2 (eV/link) = {J2_eV:.9f}\n")
            f_mc.write(f"J3 (eV/link) = {J3_eV:.9f}\n")
            f_mc.write(f"J4 (eV/link) = {J4_eV:.9f}\n")
            f_mc.write(f"K1x (eV/link) = {K1x_eV:.9e}\n")
            f_mc.write(f"K1y (eV/link) = {K1y_eV:.9e}\n")
            f_mc.write(f"K1z (eV/link) = {K1z_eV:.9e}\n")
            f_mc.write(f"K2x (eV/link) = {K2x_eV:.9e}\n")
            f_mc.write(f"K2y (eV/link) = {K2y_eV:.9e}\n")
            f_mc.write(f"K2z (eV/link) = {K2z_eV:.9e}\n")
            f_mc.write(f"K3x (eV/link) = {K3x_eV:.9e}\n")
            f_mc.write(f"K3y (eV/link) = {K3y_eV:.9e}\n")
            f_mc.write(f"K3z (eV/link) = {K3z_eV:.9e}\n")
            f_mc.write(f"K4x (eV/link) = {K4x_eV:.9e}\n")
            f_mc.write(f"K4y (eV/link) = {K4y_eV:.9e}\n")
            f_mc.write(f"K4z (eV/link) = {K4z_eV:.9e}\n")
            f_mc.write(f"Ax (eV/mag_atom) = {Ax_eV:.9e}\n")
            f_mc.write(f"Ay (eV/mag_atom) = {Ay_eV:.9e}\n")
            f_mc.write(f"Az (eV/mag_atom) = {Az_eV:.9e}\n")
            f_mc.write(f"mu (mu_B/mag_atom) = {magmom_stable}\n")
            f_mc.write(f"EMA = {EMA}\n")
            f_mc.write("T_start (K) = 1e-6\n")
            f_mc.write(f"T_end (K) = {T_MF}\n")
            f_mc.write(f"div_T = {div_T}\n")
            f_mc.write("MCS = 100000\n")
            f_mc.write("thresh = 10000\n")


        msg = "Input_MC successfully written. You can modify it if needed before continuing to MC simulation by running with '--only-mc'."
        log(msg)
        sleep(3)
    else:
        msg = 'Existing input_MC detected, will try to run the MC based on this'
        log(msg)
        sleep(3)
        

    log("Completed Hamiltonian fitting. Now proceeding to Monte Carlo simulation...")        
    run_monte_carlo() # <---  The final step (MC)

        
    return


def read_mc_params(filename="input_MC"):
    params = {}
    with open(filename, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.split("=", 1)
                params[key.strip()] = value.strip()
    return params


def pad_and_convert_to_array(list_of_lists, fill_value=-5):
    """
    Given a list of lists, pad them to the same length with fill_value,
    then convert to a NumPy array.

    Returns: A 2D NumPy array of shape (num_sublists, max_length).
    """
    # If it's empty, return an empty array.
    if not list_of_lists:
        return np.array([])

    # Find the max length of any sublist
    max_len = max(len(sublist) for sublist in list_of_lists)

    # Pad each sublist
    padded = []
    for sublist in list_of_lists:
        # If it's shorter than max_len, pad it with fill_value
        needed = max_len - len(sublist)
        if needed > 0:
            sublist = sublist + [fill_value] * needed
        padded.append(sublist)

    return np.array(padded)


def generate_Ts(T_start: float,
                           T_end:   float,
                           n_pts:   int,
                           block:   int   = 20,
                           dT0:     float = 1.0,
                           factor:  float = 2.0,
                           skip:    bool  = False) -> np.ndarray:
    """
    Strict doubling grid:
        0,1,…,9,  12,14,…,30,  34,38,…   (if skip=True, factor=2, block=10)

    Rules
    -----
    1. First `block` points spaced by dT0.
    2. After every `block` points multiply ΔT by `factor`.
    3. If `skip` is True, jump forward an *extra* ΔT at each new block,
       *provided* the jump stays ≤ T_end.
    4. Stop when either
          • the list already has `n_pts` points, or
          • the next point would exceed `T_end`.

    Because of (4) the function may return **fewer than `n_pts`** points
    (never more), but every value respects the spacing rule and the sequence
    is strictly increasing and ≤ `T_end`.
    """
    assert n_pts >= 1, "n_pts must be positive"
    Ts = [T_start]
    dT = dT0
    points_in_block = 0

    while len(Ts) < n_pts:
        nxt = Ts[-1] + dT
        if nxt > T_end + 1e-12:
            break

        Ts.append(nxt)
        points_in_block += 1

        if points_in_block == block:
            points_in_block = 0
            if skip and (Ts[-1] + dT) <= T_end + 1e-12:
                Ts.append(Ts[-1] + dT)
            dT *= factor
        if len(Ts) >= n_pts:
            break
    return np.array(Ts[:n_pts], dtype=float)



###############################################################################
# Performs the MC simulation
###############################################################################

def run_monte_carlo():
    """
    Runs the Monte Carlo simulation that was previously inside `main()`,
    using all the Heisenberg+anisotropy parameters from the fitted Hamiltonian.

    Reads these parameters (and the supercell repetition, T-range, etc.)
    from 'input_MC', then performs the Metropolis MC. Finally plots E, M,
    Cv, Chi vs T and saves "heisenberg_mc_data.txt".
    """

    global struct_mag_stable, N1list, N2list, N3list, N4list, ds_stable, rep_DFT, root_path,encut,lvdw, dftu,no_magstruct
    global J1, J2, J3, J4
    global K1x, K1y, K1z, K2x, K2y, K2z, K3x, K3y, K3z, K4x, K4y, K4z
    global Ax, Ay, Az, EMA
    global threshold, mc_range, kB, GPU_accel, padding


#    if 'struct_mag_stable' not in globals():
#        log("Error: 'struct_mag_stable' is not defined. Please run the full workflow to generate the relaxed structure before running the Monte Carlo simulation.")
#        sys.exit(1)
#    if 'ds_stable' not in globals():
#        log("Error: 'ds_stable' is not defined. Please run the full workflow to generate neighbor mapping data before running the Monte Carlo simulation.")
#        sys.exit(1)
        

                    
    # ------------------------------------------------------------------------
    # (Reads J1, J2, Ax, etc. from lines of 'input_MC', plus Tstart, Trange, etc.)
    # ------------------------------------------------------------------------
    start_time_mc = time()
    if not os.path.exists(root_path+'/input_MC'):
        msg = 'no input_MC file detected; please provide it or run the full workflow first.'
        log(msg)
        sys.exit()
    else:
        with open('input_MC') as f:
            for line in f:
                row = line.split()
                if 'directory' in line:
                    path = root_path+'/'+row[-1]
                elif 'repeat' in line:
                    rep_z = int(row[-1])
                    rep_y = int(row[-2])
                    rep_x = int(row[-3])
                elif 'restart' in line:
                    restart = int(row[-1])
                elif 'J1' in line:
                    J1 = np.double(row[-1])
                elif 'J2' in line:
                    J2 = np.double(row[-1])
                elif 'J3' in line:
                    J3 = np.double(row[-1])
                elif 'J4' in line:
                    J4 = np.double(row[-1])
                elif 'K1x' in line:
                    K1x = np.double(row[-1])
                elif 'K1y' in line:
                    K1y = np.double(row[-1])
                elif 'K1z' in line:
                    K1z = np.double(row[-1])
                elif 'K2x' in line:
                    K2x = np.double(row[-1])
                elif 'K2y' in line:
                    K2y = np.double(row[-1])
                elif 'K2z' in line:
                    K2z = np.double(row[-1])
                elif 'K3x' in line:
                    K3x = np.double(row[-1])
                elif 'K3y' in line:
                    K3y = np.double(row[-1])
                elif 'K3z' in line:
                    K3z = np.double(row[-1])
                elif 'K4x' in line:
                    K4x = np.double(row[-1])
                elif 'K4y' in line:
                    K4y = np.double(row[-1])
                elif 'K4z' in line:
                    K4z = np.double(row[-1])
                elif 'Ax' in line:
                    Ax = np.double(row[-1])
                elif 'Ay' in line:
                    Ay = np.double(row[-1])
                elif 'Az' in line:
                    Az = np.double(row[-1])
                elif 'EMA' in line:
                    EMA = int(row[-1])
                elif 'T_start' in line:
                    Tstart = float(row[-1])
                elif 'T_end' in line:
                    Trange = float(row[-1])
                elif 'div_T' in line:
                    div_T = int(row[-1])
                elif 'mu' in line:
                    mu = float(row[-1])
                elif 'MCS' in line:
                    mc_range = int(row[-1])
                elif 'thresh' in line:
                    threshold = int(row[-1])

    if os.path.exists(path):
        new_name = path+'_'+str(time())
        os.rename(path, new_name)
        msg = 'found an old MC directory, renaming it to '+new_name
        log(msg)

    os.makedirs(path)
    os.chdir(path)

    try:
        #copyfile(new_name+'/N1list',path+'/N1list')
        #copyfile(new_name+'/N2list',path+'/N2list')
        #copyfile(new_name+'/N3list',path+'/N3list')
        #copyfile(new_name+'/N4list',path+'/N4list')
        safe_symlink(new_name + '/N1list', path + '/N1list')
        safe_symlink(new_name + '/N2list', path + '/N2list')
        safe_symlink(new_name + '/N3list', path + '/N3list')
        safe_symlink(new_name + '/N4list', path + '/N4list')
    except:
        pass

    repeat = [rep_x,rep_y,rep_z]
    S = mu/2
    os.chdir(path)

    struct_mag_stable.make_supercell(repeat)
    global N
    N = len(struct_mag_stable)
    spins_init = np.array(struct_mag_stable.site_properties['magmom'][:])/2.0

    if restart==0:
        dr_max = ds_stable[0]
        d_N1 = ds_stable[1]
        d_N2 = ds_stable[2]
        d_N3 = ds_stable[3]
        d_N4 = ds_stable[4]
        global all_coords
        all_coords = [0]*N
        for i in range(N):
            all_coords[i] = [struct_mag_stable[i].x, struct_mag_stable[i].y, struct_mag_stable[i].z]
        all_coords = np.array(all_coords,dtype='float32')
        all_coords = all_coords.flatten()
        global N1list,N2list,N3list,N4list
        N1list = [[1,2]]*N
        N2list = [[1,2]]*N
        N3list = [[1,2]]*N
        N4list = [[1,2]]*N

        if GPU_accel and cuda.is_available():
            #def nf(struct_mag, site, d_N, dr):
            #    return Nfinder_GPU(struct_mag, site, d_N, dr, all_coords)
            nf = lambda struct, site, d_N, dr, all_coords=all_coords: Nfinder_GPU(struct, site, d_N, dr, all_coords)
            msg = 'Nighbor mapping will use GPU acceleration'
        else:
            nf = Nfinder
            msg = 'GPU not available; neighbor mapping will run on CPU'
        log(msg)
          

        start_time_map = time()
        for i in range(N):
            N1list[i] = nf(struct_mag_stable,i,d_N1,dr_max)
            if J2!=0:
                N2list[i] = nf(struct_mag_stable,i,d_N2,dr_max)
            if J3!=0:
                N3list[i] = nf(struct_mag_stable,i,d_N3,dr_max)
            if J4!=0:
                N4list[i] = nf(struct_mag_stable,i,d_N4,dr_max)
            print(str(i)+' / '+str(N-1)+' mapped')

        if padding:
            log('Padding neighbor lists to handle inhomogeneous coordination.')
            make_homogenous(N1list)
            make_homogenous(N2list)
            make_homogenous(N3list)
            make_homogenous(N4list)

        end_time_map = time()
        time_map = np.around(end_time_map - start_time_map, 2)
        with open('N1list','wb') as fn1:
            dump(N1list, fn1)
        with open('N2list','wb') as fn2:
            dump(N2list, fn2)
        with open('N3list','wb') as fn3:
            dump(N3list, fn3)
        with open('N4list','wb') as fn4:
            dump(N4list, fn4)
        msg = 'Neighbor mapping finished and saved!'
        log(msg)
        msg = 'The neighbor mapping process for a '+str(N)+' site lattice took '+str(time_map)+' s'
        log(msg)
    else:
        with open('N1list','rb') as fN1:
            N1list = load(fN1)
        with open('N2list','rb') as fN2:
            N2list = load(fN2)
        with open('N3list','rb') as fN3:
            N3list = load(fN3)
        with open('N4list','rb') as fN4:
            N4list = load(fN4)
        N = len(N1list)
        msg = 'Neighbor mapping successfully read'
        log(msg)

    #N1list = np.array(N1list)
    #N2list = np.array(N2list)
    #N3list = np.array(N3list)
    #N4list = np.array(N4list)

    N1list = pad_and_convert_to_array(N1list, fill_value=-5)
    N2list = pad_and_convert_to_array(N2list, fill_value=-5)
    N3list = pad_and_convert_to_array(N3list, fill_value=-5)
    N4list = pad_and_convert_to_array(N4list, fill_value=-5)


    temp = N1list.flatten()
    corrupt = np.count_nonzero(temp==-5)
    msg = 'The amount of site corruption in N1s is ' + str(corrupt) + ' / ' + str(len(temp)) + ', or ' + str(100.0*corrupt/len(temp)) + '%'
    log(msg)
    if J2!=0:
        temp2 = N2list.flatten()
        corrupt2= np.count_nonzero(temp2==-5)
        msg= 'The amount of site corruption in N2s is ' + str(corrupt2) + ' / ' + str(len(temp2)) + ', or ' + str(100.0*corrupt2/len(temp2)) + '%'
        log(msg)
    if J3!=0:
        temp3 = N3list.flatten()
        corrupt3= np.count_nonzero(temp3==-5)
        msg= 'The amount of site corruption in N3s is ' + str(corrupt3) + ' / ' + str(len(temp3)) + ', or ' + str(100.0*corrupt3/len(temp3)) + '%'
        log(msg)
    if J4!=0:
        temp4 = N4list.flatten()
        corrupt4= np.count_nonzero(temp4==-5)
        msg= 'The amount of site corruption in N4s is ' + str(corrupt4) + ' / ' + str(len(temp4)) + ', or ' + str(100.0*corrupt4/len(temp4)) + '%'
        log(msg)

    Ts = generate_Ts(Tstart, Trange, div_T) #np.linspace(Tstart,Trange,div_T)
    
    #M_ups = []
    #X_ups = []
    #M_downs = []
    #X_downs = []
    M_tots = []
    X_tots = []
    energies_data = []
    E_errors_data= []
    Ms_data= []
    M_errors_data= []
    Cvs_data= []
    Cv_errors_data=[]
    Chis_data=[]
    Chi_errors_data=[]

    start_time_mc = time()
    msg = f"MC Simulation started on {datetime.datetime.now().strftime('%A, %d %B %Y, %H:%M:%S')}!"
    log(msg)


    # Determine the material name from the structure in final_list[0][1].
    material = semifinal_list[0][1].composition.reduced_formula
    out_filename = f"{material}_{int(np.floor(Tstart))}K-{int(np.floor(Trange))}K_M-X.dat"

    from mc_class import HybridMC, QuantumSpinED, QMC_func_SSE
    
    if mc_method == 2:
        mc_run = "Hybrid Metropolis (heat-bath + over-relaxation + cluster)"
    elif mc_method == 1:
        mc_run = "Optimized Metropolis (fast single-spin updates)"
    elif mc_method == 0:
        mc_run = "Reference Metropolis (simple, benchmark kernel)"
    elif mc_method == 3:
        mc_run = "Exact Diagonalization (QuantumSpinED)"
    elif mc_method == 4:
        mc_run = "Stochastic-Series Expansion QMC"
    else:
        raise ValueError("Invalid Monte Carlo method selected.")


    msg = f"Monte Carlo sampling will be performed using {mc_run}"
    log(msg)


    mc_obj = HybridMC(
        N,
        N1list, N2list, N3list, N4list,
        J1, J2, J3, J4,
        K1x, K1y, K1z,
        K2x, K2y, K2z,
        K3x, K3y, K3z,
        K4x, K4y, K4z,
        Ax, Ay, Az,
        kB,
        mc_range,
        threshold,
        EMA
    )     
    
    specQ = None
    
    
    if mc_method == 3:           # ---- Exact Diagonalisation ----
        if N > 18:
            raise ValueError(
                f"Exact diagonalisation limited to N ≤ 18, got N = {N}. "
                "Choose mc_method = 4 (SSE QMC) for larger systems."
            )
        specQ = QuantumSpinED(
            spins_init,
            N1list, N2list, N3list, N4list,
            J1, J2, J3, J4,
            Delta = 1.0,   # XXZ anisotropy
            h     = 0.0    # external field (eV)
        )

            
                                          
    prev_M_up_val = None
    
    if not os.path.exists(out_filename):
        with open(out_filename, 'w') as f:
            f.write("# T(K)    M_up      X_up      M_down    X_down    "
                    "M_tot     X_tot    Cv_tot    E    M_err      Chi_err     "
                    "E_err     Cv_err\n")
            f.write("# Note Units: Energy = eV/site; Magnetization = per site; "
                    "Cv = 1/k_B; Chi = 1/eV; Temperature = K \n")



    if dump_spins and mc_method in (0, 1, 2):          
        spins_filename = (f"{material}_"
                          f"{int(np.floor(Tstart))}K-"
                          f"{int(np.floor(Trange))}K_spinsdump.dat")
        with open(spins_filename, 'w') as f:
            f.write(f"# Spin dump for {material}\n\n")
                                   
    # -----------------------------------------------------------------
    #  TEMPERATURE LOOP  – classical MC, ED, or SSE QMC
    # -----------------------------------------------------------------
    for iT, T_cur in enumerate(Ts):

        # ------------ (A) choose Monte-Carlo kernel -------------------
        if   mc_method == 2:        # hybrid BOC
            results = mc_obj.MC_func_hybrid_boc(
                        spins_init, T_cur,
                        (J2 != 0), (J3 != 0), (J4 != 0))

        elif mc_method == 1:        # optimised Metropolis
            results = mc_obj.MC_func_simple_metropolis(
                        spins_init, T_cur,
                        (J2 != 0), (J3 != 0), (J4 != 0))

        elif mc_method == 0:        # reference Metropolis
            results = mc_obj.MC_func_metropolis(
                        spins_init, T_cur,
                        (J2 != 0), (J3 != 0), (J4 != 0))

        elif mc_method == 3:        # exact diagonalisation (small N)
            results = specQ.QMC_func_exact(T = T_cur)

        elif mc_method == 4:        # stochastic–series expansion (large N)
            results = QMC_func_SSE(
                        spins_init = spins_init,
                        T          = T_cur,          # Kelvin
                        N1list = N1list, N2list = N2list,
                        N3list = N3list, N4list = N4list,
                        J1 = J1, J2 = J2, J3 = J3, J4 = J4,
                        sweeps = 50_000,
                        therm  = 10_000,
                        Delta  = 1.0)                # XXZ anisotropy
                        #h      = 0.0)                # field (eV)

        else:
            raise ValueError("Invalid Monte-Carlo method selected.")

        # ------------ (B) unpack 14-tuple --------------------------------
        (M_up_val,  X_up_val,
        M_down_val, X_down_val,
        M_tot_val, X_tot_val,
        E_val,     Cv_val,
        Chi_err,   E_err, M_err, Cv_err,
        spins_x,   spins_y, spins_z) = results


        # ------------ (C) output & optional spin dump -------------------
        line = (f"{T_cur:8.1f}  {M_up_val:8.5f}  {X_up_val:8.5f}  "
                f"{M_down_val:8.5f}  {X_down_val:8.5f}  "
                f"{M_tot_val:8.5f}  {X_tot_val:8.5f}  "
                f"{Cv_val:8.5f}  {E_val:10.6f}  "
                f"{M_err:8.5f}  {Chi_err:8.5f}  {E_err:8.5f}  {Cv_err:8.5f}\n")


        print(line)
        
        with open(out_filename, 'a') as f:
            f.write(line)

        if dump_spins and mc_method in (0, 1, 2):     
            with open(spins_filename, 'a') as f:
                f.write(f"T = {T_cur:.2f} K\n\n")
                f.write("Sx = \n")
                f.write(str(spins_x.tolist()) + "\n\n")
                f.write("Sy = \n")
                f.write(str(spins_y.tolist()) + "\n\n")
                f.write("Sz = \n")
                f.write(str(spins_z.tolist()) + "\n\n")
                f.write("-" * 100 + "\n\n")      
            log(f"Spin data saved to '{spins_filename}'")
            
                    
        M_tots.append(M_tot_val)
        X_tots.append(X_tot_val)
        energies_data.append(E_val)
        E_errors_data.append(E_err)
        M_errors_data.append(M_err)
        Cvs_data.append(Cv_val)
        Cv_errors_data.append(Cv_err)
        Chi_errors_data.append(Chi_err)

        
        #spins_init = spins_x.copy() #np.copy(spins_x)  # keep final state for next                  

    
    
        if M_up_val < 1.0e-3:
            log(f"Detected Magnetization < 1e-3 at T={T_cur:.3f}K. "
                "Exiting loop and finalizing.")
            break



        if prev_M_up_val is not None:
            if round(M_up_val, 4) == round(prev_M_up_val, 4):
                log(f"No significant change in M_up_val at T={T_cur:.3f}K "
                    f"({M_up_val:.6f} ≈ {prev_M_up_val:.6f}). "
                    "Exiting loop and finalizing.")
                break

        # Update previous value
        prev_M_up_val = M_up_val
                        

    log(f"Computed spin and thermodynamic parameters for {material} saved to '{out_filename}'")    
                
    # Save final data to "heisenberg_mc_data.txt" #Additional data. See if it is necessary
#    filename = f"{material}_Heisenberg_mc.txt"
#    with open(filename,'w') as fdata:
#        fdata.write("# T(K)  E  E_err  M  M_err  Cv  Cv_err  Chi  Chi_err\n")
#        for iT, T_cur in enumerate(Ts):
#            fdata.write(
#                f"{T_cur} {energies_data[iT]} {E_errors_data[iT]} "
#                f"{Ms_data[iT]} {M_errors_data[iT]} "
#                f"{Cvs_data[iT]} {Cv_errors_data[iT]} "
#                f"{Chis_data[iT]} {Chi_errors_data[iT]}\n"
#            )

    
    
#    msg = ("Units: Energy = eV/site; Magnetization = per site; Cv = eV/(K·site); "
#       "Chi = 1/eV; Temperature = K.")
    
#    log(msg)
   
    if dump_spins:
        plot_spin_dump(spins_filename, material)
    
    # Finally produce the plot(s):
    plot_results(
        T_list=Ts[: iT+1],
        E_list=energies_data,
        E_err_list=E_errors_data,
        M_list=M_tots,
        M_err_list=M_errors_data,
        Cv_list=Cvs_data,
        Cv_err_list=Cv_errors_data,
        Chi_list=X_tots,
        Chi_err_list=Chi_errors_data,
        matName = material,
        plot_errors=True
    )

    os.chdir(root_path)


    end_time_mc = time()
    time_mc = np.around(end_time_mc - start_time_mc, 2)
    msg = "MC simulation finished. Analyze the output to determine Curie/Neel T."
    log(msg)
    msg = 'The MC simulation took '+str(time_mc)+' s'
    log(msg)

    
    return


def parse_spin_axes(spin_axes_str):
    """
    Parse a semicolon-separated string of spin directions.
    For example, "100;001;111" returns [(1,0,0), (0,0,1), (1,1,1)].
    Negative digits are also allowed.
    """
    axes = spin_axes_str.split(";")
    axes_tuples = []
    for axis in axes:
        axis = axis.strip()
        if not axis:
            continue
        components = tuple(int(ch) for ch in axis)
        axes_tuples.append(components)
    return axes_tuples



def generate_default_input():
    """Generates a default input file for Curie2D calculations."""
    default_lines = [
        "# Default input parameters for Curie2D",
        "system_dimension = 2D",
        "structure_file = POSCAR",
        "XC_functional = PBE",
        "vacuum = 25",
        "DFT_supercell_size = 2 2 1",
        "strain = 0.01 0.01 0",  # Empty strain list; you could also list values if desired
        "mag_prec = 0.1",
        "enum_prec = 1E-7",
        "max_neighbors = 4",
        "randomise_VASP_command = False",
        "mag_from = OSZICAR",
        "relax_structures = True",
        "GPU_accel = False",
        "more_than_2_metal_layers = False",  # padding equivalent
        "dump_spins = False",
        "ENCUT = 520",
        "IBRION = 2",
        "POTIM = 0.1",
        "NSIM = 4",
        "KPAR = 1",
        "NPAR = 1",
        "NCORE = 1",
        "ISMEAR = -5",
        "SIGMA = 0.05",
        "ISIF = 4",
        "LVDW = False",
        "mc_method = 1",
        "dftu = True",
        "no_magstruct = 4",
        "LPLANE = True",
        "PSTRESS = 0.001",
        "same_neighbor_thresh = 0.05",
        "same_neighbor_thresh_buffer = 0.01",
        "accuracy = high",
        "LDAUJ = {}",
        "LDAUU = {}",
        "LDAUL = {}",
        "LDAUTYPE = 2",
        "LDAUPRINT = 1",
        "log_filename = log",
        "kpoints_density_relax = 15",
        "kpoints_density_static = 30",
        "potential_directory = {}",
        "POTCAR = Ba Ba_sv_GW  Ni Ni_sv_GW Cl Cl_GW",
        "spin_axes = 100;010;001"
        
                    
    ]
    with open("input", "w") as f:
        f.write("\n".join(default_lines))
    print("Default input file 'input' generated successfully.\n Modify and remove some parameters as needed")

def remove_potential_symlink(symlink_path):
    import os
    if os.path.lexists(symlink_path):
        os.remove(symlink_path)
        log(f"Removed symbolic link {symlink_path} after run.")
        
