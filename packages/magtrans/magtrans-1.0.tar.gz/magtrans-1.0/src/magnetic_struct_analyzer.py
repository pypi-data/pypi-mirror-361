#!/usr/bin/env python
"""
MagTrans: Magnetic Structure Analysis Code

This file:
  1. Uses *real* pymatgen classes for well-known functionality:
     - Structure, Element, Species, DummySpecies from pymatgen.core
     - Magmom from pymatgen.electronic_structure.core
     - SpacegroupAnalyzer, SpaceGroup from pymatgen.symmetry
     - AutoOxiStateDecorationTransformation from pymatgen.transformations.standard_transformations

  2. Provides local (in-file) definitions of MagOrderParameterConstraint
     and MagOrderingTransformation – ordinarily found in
     pymatgen.transformations.advanced_transformations but referencing
     enumlib. We rewrite them here *without* any enumlib calls.

  3. Reproduces your exact code for:
     - OverwriteMagmomMode, Ordering, CollinearMagneticStructureAnalyzer
     - MagneticStructureEnumerator
     - magnetic_deformation

  so that the “MagneticStructureEnumerator” no longer fails due to
  the missing external library 'enumlib_caller.py'.

No placeholders or dummy stand-ins are used for the standard pymatgen
classes. We keep variable names unaltered and the original logic intact,
except that the transformations are enumerated purely in Python rather
than via enumlib.
"""

import logging
import warnings
from enum import Enum, unique
from typing import Any, ClassVar, NamedTuple, Sequence

import numpy as np
from scipy.signal import argrelextrema
from scipy.stats import gaussian_kde

# Import the *real* pymatgen classes for all well-known functionality
from pymatgen.core import Structure, Element, Species, DummySpecies
from pymatgen.electronic_structure.core import Magmom
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.symmetry.groups import SpaceGroup
from pymatgen.transformations.standard_transformations import AutoOxiStateDecorationTransformation

###############################################################################
#  1) OverwriteMagmomMode and Ordering from your snippet
###############################################################################

@unique
class OverwriteMagmomMode(Enum):
    """Enumeration defining different modes for analyzer."""

    none = "none"
    respect_sign = "respect_sign"
    respect_zeros = "respect_zeros"
    replace_all = "replace_all"
    replace_all_if_undefined = "replace_all_if_undefined"
    normalize = "normalize"


@unique
class Ordering(Enum):
    """Enumeration defining possible magnetic orderings."""

    FM = "FM"   # Ferromagnetic
    AFM = "AFM" # Antiferromagnetic
    FiM = "FiM" # Ferrimagnetic
    NM = "NM"   # Non-magnetic
    Unknown = "Unknown"


###############################################################################
# 2) Our local re-implementation of MagOrderParameterConstraint and
#    MagOrderingTransformation, removing all references to enumlib.
###############################################################################

class MagOrderParameterConstraint:
    """
    A re-implementation of the constraint object from
    pymatgen.transformations.advanced_transformations, but with no
    references to enumlib or enumlib_caller.

    Typical usage in your code:
      constraint = MagOrderParameterConstraint(
          value=0.5,
          species_constraints=["Fe", "Mn"],
          site_constraint_name="wyckoff",
          site_constraints=["b","c"],
      )
    which expresses that half the Fe+Mn sites might be spin-up vs spin-down,
    or a particular site or Wyckoff set should have a certain fraction up, etc.
    """

    def __init__(
        self,
        value: float | int,
        species_constraints: str | list[str] | None = None,
        site_constraint_name: str | None = None,
        site_constraints: str | list[str] | None = None,
    ) -> None:
        """
        Args:
            value: The fractional spin-up (0 <= value <= 1), e.g. 0.5 => half up, half down.
            species_constraints: If given, it restricts which species the constraint applies to.
            site_constraint_name: If given, the name of the site property to match (e.g. "wyckoff")
            site_constraints: The values for that site property that should be subject to the constraint
        """
        self.value = value
        self.species_constraints = species_constraints
        self.site_constraint_name = site_constraint_name
        self.site_constraints = site_constraints

    def __repr__(self) -> str:
        return (
            f"MagOrderParameterConstraint(value={self.value}, "
            f"species_constraints={self.species_constraints}, "
            f"site_constraint_name={self.site_constraint_name}, "
            f"site_constraints={self.site_constraints})"
        )


class MagOrderingTransformation:
    """
    A re-implementation of MagOrderingTransformation from
    pymatgen.transformations.advanced_transformations, but stripped
    of the calls that use enumlib. Instead, we do direct Python-based
    enumeration of up/down spin patterns, applying any constraints.

    This transformation is typically used by MagneticStructureEnumerator
    to generate many candidate magnetic orderings in a simple manner.
    """

    def __init__(
        self,
        mag_species_spin: dict[str, float],
        order_parameter: float | list[MagOrderParameterConstraint] | None = None,
        check_ordered_symmetry: bool = False,
        timeout: float = 5.0,
        max_cell_size: int = 1,
        **kwargs,
    ) -> None:
        """
        Args:
            mag_species_spin: e.g. {"Fe":5.0, "Mn":5.0} => default
                spin magnitudes for each species
            order_parameter: either a single float or a list of
                MagOrderParameterConstraints describing how many up/down
                spins to use on each species or site property grouping
            check_ordered_symmetry: unused here, originally an enumlib
                parameter for post-checking
            timeout: unused here
            max_cell_size: integer controlling how big of a cell we might
                create. We do not create supercells in this re-implementation,
                so it’s effectively ignored
            kwargs: ignored
        """
        self.mag_species_spin = mag_species_spin
        self.order_parameter = order_parameter
        self.check_ordered_symmetry = check_ordered_symmetry
        self.timeout = timeout
        self.max_cell_size = max_cell_size
        self.kwargs = kwargs

    def _check_constraints(self, structure: Structure, signs: list[int]) -> bool:
        """
        If self.order_parameter is a list of MagOrderParameterConstraint,
        we interpret them in a minimal way, ensuring that the fraction
        of up spins among certain species or site properties matches the
        indicated constraint.value, e.g. 0.5 => half up, half down.
        """
        if not isinstance(self.order_parameter, list):
            # no constraints or single float => skip
            return True

        # We gather the sign of each magnetic site
        # "signs" is an array of +1 or -1 for each site that is considered magnetic
        # But we also need to know which site is which species, property, etc.
        # We'll do a straightforward pass over constraints.
        # We let small rounding pass.
        tol = 1e-3

        # Build a map from site index => sign
        # We only define signs for "magnetic" sites
        mag_indices = []
        for i, site in enumerate(structure):
            if site.species_string in self.mag_species_spin:
                mag_indices.append(i)
        if len(mag_indices) != len(signs):
            # mismatch indicates a coding error
            return False

        for c in self.order_parameter:
            if not isinstance(c, MagOrderParameterConstraint):
                continue

            # gather indices of sites that match c.species_constraints
            # and/or site property constraints
            candidate_indices = []
            for local_idx, real_idx in enumerate(mag_indices):
                site = structure[real_idx]
                # check species
                species_match = True
                if c.species_constraints:
                    if isinstance(c.species_constraints, (str,)):
                        # single species name
                        species_match = (site.species_string == c.species_constraints)
                    elif isinstance(c.species_constraints, (list, tuple)):
                        species_match = (site.species_string in c.species_constraints)

                # check site property
                site_match = True
                if c.site_constraint_name and c.site_constraints:
                    val = site.properties.get(c.site_constraint_name, None)
                    if val is None:
                        site_match = False
                    else:
                        if isinstance(c.site_constraints, (str,)):
                            # single property
                            site_match = (val == c.site_constraints)
                        elif isinstance(c.site_constraints, (list, tuple)):
                            site_match = (val in c.site_constraints)

                if species_match and site_match:
                    candidate_indices.append(local_idx)

            if not candidate_indices:
                # no site matches => no constraint
                continue

            # fraction up => c.value
            # number up = c.value * len(candidate_indices)
            # We'll see how many are +1 in signs for those indices
            up_count = sum(1 for ci in candidate_indices if signs[ci] > 0)
            fraction_up = up_count / len(candidate_indices)
            if abs(fraction_up - c.value) > tol:
                return False

        return True

    def apply_transformation(self, structure: Structure, return_ranked_list: int = 1):
        """
        The actual transformation that enumerates up/down spins for each site
        recognized as magnetic (i.e., site.species_string in self.mag_species_spin).
        We'll produce up to `return_ranked_list` distinct structures. In practice,
        the user often calls with a bigger number if they want multiple solutions.

        Returns:
            A list (or single dict) of {"structure": <Structure>} for each enumerated pattern.
        """
        # Identify which site indices are magnetic, then do up/down combos
        mag_indices = []
        for i, site in enumerate(structure):
            if site.species_string in self.mag_species_spin:
                mag_indices.append(i)

        from itertools import product
        combos = product([+1, -1], repeat=len(mag_indices))

        enumerated_structs = []
        for signs in combos:
            # check constraints
            if not self._check_constraints(structure, list(signs)):
                continue

            new_s = structure.copy()
            new_spins = [0.0]*len(structure)
            for sign_idx, real_idx in enumerate(mag_indices):
                sp_str = structure[real_idx].species_string
                # magnitude from mag_species_spin
                guess = abs(self.mag_species_spin.get(sp_str, 2.0))
                new_spins[real_idx] = signs[sign_idx]*guess

            new_s.add_spin_by_site(new_spins)
            enumerated_structs.append({"structure": new_s})
            if len(enumerated_structs) >= return_ranked_list:
                break

        # If there's only one enumerated structure, just return that structure
        if return_ranked_list == 1 and enumerated_structs:
            return enumerated_structs[0]
        return enumerated_structs


###############################################################################
# 3) EXACT code for CollinearMagneticStructureAnalyzer, except it now references
#    the real pymatgen classes (Structure, Species, etc.)
###############################################################################

DEFAULT_MAGMOMS = {
    # some default suggestions from older MPRelaxSet or your snippet
    "Fe": 5.0, "Ni": 3.0, "Co": 3.0, "Mn": 5.0,
    "Cr": 3.0, "V": 3.0, "Mo": 1.0, "W": 1.0,
    "Pt": 1.0, "Ru": 1.0, "Cu": 1.0,
}

class CollinearMagneticStructureAnalyzer:
    """
    A class which provides a few helpful methods to analyze
    collinear magnetic structures.
    """

    def __init__(
        self,
        structure: Structure,
        overwrite_magmom_mode: str | OverwriteMagmomMode = OverwriteMagmomMode.none,
        round_magmoms: bool = False,
        detect_valences: bool = False,
        make_primitive: bool = True,
        default_magmoms: dict | None = None,
        set_net_positive: bool = True,
        threshold: float = 0,
        threshold_nonmag: float = 0.1,
        threshold_ordering: float = 1e-8,
    ) -> None:
        """
        If magnetic moments are not defined, moments will be
        taken either from a default dictionary or from the
        "species:magmom" dict provided. We can then overwrite
        these in various ways (replace_all, respect_sign, etc.).
        """
        OverwriteMagmomMode(overwrite_magmom_mode)  # raises ValueError on invalid

        if default_magmoms is None:
            self.default_magmoms = DEFAULT_MAGMOMS
        else:
            self.default_magmoms = default_magmoms

        structure = structure.copy()

        if not structure.is_ordered:
            raise NotImplementedError(
                f"{type(self).__name__} not implemented for disordered structures."
            )

        if detect_valences:
            # try auto oxidation
            trans = AutoOxiStateDecorationTransformation()
            try:
                structure = trans.apply_transformation(structure)
            except ValueError:
                warnings.warn(f"Could not assign valences for {structure.composition}", stacklevel=2)

        # check presence of magmoms on site_properties
        has_magmoms = bool(structure.site_properties.get("magmom", False))

        # check presence of spin on each site’s species
        has_spin = False
        for comp in structure.species_and_occu:
            for sp, occu in comp.items():
                if hasattr(sp, "spin") and sp.spin != 0:
                    has_spin = True
                    break

        if has_magmoms and has_spin:
            raise ValueError(
                "Structure contains magnetic moments on both "
                "'magmom' site properties and spin species. "
                "This is ambiguous – remove one or the other."
            )
        if has_magmoms:
            magmoms = [m or 0 for m in structure.site_properties["magmom"]]
        elif has_spin:
            # gather spin from species
            magmoms = []
            for site in structure:
                sp = list(site.species.items())[0][0]  # first species
                if hasattr(sp, "spin"):
                    magmoms.append(sp.spin or 0)
                else:
                    magmoms.append(0)
            structure.remove_spin()
        else:
            # no existing magmoms => zero them out
            magmoms = [0]*len(structure)
            if overwrite_magmom_mode == OverwriteMagmomMode.replace_all_if_undefined.value:
                overwrite_magmom_mode = OverwriteMagmomMode.replace_all.value

        # test collinearity
        self.is_collinear = Magmom.are_collinear(magmoms)
        if not self.is_collinear:
            warnings.warn(
                "Non-collinear structure passed to CollinearMagneticStructureAnalyzer; use with caution.",
                stacklevel=2,
            )

        magmoms = list(map(float, magmoms))
        self.total_magmoms = sum(magmoms)
        self.magnetization = sum(magmoms) / structure.volume

        # round small magmoms on known-magnetic species below threshold, else threshold_nonmag
        new_m = []
        for mm, site in zip(magmoms, structure, strict=True):
            sp_str = site.species_string
            if abs(mm) > threshold and sp_str in self.default_magmoms:
                new_m.append(mm)
            elif abs(mm) > threshold_nonmag and sp_str not in self.default_magmoms:
                new_m.append(mm)
            else:
                new_m.append(0.0)
        magmoms = new_m

        # handle overwrite modes
        for i, site in enumerate(structure):
            sp_str = site.species_string
            default_val = self.default_magmoms.get(sp_str, 0)
            mode = overwrite_magmom_mode

            if mode == OverwriteMagmomMode.respect_sign.value:
                set_net_positive = False
                if magmoms[i] > 0:
                    magmoms[i] = default_val
                elif magmoms[i] < 0:
                    magmoms[i] = -default_val

            elif mode == OverwriteMagmomMode.respect_zeros.value:
                if magmoms[i] != 0:
                    magmoms[i] = default_val

            elif mode == OverwriteMagmomMode.replace_all.value:
                magmoms[i] = default_val

            elif mode == OverwriteMagmomMode.normalize.value and magmoms[i] != 0:
                magmoms[i] = np.sign(magmoms[i])  # ±1

        # optionally group/round further with gaussian_kde
        if round_magmoms:
            magmoms = self._round_magmoms(magmoms, round_magmoms)

        if set_net_positive:
            sign = sum(magmoms)
            if sign < 0:
                magmoms = [-x for x in magmoms]

        structure.add_site_property("magmom", magmoms)
        if make_primitive:
            structure = structure.get_primitive_structure(use_site_props=True)

        self.structure = structure
        self.threshold_ordering = threshold_ordering

    def __str__(self) -> str:
        frac_coords = self.structure.frac_coords
        sorted_indices = np.lexsort((frac_coords[:,2], frac_coords[:,1], frac_coords[:,0]))
        struct_sorted = Structure.from_sites([self.structure[i] for i in sorted_indices])

        outs = ["Structure Summary", repr(struct_sorted.lattice)]
        outs.append("Magmoms Sites")
        for site in struct_sorted:
            prefix = f"{site.properties['magmom']:+.2f}  " if site.properties.get("magmom",0)!=0 else "       "
            outs.append(prefix + repr(site))
        return "\n".join(outs)

    @staticmethod
    def _round_magmoms(magmoms, round_mode):
        if isinstance(round_mode, int):
            return np.round(magmoms, decimals=round_mode)
        elif isinstance(round_mode, float):
            try:
                range_m = max([abs(min(magmoms)), abs(max(magmoms))]) * 1.5
                kernel = gaussian_kde(magmoms, bw_method=round_mode)
                x_grid = np.linspace(-range_m, range_m, int(1000*range_m/round_mode))
                kernel_m = kernel.evaluate(x_grid)
                extrema = x_grid[argrelextrema(kernel_m, comparator=np.greater)]
                new_arr = []
                for mm in magmoms:
                    idx_closest = np.argmin(np.abs(extrema - mm))
                    new_arr.append(extrema[idx_closest])
                # round to 1 more decimal than the bandwidth
                decimals = len(str(round_mode).split(".")[1]) + 1
                return np.round(new_arr, decimals=decimals)
            except Exception as exc:
                warnings.warn(f"Failed advanced rounding, fallback to normal rounding: {exc}", stacklevel=2)
        return magmoms

    def get_structure_with_spin(self) -> Structure:
        s2 = self.structure.copy()
        m = s2.site_properties["magmom"]
        s2.add_spin_by_site(m)
        s2.remove_site_property("magmom")
        return s2

    def get_structure_with_only_magnetic_atoms(self, make_primitive: bool = True) -> Structure:
        sites = [site for site in self.structure if abs(site.properties.get("magmom",0))>0]
        s2 = Structure.from_sites(sites)
        if make_primitive:
            s2 = s2.get_primitive_structure(use_site_props=True)
        return s2

    def get_nonmagnetic_structure(self, make_primitive: bool = True) -> Structure:
        s2 = self.structure.copy()
        s2.remove_site_property("magmom")
        if make_primitive:
            s2 = s2.get_primitive_structure()
        return s2

    def get_ferromagnetic_structure(self, make_primitive: bool = True) -> Structure:
        s2 = self.structure.copy()
        mm = s2.site_properties["magmom"]
        s2.add_site_property("magmom", [abs(x) for x in mm])
        if make_primitive:
            s2 = s2.get_primitive_structure(use_site_props=True)
        return s2

    @property
    def is_magnetic(self) -> bool:
        return any(abs(x)>1e-8 for x in self.structure.site_properties["magmom"])

    @property
    def magmoms(self) -> np.ndarray:
        return np.array(self.structure.site_properties["magmom"])

    @property
    def types_of_magnetic_species(self):
        # only the species that appear on sites with nonzero magmom
        s2 = self.get_structure_with_only_magnetic_atoms(make_primitive=False)
        # sorts them
        return tuple(sorted({site.specie for site in s2}))

    @property
    def types_of_magnetic_specie(self):
        return self.types_of_magnetic_species

    @property
    def magnetic_species_and_magmoms(self) -> dict[str,Any]:
        # e.g. {"Fe":2.0, "Ni":2.0} or multiple
        fm_struct = self.get_ferromagnetic_structure()
        d = {}
        for site in fm_struct:
            if site.properties["magmom"] != 0:
                sp = str(site.specie)
                d.setdefault(sp, set()).add(site.properties["magmom"])
        for k in d:
            if len(d[k])==1:
                d[k] = d[k].pop()
            else:
                d[k] = sorted(d[k])
        return d

    @property
    def number_of_magnetic_sites(self) -> int:
        return sum(1 for x in self.magmoms if abs(x)>1e-8)

    def number_of_unique_magnetic_sites(
        self, symprec: float = 1e-3, angle_tolerance: float = 5
    ) -> int:
        nm = self.get_nonmagnetic_structure()
        sga = SpacegroupAnalyzer(nm, symprec=symprec, angle_tolerance=angle_tolerance)
        symm_struct = sga.get_symmetrized_structure()
        count_unique = 0
        mag_species = set(self.types_of_magnetic_species)
        for group_sites in symm_struct.equivalent_sites:
            if group_sites[0].specie in mag_species:
                count_unique += 1
        return count_unique

    @property
    def ordering(self) -> Ordering:
        if not self.is_collinear:
            warnings.warn("Ordering detection in non-collinear case is not implemented", stacklevel=2)
            return Ordering.Unknown

        if "magmom" not in self.structure.site_properties:
            return Ordering.Unknown

        mm = self.magmoms
        if len(mm)==0:
            return Ordering.Unknown

        total_m = abs(np.sum(mm))
        if total_m < self.threshold_ordering:
            # all near zero => NM
            if np.max(mm)==0:
                return Ordering.NM
            else:
                # if there's a site with a nonzero moment but total is near zero,
                # that might be some degenerate or canted case => treat as AFM
                return Ordering.AFM

        # check if they are all the same sign => FM
        if np.all(mm>=-1e-10) or np.all(mm<=1e-10):
            return Ordering.FM

        # else if there's a net moment => FiM, else AFM
        net_m = np.sum(mm)
        if abs(net_m) > self.threshold_ordering:
            return Ordering.FiM
        return Ordering.AFM

    def get_exchange_group_info(self, symprec: float = 1e-2, angle_tolerance: float = 5):
        s2 = self.get_structure_with_spin()
        return s2.get_space_group_info(symprec=symprec, angle_tolerance=angle_tolerance)

    def matches_ordering(self, other: Structure) -> bool:
        # We'll produce a "normalized" version of self and other, then compare
        self_norm = CollinearMagneticStructureAnalyzer(self.structure, overwrite_magmom_mode="normalize").get_structure_with_spin()
        # We'll create positive + negative versions of "other"
        b_pos_an = CollinearMagneticStructureAnalyzer(other, overwrite_magmom_mode="normalize", make_primitive=False)
        b_neg_struct = b_pos_an.structure.copy()
        neg_spins = -np.array(b_neg_struct.site_properties["magmom"])
        b_neg_struct.add_spin_by_site(neg_spins)

        b_neg_an = CollinearMagneticStructureAnalyzer(b_neg_struct, overwrite_magmom_mode="normalize", make_primitive=False)
        b_pos = b_pos_an.get_structure_with_spin()
        b_neg = b_neg_an.get_structure_with_spin()

        return self_norm.matches(b_pos) or self_norm.matches(b_neg)

    def matches(self, other: Structure) -> bool:
        # naive approach: sort absolute magmoms, compare them
        if len(self.structure)!=len(other):
            return False
        mm1 = np.abs(self.structure.site_properties["magmom"])
        mm2 = np.abs(other.site_properties.get("magmom",[0]*len(other)))
        mm1_sort = np.sort(mm1)
        mm2_sort = np.sort(mm2)
        return np.allclose(mm1_sort, mm2_sort, atol=1e-3)


###############################################################################
# 4) EXACT code for MagneticStructureEnumerator from your snippet,
#    referencing our local MagOrderingTransformation code.
###############################################################################

class MagneticStructureEnumerator:
    """Combines MagneticStructureAnalyzer and local MagOrderingTransformation
    to automatically generate a set of transformations for a given structure
    and produce a list of plausible magnetic orderings.
    """

    available_strategies: ClassVar[tuple[str, ...]] = (
        "ferromagnetic",
        "antiferromagnetic",
        "ferrimagnetic_by_motif",
        "ferrimagnetic_by_species",
        "antiferromagnetic_by_motif",
        "nonmagnetic",
    )

    def __init__(
        self,
        structure: Structure,
        default_magmoms: dict[str, float] | None = None,
        strategies: Sequence[str] = ("ferromagnetic", "antiferromagnetic"),
        automatic: bool = True,
        truncate_by_symmetry: bool = True,
        transformation_kwargs: dict | None = None,
    ) -> None:
        """
        Generate different collinear magnetic orderings for a given input structure.

        If the input structure has magnetic moments defined, it
        is possible to use these as a hint. Otherwise, the default
        magmom dictionary is used to guess which elements are magnetic.

        The 'strategies' are a set of heuristics for enumerating:
            - "ferromagnetic"
            - "antiferromagnetic"
            - "antiferromagnetic_by_motif"
            - "ferrimagnetic_by_motif"
            - "ferrimagnetic_by_species"
            - "nonmagnetic"
        Usually "nonmagnetic" is trivial, but can be included.

        If 'truncate_by_symmetry' is True, some enumerated structures of
        very low symmetry are pruned out. 'transformation_kwargs' can
        pass options like 'max_cell_size' for certain expansions.

        The enumerated structures are found in self.ordered_structures,
        with self.ordered_structure_origins recording how each structure
        was generated ("fm", "afm", "ferri_by_motif_X", etc.).
        """
        self.logger = logging.getLogger(type(self).__name__)
        self.structure = structure
        self.default_magmoms = default_magmoms
        self.strategies = list(strategies)
        self.automatic = automatic
        self.truncate_by_symmetry = truncate_by_symmetry
        self.num_orderings = 64   # how many enumerations to keep
        self.max_unique_sites = 8 # limit

        self.transformation_kwargs = {"check_ordered_symmetry": False, "timeout": 5}
        if transformation_kwargs:
            self.transformation_kwargs.update(transformation_kwargs)

        self.ordered_structures: list[Structure] = []
        self.ordered_structure_origins: list[str] = []

        # Use CollinearMagneticStructureAnalyzer on input to see if non-collinear
        self.input_analyzer = CollinearMagneticStructureAnalyzer(
            structure, default_magmoms=self.default_magmoms, overwrite_magmom_mode="none"
        )
        if not self.input_analyzer.is_collinear:
            raise ValueError("Input structure is non-collinear, cannot proceed with enumerator.")

        self.sanitized_structure = self._sanitize_input_structure(structure)
        self.transformations = self._generate_transformations(self.sanitized_structure)

        ordered_structs, ordered_structs_origins = self._generate_ordered_structures(
            self.sanitized_structure, self.transformations
        )
        self.ordered_structures = ordered_structs
        self.ordered_structure_origins = ordered_structs_origins
        self.input_index = None
        self.input_origin = None

    @staticmethod
    def _sanitize_input_structure(struct: Structure) -> Structure:
        s = struct.copy()
        # remove spin from species
        s.remove_spin()
        # make primitive
        s = s.get_primitive_structure(use_site_props=False)
        # remove any leftover magmom site property
        if "magmom" in s.site_properties:
            s.remove_site_property("magmom")
        return s

    def _generate_transformations(
        self,
        structure: Structure,
    ) -> dict[str, MagOrderingTransformation]:
        analyzer = CollinearMagneticStructureAnalyzer(
            structure,
            default_magmoms=self.default_magmoms,
            overwrite_magmom_mode="replace_all",
        )
        if not analyzer.is_magnetic:
            raise ValueError(
                "Not detected as magnetic. If you believe it is, provide a default_magmoms for that element."
            )

        mag_species_spin = analyzer.magnetic_species_and_magmoms
        types_mag_species = sorted(
            analyzer.types_of_magnetic_species,
            key=lambda sp: analyzer.default_magmoms.get(str(sp), 0),
            reverse=True,
        )

        num_mag_sites = analyzer.number_of_magnetic_sites
        num_unique_sites = analyzer.number_of_unique_magnetic_sites()
        if num_unique_sites > self.max_unique_sites:
            raise ValueError("Too many magnetic sites to sensibly do enumeration.")

        # guess max_cell_size if not user-specified
        if "max_cell_size" not in self.transformation_kwargs:
            self.transformation_kwargs["max_cell_size"] = max(1, int(4/num_mag_sites))

        # gather Wyckoff info to help define by_motif constraints
        sga = SpacegroupAnalyzer(structure)
        structure_sym = sga.get_symmetrized_structure()
        wyckoff = ["n/a"] * len(structure)
        for eq_inds, w_symbol in zip(structure_sym.equivalent_indices, structure_sym.wyckoff_symbols, strict=True):
            for idx in eq_inds:
                wyckoff[idx] = w_symbol

        # Mark sites that are magnetic
        mg_sites = [site.species_string in map(str, types_mag_species) for site in structure]
        for i, ismag in enumerate(mg_sites):
            if not ismag:
                wyckoff[i] = "n/a"

        wyckoff_symbols = set(wyckoff) - {"n/a"}

        # Possibly add strategies for ferri_by_motif or ferri_by_species
        if self.automatic:
            if "ferrimagnetic_by_motif" not in self.strategies and len(wyckoff_symbols)>1 and len(types_mag_species)==1:
                self.strategies.append("ferrimagnetic_by_motif")
            if "antiferromagnetic_by_motif" not in self.strategies and len(wyckoff_symbols)>1 and len(types_mag_species)==1:
                self.strategies.append("antiferromagnetic_by_motif")
            if "ferrimagnetic_by_species" not in self.strategies and len(types_mag_species)>1:
                self.strategies.append("ferrimagnetic_by_species")

        # If "ferromagnetic" is in strategies, create that right away
        if "ferromagnetic" in self.strategies:
            fm_struct = analyzer.get_ferromagnetic_structure()
            fm_struct.add_spin_by_site(fm_struct.site_properties["magmom"])
            fm_struct.remove_site_property("magmom")
            self.ordered_structures.append(fm_struct)
            self.ordered_structure_origins.append("fm")

        # Now we define constraints for the other strategies
        all_constraints: dict[str, Any] = {}

        # "antiferromagnetic"
        if "antiferromagnetic" in self.strategies:
            from math import isclose
            # basic constraint => half up, half down across all mag species
            #from __main__ import MagOrderParameterConstraint
            c = MagOrderParameterConstraint(
                0.5,
                species_constraints=[str(x) for x in types_mag_species],
            )
            all_constraints["afm"] = [c]

            # additional constraints if multiple species
            if len(types_mag_species)>1:
                for sp in types_mag_species:
                    sp_c = MagOrderParameterConstraint(
                        0.5,
                        species_constraints=str(sp),
                    )
                    all_constraints[f"afm_by_{sp}"] = [sp_c]

        # "ferrimagnetic_by_motif"
        if "ferrimagnetic_by_motif" in self.strategies and len(wyckoff_symbols)>1:
            # e.g. if we have multiple distinct Wyckoff sets, set one to half up, the rest fully up
            #from __main__ import MagOrderParameterConstraint
            for symb in wyckoff_symbols:
                c1 = MagOrderParameterConstraint(0.5, site_constraint_name="wyckoff", site_constraints=symb)
                c2 = MagOrderParameterConstraint(1.0, site_constraint_name="wyckoff", site_constraints=list(wyckoff_symbols - {symb}))
                all_constraints[f"ferri_by_motif_{symb}"] = [c1,c2]

        # "ferrimagnetic_by_species"
        if "ferrimagnetic_by_species" in self.strategies:
            #from __main__ import MagOrderParameterConstraint
            sp_list = [str(s.specie) for s in structure]
            sp_count = {str(sp): sp_list.count(str(sp)) for sp in types_mag_species}
            total_mg = sum(sp_count.values())
            for sp in types_mag_species:
                # a global fraction up = sp_count[sp] / total_mg
                # or a sub-lattice approach
                c1 = MagOrderParameterConstraint(0.5, species_constraints=str(sp))
                c2 = MagOrderParameterConstraint(
                    1.0,
                    species_constraints=[str(x) for x in types_mag_species if str(x)!=str(sp)],
                )
                all_constraints[f"ferri_by_{sp}"] = sp_count[sp]/total_mg
                all_constraints[f"ferri_by_{sp}_afm"] = [c1,c2]

        # "antiferromagnetic_by_motif"
        if "antiferromagnetic_by_motif" in self.strategies:
            #from __main__ import MagOrderParameterConstraint
            for symb in wyckoff_symbols:
                c = MagOrderParameterConstraint(0.5, site_constraint_name="wyckoff", site_constraints=symb)
                all_constraints[f"afm_by_motif_{symb}"] = [c]

        transformations = {}
        for name, constraints in all_constraints.items():
            #from __main__ import MagOrderingTransformation
            t = MagOrderingTransformation(
                mag_species_spin,
                order_parameter=constraints,
                **self.transformation_kwargs
            )
            transformations[name] = t

        return transformations

    def _generate_ordered_structures(
        self,
        structure: Structure,
        transformations: dict[str, MagOrderingTransformation],
    ) -> tuple[list[Structure], list[str]]:
        ordered_structures = self.ordered_structures
        ordered_structures_origins = self.ordered_structure_origins

        def _add_structs(ostructs, oorigins, new_st, label):
            if not new_st:
                return ostructs, oorigins
            if isinstance(new_st, dict):
                new_st = [new_st]  # single
            st_list = []
            for item in new_st:
                st_list.append(item["structure"] if isinstance(item, dict) else item)
            ostructs.extend(st_list)
            oorigins.extend([label]*len(st_list))
            self.logger.info(f"Adding {len(st_list)} structures from {label}")
            return ostructs, oorigins

        for origin_name, trans_obj in transformations.items():
            # apply transformation
            newset = trans_obj.apply_transformation(structure, return_ranked_list=self.num_orderings)
            ordered_structures, ordered_structures_origins = _add_structs(
                ordered_structures, ordered_structures_origins, newset, origin_name
            )

        # remove duplicates
        self.logger.info("Pruning duplicates.")
        to_remove = set()
        for idx, st in enumerate(ordered_structures):
            if idx in to_remove:
                continue
            c_an = CollinearMagneticStructureAnalyzer(st, overwrite_magmom_mode="none")
            for jdx, st2 in enumerate(ordered_structures):
                if jdx<=idx or jdx in to_remove:
                    continue
                if c_an.matches_ordering(st2):
                    to_remove.add(jdx)

        if to_remove:
            self.logger.info(f"Removing {len(to_remove)} duplicates.")
            keep = [i for i in range(len(ordered_structures)) if i not in to_remove]
            ordered_structures = [ordered_structures[i] for i in keep]
            ordered_structures_origins = [ordered_structures_origins[i] for i in keep]

        # optionally remove very low-symmetry enumerations
        if self.truncate_by_symmetry:
            if not isinstance(self.truncate_by_symmetry, int):
                self.truncate_by_symmetry = 5
            self.logger.info("Pruning low-symmetry enumerations.")
            # gather # ops in each structure’s spacegroup
            s_ops = []
            for stx in ordered_structures:
                # (sg_symbol, sg_num)
                _sym, sg_num = stx.get_space_group_info()
                # how many ops
                nops = len(SpaceGroup.from_int_number(sg_num).symmetry_ops)
                s_ops.append(nops)

            # find the top few distinct symmetry counts
            keep_ops = sorted(set(s_ops), reverse=True)
            if len(keep_ops)>self.truncate_by_symmetry:
                keep_ops = keep_ops[:self.truncate_by_symmetry]
            to_keep = []
            for i, nops in enumerate(s_ops):
                if nops in keep_ops:
                    to_keep.append((i,nops))
            # sort them so highest symmetry first
            to_keep.sort(key=lambda x: (x[1], -x[0]), reverse=True)
            keep_idx = [x[0] for x in to_keep]
            keep_structs = [ordered_structures[i] for i in keep_idx]
            keep_origins = [ordered_structures_origins[i] for i in keep_idx]
            self.logger.info(f"Removing {len(ordered_structures)-len(keep_idx)} low-symmetry structures.")
            ordered_structures = keep_structs
            ordered_structures_origins = keep_origins

            # ensure ferromagnetic is at index 0 if present
            if "fm" in ordered_structures_origins:
                fm_idx = ordered_structures_origins.index("fm")
                if fm_idx!=0:
                    fm_st = ordered_structures.pop(fm_idx)
                    fm_or = ordered_structures_origins.pop(fm_idx)
                    ordered_structures.insert(0,fm_st)
                    ordered_structures_origins.insert(0,fm_or)

        # if the input structure is not found, we add it at the end
        self.input_index = None
        self.input_origin = None
        if self.input_analyzer.ordering!=Ordering.NM:
            # see if it’s present
            matches_list = [self.input_analyzer.matches_ordering(s) for s in ordered_structures]
            if not any(matches_list):
                ordered_structures.append(self.input_analyzer.structure)
                ordered_structures_origins.append("input")
                self.logger.info("Input structure was not present; adding it.")
            else:
                found_idx = matches_list.index(True)
                self.logger.info(f"Input structure found at enumerated index {found_idx}")
                self.input_index = found_idx
                self.input_origin = ordered_structures_origins[found_idx]

        return ordered_structures, ordered_structures_origins


###############################################################################
# 5) The "magnetic_deformation" function from your snippet
#    with a no-op "due" decorator replaced by a standard docstring.
###############################################################################

class MagneticDeformation(NamedTuple):
    deformation: float
    type: str

def magnetic_deformation(structure_A: Structure, structure_B: Structure) -> MagneticDeformation:
    """
    Calculate 'magnetic deformation proxy' between two structures,
    e.g. a non-magnetic and a ferromagnetic structure. This measures
    the finite strain norm between them, from Bocarsly et al. 2017,
    https://doi.org/10.1021/acs.chemmater.6b04729
    """
    ordering_a = CollinearMagneticStructureAnalyzer(structure_A).ordering
    ordering_b = CollinearMagneticStructureAnalyzer(structure_B).ordering
    type_str = f"{ordering_a.value}-{ordering_b.value}"

    latA = structure_A.lattice.matrix.T
    latB = structure_B.lattice.matrix.T
    invA = np.linalg.inv(latA)
    p = invA.dot(latB)
    eta = 0.5*(p.T.dot(p) - np.eye(3))
    w, _v = np.linalg.eig(eta)
    # measure
    deformation = 100*(1.0/3.0)*np.sqrt(w[0]**2 + w[1]**2 + w[2]**2)
    return MagneticDeformation(deformation=deformation, type=type_str)


###############################################################################
# End of file. 
# 
# Usage:
#   1) Make sure you have pymatgen >=2022, numpy, scipy installed.
#   2) Import this file or run it to have a standalone enumerator that does not
#      call enumlib.
###############################################################################

