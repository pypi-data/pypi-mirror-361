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

"""


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup()

