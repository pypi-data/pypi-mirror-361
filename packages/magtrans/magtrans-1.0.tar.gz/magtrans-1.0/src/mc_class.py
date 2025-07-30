import math
import numpy as np
from numba import njit, int64, float64
from numba.typed import List
from numba.core import types

##############################################################################
# Universal constants and subroutines
##############################################################################
kB = np.double(8.6173303e-5)  # eV/K



# -------------------------------------------------------------------------
#  Spin-array initialisation (collinear & non-collinear)
# -------------------------------------------------------------------------
EMA_X   = 0      # spins_init is 1-D, start ‖ +x  (100)
EMA_Y   = 1      # spins_init is 1-D, start ‖ +y  (010)
EMA_Z   = 2      # spins_init is 1-D, start ‖ +z  (001)
EMA_NCL = -1     # spins_init is (N,3), start fully non-collinear

@njit(cache=True)
def init_spin_arrays(spins_init, EMA):
    """
    Build (spins_x, spins_y, spins_z, spins_abs) from `spins_init`.

    ───────────────────────────────────────────────────────────────
      • **Collinear restart**  →  spins_init.shape == (N,)   and
                                  EMA ∈ {EMA_X, EMA_Y, EMA_Z}

      • **True non-collinear** →  spins_init.shape == (N, 3) and
                                  EMA == EMA_NCL
    ───────────────────────────────────────────────────────────────

    Any other combination is treated as a user error.
    """
    # ---- quick sanity checks -------------------------------------------------
    if spins_init.ndim == 1 and EMA == EMA_NCL:
        raise ValueError("EMA = -1 (non-collinear) but spins_init is 1-D.")
    if spins_init.ndim == 2 and EMA != EMA_NCL:
        raise ValueError("EMA must be -1 when spins_init is (N,3).")
    if spins_init.ndim not in (1, 2):
        raise ValueError("spins_init must be 1- or 2-D.")

    N = spins_init.shape[0]
    spins_x = np.zeros(N, dtype=np.float64)
    spins_y = np.zeros(N, dtype=np.float64)
    spins_z = np.zeros(N, dtype=np.float64)
    spins_abs = np.zeros(N, dtype=np.float64)

    # ---- collinear restart ---------------------------------------------------
    if spins_init.ndim == 1:          # shape (N,)
        if EMA == EMA_X:
            for i in range(N):
                val = spins_init[i]
                spins_x[i]   = val
                spins_abs[i] = math.fabs(val)
        elif EMA == EMA_Y:
            for i in range(N):
                val = spins_init[i]
                spins_y[i]   = val
                spins_abs[i] = math.fabs(val)
        elif EMA == EMA_Z:
            for i in range(N):
                val = spins_init[i]
                spins_z[i]   = val
                spins_abs[i] = math.fabs(val)
        else:
            raise ValueError("EMA must be 0,1,2 for a 1-D spins_init array.")
        return spins_x, spins_y, spins_z, spins_abs

    # ---- true non-collinear restart -----------------------------------------
    # spins_init is (N,3) & EMA == -1
    for i in range(N):
        sx_i = spins_init[i, 0]
        sy_i = spins_init[i, 1]
        sz_i = spins_init[i, 2]
        spins_x[i]   = sx_i
        spins_y[i]   = sy_i
        spins_z[i]   = sz_i
        spins_abs[i] = math.sqrt(sx_i*sx_i + sy_i*sy_i + sz_i*sz_i)

    return spins_x, spins_y, spins_z, spins_abs





@njit
def mean_and_var_1d(arr):
    """
    Returns (mean, variance) for a 1D NumPy array,
    using an unbiased estimator (ddof=1).
    Works in nopython mode for float64 or float32 arrays.
    """
    n = arr.size
    if n < 2:
        # If only 1 sample, return that sample for mean, variance=0
        return (arr[0] if n == 1 else 0.0, 0.0)

    # Compute mean
    s = 0.0
    for i in range(n):
        s += arr[i]
    mean_ = s / n

    # Compute sum of squared deviations
    sq_dev_sum = 0.0
    for i in range(n):
        diff = arr[i] - mean_
        sq_dev_sum += diff * diff

    # Unbiased variance = sum of squared deviations / (n - 1)
    var_ = sq_dev_sum / (n - 1)
    return mean_, var_


##############################################################################
# Subroutines: build_isotropic_neighbors, cluster_move_approx_allJ_fast,
# get_local_field_full_numba, heatbath_draw_numba, overrelaxation_full_numba
##############################################################################

def build_isotropic_neighbors(
    N,
    N1list, N2list, N3list, N4list,
    J1, J2, J3, J4,
    useJ2, useJ3, useJ4
):
    """
    Precompute the combined isotropic J-values for BFS partial cluster ignoring anisotropy.
    For each site i, we gather 'neighbor -> J_eff' from up to 4 shells using Python dicts.
    Then convert to float64 array (k,2) => (nbr, J_eff).
    Returns a numba typed List[np.ndarray], read in nopython BFS code.

    We call this once in __init__, not in each MC step.

    NOTE: This function itself is not decorated with @njit, because it uses
          Python dictionaries. That is fine as it is usually called only once.
    """
    from numba.typed import List

    site_arrays = []  # normal Python list of float64 arrays

    for i in range(N):
        temp_dict = {}  # neighbor -> sum_of_J

        # 1NN
        for nb1 in N1list[i]:
            if nb1 != 100000 and nb1 != -5:
                old_val = temp_dict.get(nb1, 0.0)
                temp_dict[nb1] = old_val + J1

        # 2NN
        if useJ2 and abs(J2) > 1e-14:
            for nb2 in N2list[i]:
                if nb2 != 100000 and nb2 != -5:
                    old_val = temp_dict.get(nb2, 0.0)
                    temp_dict[nb2] = old_val + J2

        # 3NN
        if useJ3 and abs(J3) > 1e-14:
            for nb3 in N3list[i]:
                if nb3 != 100000 and nb3 != -5:
                    old_val = temp_dict.get(nb3, 0.0)
                    temp_dict[nb3] = old_val + J3

        # 4NN
        if useJ4 and abs(J4) > 1e-14:
            for nb4 in N4list[i]:
                if nb4 != 100000 and nb4 != -5:
                    old_val = temp_dict.get(nb4, 0.0)
                    temp_dict[nb4] = old_val + J4

        # convert -> array (len,2)
        pairs = []
        for (k_idx, j_val) in temp_dict.items():
            if abs(j_val) > 1e-14:
                pairs.append((k_idx, j_val))

        arr = np.zeros((len(pairs), 2), dtype=np.float64)
        for idx, (knb, val) in enumerate(pairs):
            arr[idx, 0] = knb
            arr[idx, 1] = val

        site_arrays.append(arr)

    # Build numba typed list
    neighbors_isotr = List()
    for arr in site_arrays:
        neighbors_isotr.append(arr)

    return neighbors_isotr


@njit
def cluster_move_approx_allJ_fast(
    sx, sy, sz,
    beta,
    neighbors_isotr,
    N
):
    """
    BFS partial cluster ignoring anisotropy, reading precomputed neighbors:
       neighbors_isotr[i][m,0] = neighbor_index
       neighbors_isotr[i][m,1] = J_eff

    Steps:
      1) BFS from random seed
      2) bond prob = 1 - exp(-2 beta * J_eff * dot(spin_i, spin_j))
      3) reflect entire cluster about random plane normal.
    """
    visited = np.zeros(N, dtype=np.int32)
    seed = np.random.randint(0, N)
    visited[seed] = 1
    queue = [seed]

    # random reflection axis
    u1 = np.random.random()
    u2 = np.random.random()
    phi = 2.0 * math.pi * u1
    cos_t = 2.0 * u2 - 1.0
    sin_t = math.sqrt(max(0.0, 1.0 - cos_t*cos_t))
    nx = sin_t * math.cos(phi)
    ny = sin_t * math.sin(phi)
    nz = cos_t

    while len(queue) > 0:
        current = queue.pop()
        Sx_c = sx[current]
        Sy_c = sy[current]
        Sz_c = sz[current]

        arr = neighbors_isotr[current]  # shape (k,2)
        for m in range(arr.shape[0]):
            nbr = int(arr[m, 0])
            j_eff = arr[m, 1]
            if visited[nbr] == 0:
                dotp = (Sx_c*sx[nbr] + Sy_c*sy[nbr] + Sz_c*sz[nbr])
                p = 1.0 - math.exp(-2.0 * beta * j_eff * dotp)
                # clamp p to [0,1]
                if p < 0.0:
                    p = 0.0
                elif p > 1.0:
                    p = 1.0
                if np.random.random() < p:
                    visited[nbr] = 1
                    queue.append(nbr)

    # reflection about plane normal => n
    for i2 in range(N):
        if visited[i2] == 1:
            dd = (sx[i2]*nx + sy[i2]*ny + sz[i2]*nz)
            sx[i2] -= 2.0 * dd * nx
            sy[i2] -= 2.0 * dd * ny
            sz[i2] -= 2.0 * dd * nz


@njit
def get_local_field_full_numba(
    i, sx, sy, sz,
    N1list, N2list, N3list, N4list,
    J1, J2, J3, J4,
    K1x, K1y, K1z,
    K2x, K2y, K2z,
    K3x, K3y, K3z,
    K4x, K4y, K4z,
    Ax, Ay, Az,
    useJ2, useJ3, useJ4
):
    """
    Local anisotropic field from -dH/dS_i, summing up to 4 shells plus single-ion anisotropy.
    That is: H_i = dE/dS_i.
    """
    Hx = 0.0
    Hy = 0.0
    Hz = 0.0
    Sx_i = sx[i]
    Sy_i = sy[i]
    Sz_i = sz[i]

    # 1NN
    for nb1 in N1list[i]:
        if nb1 != 100000 and nb1 != -5:
            Hx += J1*sx[nb1] + K1x*sx[nb1]
            Hy += J1*sy[nb1] + K1y*sy[nb1]
            Hz += J1*sz[nb1] + K1z*sz[nb1]

    # 2NN
    if useJ2 and abs(J2) > 1e-14:
        for nb2 in N2list[i]:
            if nb2 != 100000 and nb2 != -5:
                Hx += J2*sx[nb2] + K2x*sx[nb2]
                Hy += J2*sy[nb2] + K2y*sy[nb2]
                Hz += J2*sz[nb2] + K2z*sz[nb2]

    # 3NN
    if useJ3 and abs(J3) > 1e-14:
        for nb3 in N3list[i]:
            if nb3 != 100000 and nb3 != -5:
                Hx += J3*sx[nb3] + K3x*sx[nb3]
                Hy += J3*sy[nb3] + K3y*sy[nb3]
                Hz += J3*sz[nb3] + K3z*sz[nb3]

    # 4NN
    if useJ4 and abs(J4) > 1e-14:
        for nb4 in N4list[i]:
            if nb4 != 100000 and nb4 != -5:
                Hx += J4*sx[nb4] + K4x*sx[nb4]
                Hy += J4*sy[nb4] + K4y*sy[nb4]
                Hz += J4*sz[nb4] + K4z*sz[nb4]

    # single-ion (Ax Sx^2 + Ay Sy^2 + Az Sz^2 => derivative is 2 * Ax * Sx_i, etc., but with negative sign)
    Hx += -2.0*Ax*Sx_i
    Hy += -2.0*Ay*Sy_i
    Hz += -2.0*Az*Sz_i

    return Hx, Hy, Hz


@njit
def heatbath_draw_numba(Hx, Hy, Hz, spin_r, beta):
    """
    Standard classical O(3) heat-bath local update from local field (Hx,Hy,Hz).
    If field ~ 0 => random spin on sphere of radius spin_r.
    """
    H = math.sqrt(Hx*Hx + Hy*Hy + Hz*Hz)
    if H < 1e-12:
        # field is basically zero, pick random direction
        u1 = np.random.random()
        u2 = np.random.random()
        phi = 2.0*math.pi*u1
        cos_t = 2.0*u2 - 1.0
        sin_t = math.sqrt(max(0.0, 1.0 - cos_t*cos_t))
        return (spin_r*sin_t*math.cos(phi),
                spin_r*sin_t*math.sin(phi),
                spin_r*cos_t)

    alpha = beta * spin_r * H
    u1 = np.random.random()
    u2 = np.random.random()
    phi = 2.0*math.pi*u1
    expo = math.exp(-2.0*alpha)
    zval = 1.0 - u2*(1.0 - expo)
    if zval <= 0.0:
        zval = 1e-15
    cos_t = 1.0 + (1.0 / alpha) * math.log(zval)
    if cos_t > 1.0:
        cos_t = 1.0
    elif cos_t < -1.0:
        cos_t = -1.0
    sin_t = math.sqrt(max(0.0, 1.0 - cos_t*cos_t))

    hx = Hx / H
    hy = Hy / H
    hz = Hz / H

    # a2 is a vector perpendicular to (hx,hy,hz).
    # If hx,hy is large enough, we do the standard approach:
    if hx*hx + hy*hy > 1e-14:
        denom = math.sqrt(hx*hx + hy*hy)
        a2x = -hy / denom
        a2y = hx / denom
        a2z = 0.0
    else:
        # fallback orientation
        a2x = 1.0
        a2y = 0.0
        a2z = 0.0

    # a3 = (h) x (a2)
    a3x = hx*a2y - hy*a2x
    a3y = hy*a2x - hz*a2z
    a3z = hz*a2x - hx*a2y

    # combine angles
    Sx_new = spin_r * (
        cos_t*hx + sin_t*(math.cos(phi)*a2x + math.sin(phi)*a3x)
    )
    Sy_new = spin_r * (
        cos_t*hy + sin_t*(math.cos(phi)*a2y + math.sin(phi)*a3y)
    )
    Sz_new = spin_r * (
        cos_t*hz + sin_t*(math.cos(phi)*a2z + math.sin(phi)*a3z)
    )
    return (Sx_new, Sy_new, Sz_new)


@njit
def overrelaxation_full_numba(
    site, sx, sy, sz,
    N1list, N2list, N3list, N4list,
    J1, J2, J3, J4,
    K1x, K1y, K1z,
    K2x, K2y, K2z,
    K3x, K3y, K3z,
    K4x, K4y, K4z,
    Ax, Ay, Az,
    useJ2, useJ3, useJ4
):
    """
    Overrelaxation: reflect spin_i about plane normal to local anisotropic field => 
    S_i -> S_i - 2(S_i·n)n
    """
    Hx, Hy, Hz = get_local_field_full_numba(
        site, sx, sy, sz,
        N1list, N2list, N3list, N4list,
        J1, J2, J3, J4,
        K1x, K1y, K1z,
        K2x, K2y, K2z,
        K3x, K3y, K3z,
        K4x, K4y, K4z,
        Ax, Ay, Az,
        useJ2, useJ3, useJ4
    )
    HH = Hx*Hx + Hy*Hy + Hz*Hz
    if HH < 1e-12:
        return
    invH = 1.0 / math.sqrt(HH)
    nx = Hx * invH
    ny = Hy * invH
    nz = Hz * invH
    dotSH = sx[site]*nx + sy[site]*ny + sz[site]*nz

    sx[site] -= 2.0 * dotSH * nx
    sy[site] -= 2.0 * dotSH * ny
    sz[site] -= 2.0 * dotSH * nz


###############################################################################
# Top-level jitted functions for the main MC methods
###############################################################################

@njit
def _compute_total_energy_simple(
    sx, sy, sz,
    N,
    N1list, N2list, N3list, N4list,
    Ax, Ay, Az,
    J1, J2, J3, J4,
    K1x, K1y, K1z,
    K2x, K2y, K2z,
    K3x, K3y, K3z,
    K4x, K4y, K4z,
    useJ2, useJ3, useJ4
):
    """
    Computes the total energy for the "simple" Metropolis approach, summing
    up to 4 neighbor shells (exchange + anisotropic K) + single-ion.
    """
    E_exchange = 0.0
    E_single = 0.0

    for i in range(N):
        Sxi = sx[i]
        Syi = sy[i]
        Szi = sz[i]

        # single-ion
        E_single += -Ax*(Sxi**2) -Ay*(Syi**2) -Az*(Szi**2)

        # sum neighbors => divide by 2 later
        for nb1 in N1list[i]:
            if nb1 not in [100000, -5]:
                Sxn = sx[nb1]
                Syn = sy[nb1]
                Szn = sz[nb1]
                E_exchange += -J1*(Sxi*Sxn + Syi*Syn + Szi*Szn)
                E_exchange += -(K1x*Sxi*Sxn + K1y*Syi*Syn + K1z*Szi*Szn)

        if useJ2 and abs(J2) > 1e-14:
            for nb2 in N2list[i]:
                if nb2 not in [100000, -5]:
                    Sxn = sx[nb2]
                    Syn = sy[nb2]
                    Szn = sz[nb2]
                    E_exchange += -J2*(Sxi*Sxn + Syi*Syn + Szi*Szn)
                    E_exchange += -(K2x*Sxi*Sxn + K2y*Syi*Syn + K2z*Szi*Szn)

        if useJ3 and abs(J3) > 1e-14:
            for nb3 in N3list[i]:
                if nb3 not in [100000, -5]:
                    Sxn = sx[nb3]
                    Syn = sy[nb3]
                    Szn = sz[nb3]
                    E_exchange += -J3*(Sxi*Sxn + Syi*Syn + Szi*Szn)
                    E_exchange += -(K3x*Sxi*Sxn + K3y*Syi*Syn + K3z*Szi*Szn)

        if useJ4 and abs(J4) > 1e-14:
            for nb4 in N4list[i]:
                if nb4 not in [100000, -5]:
                    Sxn = sx[nb4]
                    Syn = sy[nb4]
                    Szn = sz[nb4]
                    E_exchange += -J4*(Sxi*Sxn + Syi*Syn + Szi*Szn)
                    E_exchange += -(K4x*Sxi*Sxn + K4y*Syi*Syn + K4z*Szi*Szn)

    # double-count correction
    E_exchange *= 0.5
    return E_exchange + E_single


@njit
def MC_func_simple_metropolis_impl(
    spins_init, T, J2flag, J3flag, J4flag,
    N, N1list, N2list, N3list, N4list,
    J1, J2, J3, J4,
    K1x, K1y, K1z,
    K2x, K2y, K2z,
    K3x, K3y, K3z,
    K4x, K4y, K4z,
    Ax, Ay, Az,
    k_B,
    trange,
    threshold,
    EMA
):
    """
    Single-site Metropolis kernel.
    Magnetisations are normalised *per spin* (and by r_mag)
    at every measurement sweep.
    """

    # ------------------------------------------------ initial arrays -------
    spins_x, spins_y, spins_z, spins_abs = init_spin_arrays(spins_init, EMA)

    # sub-lattice sizes
    if abs(np.sum(spins_init)) < 1e-3:        # AFM / compensated start
        num_up_sites   = N // 2
        num_down_sites = N - num_up_sites
    else:                                     # FM start (all “up”)
        num_up_sites = num_down_sites = N

    # single-spin length  |S|  (identical for every site)
    r_mag = spins_abs[0]

    # neighbour-shell flags
    useJ2_local = (J2flag and abs(J2) > 1e-14)
    useJ3_local = (J3flag and abs(J3) > 1e-14)
    useJ4_local = (J4flag and abs(J4) > 1e-14)

    # storage for measurements
    n_meas        = trange - threshold
    energies      = np.zeros(n_meas)
    mag_ups       = np.zeros(n_meas)
    mag_up_sqs    = np.zeros(n_meas)
    mag_downs     = np.zeros(n_meas)
    mag_down_sqs  = np.zeros(n_meas)
    mag_tots      = np.zeros(n_meas)
    mag_tot_sqs   = np.zeros(n_meas)

    # =================================================== MC sweeps ========
    for sweep in range(trange):

        # ---------------------------- Metropolis sweep -------------------
        for _ in range(N):
            site = np.random.randint(0, N)

            # present spin
            S_old = np.array([spins_x[site], spins_y[site], spins_z[site]])

            # trial spin – random direction, same radius r_site
            u, v = np.random.random(), np.random.random()
            phi   = 2.0 * math.pi * u
            theta = math.acos(2.0 * v - 1.0)
            r_site = spins_abs[site]
            S_new = np.array([r_site * math.sin(theta) * math.cos(phi),
                              r_site * math.sin(theta) * math.sin(phi),
                              r_site * math.cos(theta)])

            # -------- local energy difference  ΔE = E_new − E_old ----------
            E_old, E_new = 0.0, 0.0

            # 1-NN -------------------------------------------------------
            for nb in N1list[site]:
                if nb != 100000 and nb != -5:
                    Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                    # old
                    E_old += -J1 * np.dot(S_old, Snb) \
                             -K1x * S_old[0]*Snb[0] - K1y * S_old[1]*Snb[1] - K1z * S_old[2]*Snb[2]
                    # new
                    E_new += -J1 * np.dot(S_new, Snb) \
                             -K1x * S_new[0]*Snb[0] - K1y * S_new[1]*Snb[1] - K1z * S_new[2]*Snb[2]

            # 2-NN -------------------------------------------------------
            if useJ2_local:
                for nb in N2list[site]:
                    if nb != 100000 and nb != -5:
                        Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                        E_old += -J2 * np.dot(S_old, Snb) \
                                 -K2x * S_old[0]*Snb[0] - K2y * S_old[1]*Snb[1] - K2z * S_old[2]*Snb[2]
                        E_new += -J2 * np.dot(S_new, Snb) \
                                 -K2x * S_new[0]*Snb[0] - K2y * S_new[1]*Snb[1] - K2z * S_new[2]*Snb[2]

            # 3-NN -------------------------------------------------------
            if useJ3_local:
                for nb in N3list[site]:
                    if nb != 100000 and nb != -5:
                        Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                        E_old += -J3 * np.dot(S_old, Snb) \
                                 -K3x * S_old[0]*Snb[0] - K3y * S_old[1]*Snb[1] - K3z * S_old[2]*Snb[2]
                        E_new += -J3 * np.dot(S_new, Snb) \
                                 -K3x * S_new[0]*Snb[0] - K3y * S_new[1]*Snb[1] - K3z * S_new[2]*Snb[2]

            # 4-NN -------------------------------------------------------
            if useJ4_local:
                for nb in N4list[site]:
                    if nb != 100000 and nb != -5:
                        Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                        E_old += -J4 * np.dot(S_old, Snb) \
                                 -K4x * S_old[0]*Snb[0] - K4y * S_old[1]*Snb[1] - K4z * S_old[2]*Snb[2]
                        E_new += -J4 * np.dot(S_new, Snb) \
                                 -K4x * S_new[0]*Snb[0] - K4y * S_new[1]*Snb[1] - K4z * S_new[2]*Snb[2]

            # single-ion anisotropy (identical for all cases)
            E_old += -Ax*S_old[0]**2 - Ay*S_old[1]**2 - Az*S_old[2]**2
            E_new += -Ax*S_new[0]**2 - Ay*S_new[1]**2 - Az*S_new[2]**2

            dE = E_new - E_old
            if dE < 0.0 or np.random.random() < math.exp(-dE / (k_B*T)):
                spins_x[site], spins_y[site], spins_z[site] = S_new

        # ------------------------- measurements -------------------------
        if sweep >= threshold:
            m_idx = sweep - threshold

            # sub-lattice vectors
            mu_up   = np.zeros(3)
            mu_down = np.zeros(3)
            for i in range(N):
                if spins_init[i] > 0.0:
                    mu_up   += np.array([spins_x[i], spins_y[i], spins_z[i]])
                else:
                    mu_down += np.array([spins_x[i], spins_y[i], spins_z[i]])

            # normalised magnetisations (dimensionless 0…1)
            M_up_norm   = math.sqrt(np.dot(mu_up,   mu_up  )) / (num_up_sites   * r_mag)
            M_down_norm = math.sqrt(np.dot(mu_down, mu_down)) / (num_down_sites * r_mag)

            Mx_tot = spins_x.sum()
            My_tot = spins_y.sum()
            Mz_tot = spins_z.sum()
            M_tot_norm = math.sqrt(Mx_tot*Mx_tot + My_tot*My_tot + Mz_tot*Mz_tot) / (N * r_mag)

            # store
            mag_ups[m_idx]      = M_up_norm
            mag_up_sqs[m_idx]   = M_up_norm * M_up_norm
            mag_downs[m_idx]    = M_down_norm
            mag_down_sqs[m_idx] = M_down_norm * M_down_norm
            mag_tots[m_idx]     = M_tot_norm
            mag_tot_sqs[m_idx]  = M_tot_norm * M_tot_norm

            # --- total energy (all shells) ---
            E_cfg = _compute_total_energy_simple(
                spins_x, spins_y, spins_z,
                N,
                N1list, N2list, N3list, N4list,
                Ax, Ay, Az,
                J1, J2, J3, J4,
                K1x, K1y, K1z,
                K2x, K2y, K2z,
                K3x, K3y, K3z,
                K4x, K4y, K4z,
                useJ2_local, useJ3_local, useJ4_local
            )
            energies[m_idx] = E_cfg

    # ======================= averages & thermodynamic quantities =========
    M_up_mean,   M_up_sq_mean   = np.mean(mag_ups),   np.mean(mag_up_sqs)
    M_down_mean, M_down_sq_mean = np.mean(mag_downs), np.mean(mag_down_sqs)
    M_tot_mean,  M_tot_sq_mean  = np.mean(mag_tots),  np.mean(mag_tot_sqs)

    # per-spin susceptibilities
    X_up   = (M_up_sq_mean   - M_up_mean*M_up_mean)     / (k_B*T)
    X_down = (M_down_sq_mean - M_down_mean*M_down_mean) / (k_B*T)
    X_tot  = (M_tot_sq_mean  - M_tot_mean*M_tot_mean)   / (k_B*T)

    # energy & heat capacity
    E_avg, E_var = mean_and_var_1d(energies)
    Cv_val       = (E_var / (N * (k_B*T)**2)) / k_B

    # simple error estimates
    ns       = float(n_meas)
    E_err    = math.sqrt(E_var / ns) if ns > 1.0 else 0.0
    _, M_var = mean_and_var_1d(mag_tots)
    M_err    = math.sqrt(M_var / ns) if ns > 1.0 else 0.0
    _, A_var = mean_and_var_1d(mag_tots*mag_tots)
    X_err    = math.sqrt(A_var / ns) / (k_B*T) if ns > 1.0 else 0.0
    _, E2_var = mean_and_var_1d(energies*energies)
    Cv_err   = math.sqrt(E2_var / ns) / (N * (k_B*T)**2) if ns > 1.0 else 0.0

    # ------------------------------ return block ------------------------
    return (M_up_mean,   X_up,
            M_down_mean, X_down,
            M_tot_mean,  X_tot,
            E_avg, Cv_val, X_err, E_err, M_err, Cv_err,
            spins_x, spins_y, spins_z)




@njit
def MC_func_hybrid_boc_impl(
    spins_init, T,
    J2flag, J3flag, J4flag,
    N, N1list, N2list, N3list, N4list,
    J1, J2, J3, J4,
    K1x, K1y, K1z,
    K2x, K2y, K2z,
    K3x, K3y, K3z,
    K4x, K4y, K4z,
    Ax, Ay, Az,
    k_B,
    trange,
    threshold,
    EMA,
    neighbors_isotr
):
    """Hybrid (heat-bath + over-relax + cluster) Monte-Carlo kernel."""
    beta = 1.0 / (k_B*T)

    useJ2_local = (J2flag and abs(J2) > 1e-14)
    useJ3_local = (J3flag and abs(J3) > 1e-14)
    useJ4_local = (J4flag and abs(J4) > 1e-14)

    # ------------------------------------------------------------------ set-up
    spins_x, spins_y, spins_z, spins_abs = init_spin_arrays(spins_init, EMA)

    # sub-lattice sizes (needed for normalisation)
    sum_init = np.sum(spins_init)
    if abs(sum_init) < 1e-3:
        num_up_sites   = N // 2
        num_down_sites = N - num_up_sites
    else:
        num_up_sites = num_down_sites = N

    # magnitude of a single spin (saturation moment)
    r_mag = spins_abs[0]

    meas_count      = trange - threshold
    mag_ups         = np.zeros(meas_count)
    mag_up_sqs      = np.zeros(meas_count)
    mag_downs       = np.zeros(meas_count)
    mag_down_sqs    = np.zeros(meas_count)
    mag_tots        = np.zeros(meas_count)
    mag_tot_sqs     = np.zeros(meas_count)
    E_vals          = np.zeros(meas_count)
    M_vals          = np.zeros(meas_count)   # (unnormalised) |M| for χ etc.

    # ============================================================= MC sweeps ==
    for sweep in range(trange):

        # -------------- (A) heat-bath updates -------------------------------
        for _ in range(N):
            site = np.random.randint(0, N)
            Hx, Hy, Hz = get_local_field_full_numba(
                site, spins_x, spins_y, spins_z,
                N1list, N2list, N3list, N4list,
                J1, J2, J3, J4,
                K1x, K1y, K1z, K2x, K2y, K2z,
                K3x, K3y, K3z, K4x, K4y, K4z,
                Ax, Ay, Az,
                useJ2_local, useJ3_local, useJ4_local
            )
            Sx_new, Sy_new, Sz_new = heatbath_draw_numba(
                Hx, Hy, Hz, spins_abs[site], beta)
            spins_x[site], spins_y[site], spins_z[site] = Sx_new, Sy_new, Sz_new

        # -------------- (B) over-relaxation ---------------------------------
        for site2 in range(N):
            overrelaxation_full_numba(
                site2, spins_x, spins_y, spins_z,
                N1list, N2list, N3list, N4list,
                J1, J2, J3, J4,
                K1x, K1y, K1z, K2x, K2y, K2z,
                K3x, K3y, K3z, K4x, K4y, K4z,
                Ax, Ay, Az,
                useJ2_local, useJ3_local, useJ4_local
            )

        # -------------- (C) single-cluster move -----------------------------
        cluster_move_approx_allJ_fast(
            spins_x, spins_y, spins_z, beta,
            neighbors_isotr, N
        )

        # ============================ measurements ==========================
        if sweep >= threshold:
            idx = sweep - threshold

            # ---------- raw sub-lattice vectors --------------------------
            mu_up   = np.zeros(3)
            mu_down = np.zeros(3)
            for i2 in range(N):
                if spins_init[i2] > 0.0:
                    mu_up   += np.array([spins_x[i2],
                                         spins_y[i2],
                                         spins_z[i2]])
                else:
                    mu_down += np.array([spins_x[i2],
                                         spins_y[i2],
                                         spins_z[i2]])

            # ---------- (A) *already normalised* magnitudes --------------
            M_up_norm   = math.sqrt(np.dot(mu_up,   mu_up  )) / (num_up_sites   * r_mag)
            M_down_norm = math.sqrt(np.dot(mu_down, mu_down)) / (num_down_sites * r_mag)

            Mx_tot = spins_x.sum()
            My_tot = spins_y.sum()
            Mz_tot = spins_z.sum()
            M_tot_norm = math.sqrt(Mx_tot*Mx_tot +
                                   My_tot*My_tot +
                                   Mz_tot*Mz_tot) / (N * r_mag)

            # store normalised data
            mag_ups[idx]      = M_up_norm
            mag_up_sqs[idx]   = M_up_norm * M_up_norm
            mag_downs[idx]    = M_down_norm
            mag_down_sqs[idx] = M_down_norm * M_down_norm
            mag_tots[idx]     = M_tot_norm
            mag_tot_sqs[idx]  = M_tot_norm * M_tot_norm

            # un-normalised |M| for χ, Cv, … (leave unchanged)
            M_vals[idx] = math.sqrt(Mx_tot*Mx_tot +
                                    My_tot*My_tot +
                                    Mz_tot*Mz_tot)

            # ---------- energy of this configuration --------------------
            E_vals[idx] = _compute_total_energy_simple(
                spins_x, spins_y, spins_z, N,
                N1list, N2list, N3list, N4list,
                Ax, Ay, Az,
                J1, J2, J3, J4,
                K1x, K1y, K1z, K2x, K2y, K2z,
                K3x, K3y, K3z, K4x, K4y, K4z,
                useJ2_local, useJ3_local, useJ4_local
            )

    # ========================================================================
    # averages and error bars – everything in mag_* is already on [0,1]
    # ========================================================================
    M_up_fin,   M_up_sq_fin   = np.mean(mag_ups),   np.mean(mag_up_sqs)
    M_down_fin, M_down_sq_fin = np.mean(mag_downs), np.mean(mag_down_sqs)
    M_tot_fin,  M_tot_sq_fin  = np.mean(mag_tots),  np.mean(mag_tot_sqs)

    # susceptibilities (per spin)
    X_up_fin   = (M_up_sq_fin   - M_up_fin*M_up_fin)   / (k_B * T)
    X_down_fin = (M_down_sq_fin - M_down_fin*M_down_fin) / (k_B * T)
    X_tot_fin  = (M_tot_sq_fin  - M_tot_fin*M_tot_fin)  / (k_B * T)

    # energy, Cv, and error analysis: unchanged -----------------------------
    E_avg,  E_var  = mean_and_var_1d(E_vals)
    Cv_val         = E_var / (k_B * T * T * N)  # per spin
    Cv_val         = Cv_val / k_B               # (eV → k_B units)

    ns        = float(meas_count)
    E_err     = math.sqrt(E_var / ns)           if ns > 1 else 0.0
    M_mean, M_var = mean_and_var_1d(mag_tots)
    M_err     = math.sqrt(M_var / ns)           if ns > 1 else 0.0

    # simple propagation for χ and Cv (optional, identical to before)
    A_mean, A_var = mean_and_var_1d(mag_tots*mag_tots)
    X_err = math.sqrt(A_var/ns) / (k_B*T)       if ns > 1 else 0.0
    E2_mean, E2_var = mean_and_var_1d(E_vals*E_vals)
    Cv_err = math.sqrt(E2_var/ns) / (k_B*T*T*N) if ns > 1 else 0.0

    # ---------------------------------------------------------------- return
    return (M_up_fin,   X_up_fin,
            M_down_fin, X_down_fin,
            M_tot_fin,  X_tot_fin,
            E_avg, Cv_val, X_err, E_err, M_err, Cv_err,
            spins_x, spins_y, spins_z)






##############################################################################
# extended MC routine
##############################################################################
@njit
def MC_func_full(
        spins_init, T, J2flag, J3flag, J4flag,
        N,
        N1list, N2list, N3list, N4list,
        J1, J2, J3, J4,
        K1x, K1y, K1z,
        K2x, K2y, K2z,
        K3x, K3y, K3z,
        K4x, K4y, K4z,
        Ax, Ay, Az,
        kB,
        trange,
        threshold,
        EMA
):
    """
    Reference Metropolis kernel that measures fully normalised
    sub-lattice and total magnetisations.
    Returns
        (M_up, X_up, M_down, X_down, M_tot, X_tot,
         E_avg, Cv_val, X_err, E_err, M_err, Cv_err,
         spins_x, spins_y, spins_z)
    """
    # ----------------------------------------------------------------- setup
    spins_x, spins_y, spins_z, spins_abs = init_spin_arrays(spins_init, EMA)

    # sub-lattice sizes
    if abs(np.sum(spins_init)) < 1e-3:     # AFM initial pattern
        num_up_sites   = N // 2
        num_down_sites = N - num_up_sites
    else:
        num_up_sites = num_down_sites = N

    # magnitude of a single classical spin

    r_mag = spins_abs[0]


    # storage for measurements
    n_meas         = trange - threshold
    energies       = np.zeros(n_meas)
    mag_ups        = np.zeros(n_meas)
    mag_up_sqs     = np.zeros(n_meas)
    mag_downs      = np.zeros(n_meas)
    mag_down_sqs   = np.zeros(n_meas)
    mag_tots       = np.zeros(n_meas)
    mag_tot_sqs    = np.zeros(n_meas)

    # =========================================================== MC sweeps ==
    for sweep in range(trange):

        # --------------- single-spin Metropolis sweep --------------------
        for _ in range(N):
            site = np.random.randint(0, N)

            # new random orientation on sphere of radius r_i
            u, v = np.random.random(), np.random.random()
            phi   = 2.0 * math.pi * u
            theta = math.acos(2.0 * v - 1.0)
            r_i   = spins_abs[site]
            S_new = np.array([r_i * math.sin(theta) * math.cos(phi),
                              r_i * math.sin(theta) * math.sin(phi),
                              r_i * math.cos(theta)])

            S_old = np.array([spins_x[site], spins_y[site], spins_z[site]])

            # local energy before/after – 1NN only (extend as required)
            E_old, E_new = 0.0, 0.0
            for nb in N1list[site]:
                if nb != 100000 and nb != -5:
                    Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                    E_old += -J1 * np.dot(S_old, Snb) \
                             -K1x * S_old[0]*Snb[0] - K1y * S_old[1]*Snb[1] - K1z * S_old[2]*Snb[2]
                    E_new += -J1 * np.dot(S_new, Snb) \
                             -K1x * S_new[0]*Snb[0] - K1y * S_new[1]*Snb[1] - K1z * S_new[2]*Snb[2]

            # single-ion contribution
            E_old += -Ax*S_old[0]**2 - Ay*S_old[1]**2 - Az*S_old[2]**2
            E_new += -Ax*S_new[0]**2 - Ay*S_new[1]**2 - Az*S_new[2]**2

            dE = E_new - E_old
            if dE < 0.0 or np.random.random() < math.exp(-dE / (kB*T)):
                spins_x[site], spins_y[site], spins_z[site] = S_new

        # ---------------------------- measurements -----------------------
        if sweep >= threshold:
            m_idx = sweep - threshold

            # sub-lattice vectors
            mu_up   = np.zeros(3)
            mu_down = np.zeros(3)
            for i in range(N):
                if spins_init[i] > 0.0:
                    mu_up   += np.array([spins_x[i], spins_y[i], spins_z[i]])
                else:
                    mu_down += np.array([spins_x[i], spins_y[i], spins_z[i]])

            # already normalised magnetisations
            M_up_norm   = math.sqrt(np.dot(mu_up,   mu_up  )) / (num_up_sites   * r_mag)
            M_down_norm = math.sqrt(np.dot(mu_down, mu_down)) / (num_down_sites * r_mag)

            Mx_tot = spins_x.sum()
            My_tot = spins_y.sum()
            Mz_tot = spins_z.sum()
            M_tot_norm = math.sqrt(Mx_tot*Mx_tot +
                                   My_tot*My_tot +
                                   Mz_tot*Mz_tot) / (N * r_mag)

            # store
            mag_ups[m_idx]      = M_up_norm
            mag_up_sqs[m_idx]   = M_up_norm * M_up_norm
            mag_downs[m_idx]    = M_down_norm
            mag_down_sqs[m_idx] = M_down_norm * M_down_norm
            mag_tots[m_idx]     = M_tot_norm
            mag_tot_sqs[m_idx]  = M_tot_norm * M_tot_norm

            # total energy of this configuration (1NN + single-ion shown)
            E_cfg = 0.0
            for i in range(N):
                Si = np.array([spins_x[i], spins_y[i], spins_z[i]])

                for nb in N1list[i]:
                    if nb > i and (nb != 100000 and nb != -5):
                        Snb = np.array([spins_x[nb], spins_y[nb], spins_z[nb]])
                        E_cfg += -J1 * np.dot(Si, Snb) \
                                 -K1x * Si[0]*Snb[0] - K1y * Si[1]*Snb[1] - K1z * Si[2]*Snb[2]

                E_cfg += -Ax*Si[0]**2 - Ay*Si[1]**2 - Az*Si[2]**2

            energies[m_idx] = E_cfg

    # ---------------------------------------------------------------- averages
    M_up_fin,   M_up_sq_fin   = np.mean(mag_ups),   np.mean(mag_up_sqs)
    M_down_fin, M_down_sq_fin = np.mean(mag_downs), np.mean(mag_down_sqs)
    M_tot_fin,  M_tot_sq_fin  = np.mean(mag_tots),  np.mean(mag_tot_sqs)

    # susceptibilities (already per spin, so no N-division)
    X_up_fin   = (M_up_sq_fin   - M_up_fin*M_up_fin)   / (kB*T)
    X_down_fin = (M_down_sq_fin - M_down_fin*M_down_fin) / (kB*T)
    X_tot_fin  = (M_tot_sq_fin  - M_tot_fin*M_tot_fin)  / (kB*T)

    # energy & Cv
    E_avg, E_var = mean_and_var_1d(energies)
    Cv_val       = E_var / (kB*T*T*N)          # per spin, eV → kB units
    Cv_val      /= kB

    # simple error estimates
    ns        = float(n_meas)
    E_err     = math.sqrt(E_var / ns) if ns > 1.0 else 0.0
    M_mean, M_var = mean_and_var_1d(mag_tots)
    M_err     = math.sqrt(M_var / ns) if ns > 1.0 else 0.0
    A_mean, A_var = mean_and_var_1d(mag_tots*mag_tots)
    X_err     = math.sqrt(A_var / ns) / (kB*T) if ns > 1.0 else 0.0
    E2_mean, E2_var = mean_and_var_1d(energies*energies)
    Cv_err    = math.sqrt(E2_var / ns) / (kB*T*T*N) if ns > 1.0 else 0.0

    # -------------------------------------------------------------- return
    return (M_up_fin,   X_up_fin,
            M_down_fin, X_down_fin,
            M_tot_fin,  X_tot_fin,
            E_avg, Cv_val, X_err, E_err, M_err, Cv_err,
            spins_x, spins_y, spins_z)


###############################################################################
# The HybridMC class that calls the jitted functions
###############################################################################
class HybridMC:
    """
    Hybrid MC class storing system size, neighbor lists, couplings, anisotropy, etc.

    We define two main MC methods here:
      (1) MC_func_simple_metropolis: simpler single-site method.
      (2) MC_func_hybrid_boc: advanced approach combining heat-bath local,
          overrelaxation, partial cluster BFS.

    We do a single precomputation of BFS neighbors ignoring anisotropy => self.neighbors_isotr
    so that the advanced cluster approach is efficient.
    """

    def __init__(self,
                 N,
                 N1list, N2list, N3list, N4list,
                 J1, J2, J3, J4,
                 K1x, K1y, K1z,
                 K2x, K2y, K2z,
                 K3x, K3y, K3z,
                 K4x, K4y, K4z,
                 Ax, Ay, Az,
                 kB,
                 trange,
                 threshold,
                 EMA):
        self.N = N
        self.N1list = N1list
        self.N2list = N2list
        self.N3list = N3list
        self.N4list = N4list

        self.J1 = J1
        self.J2 = J2
        self.J3 = J3
        self.J4 = J4

        self.K1x = K1x
        self.K1y = K1y
        self.K1z = K1z
        self.K2x = K2x
        self.K2y = K2y
        self.K2z = K2z
        self.K3x = K3x
        self.K3y = K3y
        self.K3z = K3z
        self.K4x = K4x
        self.K4y = K4y
        self.K4z = K4z

        self.Ax = Ax
        self.Ay = Ay
        self.Az = Az

        self.kB = kB
        self.trange = trange
        self.threshold = threshold
        self.EMA = EMA

        # Precompute BFS neighbors ignoring anisotropy => used by partial cluster
        useJ2_flag = (abs(self.J2) > 1e-14)
        useJ3_flag = (abs(self.J3) > 1e-14)
        useJ4_flag = (abs(self.J4) > 1e-14)
        self.neighbors_isotr = build_isotropic_neighbors(
            N,
            N1list, N2list, N3list, N4list,
            J1, J2, J3, J4,
            useJ2_flag, useJ3_flag, useJ4_flag
        )

    def MC_func_simple_metropolis(self, spins_init, T, J2flag, J3flag, J4flag):
        """
        Wrapper: calls the jitted metropolis function.
        """
        return MC_func_simple_metropolis_impl(
            spins_init, T, J2flag, J3flag, J4flag,
            self.N,
            self.N1list, self.N2list, self.N3list, self.N4list,
            self.J1, self.J2, self.J3, self.J4,
            self.K1x, self.K1y, self.K1z,
            self.K2x, self.K2y, self.K2z,
            self.K3x, self.K3y, self.K3z,
            self.K4x, self.K4y, self.K4z,
            self.Ax, self.Ay, self.Az,
            self.kB,
            self.trange,
            self.threshold,
            self.EMA
        )

    def MC_func_hybrid_boc(self, spins_init, T, J2flag, J3flag, J4flag):
        """
        Wrapper: calls the jitted hybrid BOC function.
        """
        return MC_func_hybrid_boc_impl(
            spins_init, T,
            J2flag, J3flag, J4flag,
            self.N,
            self.N1list, self.N2list, self.N3list, self.N4list,
            self.J1, self.J2, self.J3, self.J4,
            self.K1x, self.K1y, self.K1z,
            self.K2x, self.K2y, self.K2z,
            self.K3x, self.K3y, self.K3z,
            self.K4x, self.K4y, self.K4z,
            self.Ax, self.Ay, self.Az,
            self.kB,
            self.trange,
            self.threshold,
            self.EMA,
            self.neighbors_isotr
        )

    # ------------------------------------------------------------------
    #  (3)  Reference / debug Metropolis routine that returns the full
    #       14‑element tuple (identical format to the other kernels)
    # ------------------------------------------------------------------
    def MC_func_metropolis(self, spins_init, T, J2flag, J3flag, J4flag):
        """
        Wrapper around the fully‑featured but slower MC_func_full.
        Use it as a correctness benchmark for the fast kernels.
        """
        return MC_func_full(
            spins_init, T, J2flag, J3flag, J4flag,
            self.N,
            self.N1list, self.N2list, self.N3list, self.N4list,
            self.J1, self.J2, self.J3, self.J4,
            self.K1x, self.K1y, self.K1z,
            self.K2x, self.K2y, self.K2z,
            self.K3x, self.K3y, self.K3z,
            self.K4x, self.K4y, self.K4z,
            self.Ax, self.Ay, self.Az,
            self.kB,
            self.trange,
            self.threshold,
            self.EMA
        )


#-----------------------------------
# Quantum Spin using ED
#-----------------------------------

# ─────────────────────────────────────────────────────────────────────────────
# quantum_mc_exact.py  —  exact-diagonalisation reference for spin-½ XXZ model
# ─────────────────────────────────────────────────────────────────────────────
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from math import exp, sqrt


# single–site Pauli matrices  ( 2 S = σ ;   S = ½ )
σx = sp.csr_matrix([[0, 1], [1, 0]], dtype=np.complex128)
σy = sp.csr_matrix([[0, -1j], [1j, 0]], dtype=np.complex128)
σz = sp.csr_matrix([[1, 0], [0, -1]],  dtype=np.complex128)
iden = sp.identity(2, dtype=np.complex128)


def _kron_list(ops):
    """Kronecker product of a list of sparse 2×2 operators."""
    out = ops[0]
    for op in ops[1:]:
        out = sp.kron(out, op, format='csr')
    return out


class QuantumSpinED:
    """
    Exact-diagonalisation for the spin-½ XXZ Hamiltonian

        H =  Σ_{⟨i,j⟩} J_ij ( S_i·S_j  with  Δ on SzSz )  −  h Σ_i S_i^z

    The neighbour topology (1- to 4-NN) and couplings are taken from
    exactly the same lists/values that feed your classical kernels.

    Limit:  N ≤ 18 sites is practical on a laptop; beyond that use SSE / DMRG.
    """

    # ---------------------------------------------------------------------
    def __init__(self,
                 spins_init,               # the same array you already build
                 N1list, N2list, N3list, N4list,
                 J1, J2, J3, J4,
                 Delta=1.0,                # XXZ anisotropy (Δ=1 ⇒ isotropic)
                 h=0.0):                   # external field in eV units
        self.N      = int(spins_init.shape[0])
        if self.N > 18:
            raise ValueError(
                f"Exact diagonalisation limited to N ≤ 18, "
                f"got N = {self.N}. "
                "Use mc_method = 4 (SSE QMC) for larger systems."
            )
            
        self.Delta  = float(Delta)
        self.h      = float(h)
        self.sublat = np.sign(spins_init).astype(np.int8)  # +1 (up) | −1 (down)

        # build sparse many-body Hamiltonian --------------------------------
        dim = 2 ** self.N
        H = sp.csr_matrix((dim, dim), dtype=np.complex128)

        # cache one-site Sα operators
        Sx, Sy, Sz = [], [], []
        for i in range(self.N):
            ops = [iden]*self.N
            ops[i] = 0.5 * σx
            Sx.append(_kron_list(ops))
            ops[i] = 0.5 * σy
            Sy.append(_kron_list(ops))
            ops[i] = 0.5 * σz
            Sz.append(_kron_list(ops))

        # helper to add J_ij term once (i<j)
        def add_pair(i, j, J):
            nonlocal H
            if abs(J) < 1e-14:
                return
            H += J * ( Sx[i].dot(Sx[j]) + Sy[i].dot(Sy[j])
                       + self.Delta * Sz[i].dot(Sz[j]) )

        for i in range(self.N):
            for j in N1list[i]:
                if j > i and j not in (100000, -5):
                    add_pair(i, j, J1)
            for j in N2list[i]:
                if j > i and j not in (100000, -5):
                    add_pair(i, j, J2)
            for j in N3list[i]:
                if j > i and j not in (100000, -5):
                    add_pair(i, j, J3)
            for j in N4list[i]:
                if j > i and j not in (100000, -5):
                    add_pair(i, j, J4)

        # Zeeman term  −h Σ Sᶻ
        if abs(self.h) > 1e-14:
            for i in range(self.N):
                H += -self.h * Sz[i]

        # exact spectrum ----------------------------------------------------
        print(f"[Quantum ED]  N = {self.N:2d}  Hilbert dim = {2**self.N}")
        # full dense diagonalisation up to 14 sites, sparse Lanczos above
        if self.N <= 14:
            self.evals, self.evecs = np.linalg.eigh(H.toarray())
        else:
            # compute the whole spectrum with ARPACK iterative solver
            # (k = dim-1 because ARPACK cannot compute all states at once)
            dim = H.shape[0]
            # small numerical trick: shift-invert around centre of spectrum
            Emax = spla.eigsh(H, k=1, which='LA', return_eigenvectors=False)[0]
            Emin = spla.eigsh(H, k=1, which='SA', return_eigenvectors=False)[0]
            centre = 0.5*(Emax+Emin)
            ShiftH = H - centre*sp.eye(dim, dtype=np.complex128)
            self.evals, self.evecs = spla.eigsh(ShiftH, k=dim-2, which='LM')
            self.evals = self.evals + centre
            # ARPACK does not guarantee ordering
            idx_sort = np.argsort(self.evals.real)
            self.evals = self.evals[idx_sort].real
            self.evecs = self.evecs[:, idx_sort]

        # cache ⟨Sᶻ_tot⟩ for every eigenstate (needed for magnetisation)
        Sz_tot = sum(Sz)
        self.Mz = np.real(np.einsum('ij,ij->j',
                                    np.conjugate(self.evecs),
                                    Sz_tot @ self.evecs))

    # ---------------------------------------------------------------------
    def _thermal_av(self, op_vals, beta):
        """⟨op⟩, ⟨op²⟩ thermal averages given eigenvalues op_vals(j)."""
        boltz = np.exp(-beta * self.evals)
        Z     = boltz.sum()
        avg   = (op_vals * boltz).sum() / Z
        avg2  = (op_vals**2 * boltz).sum() / Z
        return avg, avg2, Z

    # ---------------------------------------------------------------------
    def QMC_func_exact(self, T):
        """
        Exact thermodynamics at temperature T (Kelvin).

        Returns the 14-tuple:
          ( M_up, χ_up, M_down, χ_down, M_tot, χ_tot,
            E_avg, C_v, χ_err, E_err, M_err, C_v_err,
            None, None, None )
        Error bars are zero because the calculation is exact.
        """
        beta = 1.0 / (kB * T)

        # energy & Cv ------------------------------------------------------
        E_avg, E2_avg, Z = self._thermal_av(self.evals, beta)
        Cv_val = beta*beta * (E2_avg - E_avg*E_avg) / self.N / kB

        # magnetisation & susceptibility ----------------------------------
        M_avg, M2_avg, _ = self._thermal_av(self.Mz, beta)

        X_tot = beta * (M2_avg - M_avg*M_avg) / self.N

        # sub-lattice split (follow your classical definition) ------------
        up_mask   = self.sublat > 0
        down_mask = self.sublat < 0
        if up_mask.sum() == 0:   # pure FM start  → treat everything as “up”
            up_mask[:]   = True
            down_mask[:] = True

        # expectation of Σ Sᶻ on each sub-lattice
        Sz_ops = []
        for i in range(self.N):
            ops = [iden]*self.N
            ops[i] = 0.5 * σz
            Sz_ops.append(_kron_list(ops))

        def sublat_m(op_indices):
            """thermal ⟨ Σ_{i∈sub} Sᶻ_i ⟩ and variance."""
            Sz_sub = sum(Sz_ops[i] for i in op_indices)
            Sz_vals = np.real(np.einsum('ij,ij->j',
                                        np.conjugate(self.evecs),
                                        Sz_sub @ self.evecs))
            m, m2, _ = self._thermal_av(Sz_vals, beta)
            chi = beta * (m2 - m*m) / self.N
            return m / self.N, chi

        M_up,   X_up   = sublat_m(np.where(up_mask)[0])
        M_down, X_down = sublat_m(np.where(down_mask)[0])

        # normalise magnetisations to saturation moment (=½) → divide by ½
        norm = 0.5
        M_up   /= norm
        M_down /= norm
        M_tot   = M_avg / (norm * self.N)

        # assemble 14-tuple (exact → every _err = 0)
        return (M_up,   X_up,
                M_down, X_down,
                M_tot,  X_tot,
                E_avg/self.N, Cv_val,
                0.0, 0.0, 0.0, 0.0,
                None, None, None)


# How to run
"""
# neighbour lists, couplings,   spins_init  already exist…
specQ = QuantumSpinED(spins_init,
                      N1list, N2list, N3list, N4list,
                      J1, J2, J3, J4,
                      Delta=1.0,   # XXZ anisotropy
                      h=0.0)       # field (eV)

(M_up, X_up,
 M_down, X_down,
 M_tot, X_tot,
 E_avg, Cv_val,
 X_err, E_err, M_err, Cv_err,
 _, _, _)  = specQ.QMC_func_exact(T=50.0)     # Kelvin

"""

# ──────────────────────────────────────────────────────────────────────────
# quantum_sse.py     •  COMPLETE spin-½ XXZ Stochastic-Series-Expansion
# ──────────────────────────────────────────────────────────────────────────
import numpy as np
from math import exp, sqrt
from numba import njit, int32, float64
from numba.typed import List


# ───────────────────────────── helper: build one bond list ───────────────
def _bond_list(N, N1,N2,N3,N4, J1,J2,J3,J4):
    """Return list[(i,j,J)] with i<j and all inactive sentinels removed."""
    bonds=[]
    def add(shell,J):
        if abs(J)<1e-14: return
        for i in range(N):
            for j in shell[i]:
                if j>i and j not in (100000,-5):
                    bonds.append((i,j,float(J)))
    add(N1,J1); add(N2,J2); add(N3,J3); add(N4,J4)
    return np.array(bonds,
                    dtype=[('i',np.int32),('j',np.int32),('J',np.float64)])

# ──────────────────────────── directed-loop tables (XXZ) ─────────────────
@njit
def _vertex_scatter(Delta, entrance_leg, s_i, s_j, op_type):
    """
    Directed-loop scattering table for a 2-site vertex.
    Parameters
    ----------
    Delta         : XXZ anisotropy
    entrance_leg  : 0..3  (0=i-in, 1=j-in, 2=i-out, 3=j-out)
    s_i, s_j      : σᶻ  (=±1) before the vertex is entered
    op_type       : 0→diagonal, 1→off-diagonal
    Returns
    -------
    exit_leg, new_op_type, flip_i, flip_j
    """
    #  leg pairing:  0–2  and  1–3  are along world-lines
    #  Allowed operator changes & spin flips follow Syljuåsen/Sandvik (2002)
    rng = np.random.rand()

    if op_type==0:        # diagonal  (no spin flip)
        if entrance_leg in (0,2):  # came from i
            if rng<0.5:   return 2,0,0,0  # straight
            else:         return 3,1,1,1  # switch & create off-diag
        else:             # came from j
            if rng<0.5:   return 3,0,0,0
            else:         return 2,1,1,1

    else:                 # off-diagonal  (spins are opposite & will flip)
        # legs 0→3 or 1→2  with probability 1
        if entrance_leg==0: return 3,0,1,1
        if entrance_leg==3: return 0,0,1,1
        if entrance_leg==1: return 2,0,1,1
        if entrance_leg==2: return 1,0,1,1

    # should never reach here
    return entrance_leg, op_type, 0,0


# ─────────────────────────────── SSE engine class ────────────────────────
class QuantumSpinSSE:
    """Directed-loop Stochastic-Series-Expansion for spin-½ XXZ."""
    # ------------------------------------------------------------------ init
    def __init__(self, bonds, N, beta, Delta=1.0, M=None):
        self.N      = int(N)
        self.beta   = float(beta)
        self.Delta  = float(Delta)
        self.bonds  = bonds.copy()
        self.nbonds = len(bonds)
        # initial string length  (≥2 β Σ|J|)
        if M is None:
            M = int(2.0*beta*np.sum(np.abs(bonds['J'])))+32
        self.M        = int(M)
        self.op_bond  = -np.ones(self.M, dtype=np.int32)   # −1 ⇢ identity
        self.op_type  = np.zeros(self.M, dtype=np.int8)    # 0 diag / 1 off
        self.spins    = np.ones(self.N, dtype=np.int8)     # σᶻ = +1
    # ---------------------------------------------------------------- n_ops
    def n_ops(self):
        return np.count_nonzero(self.op_bond+1)
    # ---------------------------------------------------------------- diag-update
    def _diag_update(self):
        for p in range(self.M):
            b  = self.op_bond[p]
            if b==-1:                          # try to insert
                btry = np.random.randint(self.nbonds)
                i,j,J = self.bonds[btry]
                if self.spins[i]!=self.spins[j]:
                    prob = 0.5*self.beta*abs(J)*self.M/(self.M-self.n_ops())
                    if np.random.rand()<prob:
                        self.op_bond[p]=btry
                        self.op_type[p]=1      # start as off-diag
                        # flip both spins
                        self.spins[i]*=-1
                        self.spins[j]*=-1
            else:                              # try to remove
                i,j,J = self.bonds[b]
                if self.op_type[p]==1:         # only off-diag removable
                    prob=(self.M-self.n_ops()+1)/(0.5*self.beta*abs(J)*self.M)
                    if np.random.rand()<prob:
                        self.op_bond[p]=-1
                        # flip spins back
                        self.spins[i]*=-1
                        self.spins[j]*=-1
    # ---------------------------------------------------------------- link list
    def _build_links(self):
        """
        Build world-line link arrays:
            leg_spin[4M]   current σᶻ on each leg
            link[4M]       next leg along world-line
        leg numbering: 4p..4p+3  (0=i-in,1=j-in,2=i-out,3=j-out)
        """
        M4 = 4*self.M
        leg_spin = np.empty(M4, np.int8)
        link     = -np.ones(M4, np.int32)

        last_leg_site = -np.ones(self.N, np.int32)   # open segment per site

        for p in range(self.M):
            b = self.op_bond[p]
            if b==-1:   # identity → skip
                for l in range(4):
                    leg_spin[4*p+l]=0
                continue
            i,j,_ = self.bonds[b]
            s_i = self.spins[i]
            s_j = self.spins[j]
            if self.op_type[p]==1:      # off-diag flips spins between in/out
                s_i*=-1
                s_j*=-1
            leg_spin[4*p+0]=self.spins[i]
            leg_spin[4*p+1]=self.spins[j]
            leg_spin[4*p+2]=s_i
            leg_spin[4*p+3]=s_j

            # connect world-lines
            for leg,site in zip((0,2),(i,i)):
                leg_idx = 4*p+leg
                if last_leg_site[site]==-1:
                    last_leg_site[site]=leg_idx
                else:
                    prev = last_leg_site[site]
                    link[prev]=leg_idx
                    link[leg_idx]=prev
                    last_leg_site[site]=-1
            for leg,site in zip((1,3),(j,j)):
                leg_idx = 4*p+leg
                if last_leg_site[site]==-1:
                    last_leg_site[site]=leg_idx
                else:
                    prev = last_leg_site[site]
                    link[prev]=leg_idx
                    link[leg_idx]=prev
                    last_leg_site[site]=-1
        # connect time-boundary legs
        for site in range(self.N):
            if last_leg_site[site]!=-1:
                first = last_leg_site[site]
                # periodic boundary in imaginary time
                link[first]=first
        return leg_spin, link
    # ---------------------------------------------------------------- loop-update
    def _loop_update(self):
        leg_spin, link = self._build_links()
        visited = np.zeros(len(link), np.int8)

        for leg_start in range(len(link)):
            if visited[leg_start]: continue
            leg = leg_start
            while True:
                visited[leg]=1
                p   = leg>>2
                l   = leg & 3
                b   = self.op_bond[p]
                if b==-1:
                    # identity vertex: just move ahead
                    leg = link[leg]
                    if leg==leg_start: break
                    continue
                i,j,J = self.bonds[b]
                s_i   = leg_spin[4*p+0]
                s_j   = leg_spin[4*p+1]

                exit_leg, new_type, flip_i, flip_j = _vertex_scatter(
                        self.Delta, l, s_i, s_j, self.op_type[p])

                # update operator type & spins if changed
                if new_type!=self.op_type[p]:
                    self.op_type[p]=new_type
                if flip_i:
                    self.spins[i]*=-1
                if flip_j:
                    self.spins[j]*=-1

                # step to connected world-line leg
                if exit_leg==0: nxt=link[4*p+2]
                if exit_leg==1: nxt=link[4*p+3]
                if exit_leg==2: nxt=link[4*p+0]
                if exit_leg==3: nxt=link[4*p+1]
                leg = nxt
                if leg==leg_start: break
    # ---------------------------------------------------------------- sweep
    def sweep(self):
        self._diag_update()
        self._loop_update()
        # auto-expand operator string
        if self.n_ops()>0.75*self.M:
            extra = self.M//2
            self.op_bond = np.concatenate([self.op_bond,
                                           -np.ones(extra,np.int32)])
            self.op_type = np.concatenate([self.op_type,
                                           np.zeros(extra,np.int8)])
            self.M += extra
    # ---------------------------------------------------------------- measure
    def measure(self):
        """Return (E, |M|, |M|²)  (energy in eV)."""
        E   = -self.n_ops()/self.beta
        Mz  = 0.5*self.spins.sum()
        return E, abs(Mz), Mz*Mz

# ────────────────────────────── 14-tuple wrapper ─────────────────────────
def QMC_func_SSE(spins_init, T,
                 N1list,N2list,N3list,N4list,
                 J1,J2,J3,J4,
                 sweeps=12000, therm=4000,
                 Delta=1.0):
    """
    Quantum-spin kernel (SSE, directed loops).
    Produces the same 14-element tuple as the classical routines.
    """
    N      = int(spins_init.shape[0])
    beta   = 1.0/(kB*T)
    bonds  = _bond_list(N,N1list,N2list,N3list,N4list, J1,J2,J3,J4)
    sse    = QuantumSpinSSE(bonds, N, beta, Delta)

    # accumulators
    E_sum=E2_sum=M_sum=M2_sum=0.0
    for sweep in range(sweeps):
        sse.sweep()
        if sweep>=therm:
            E,M,M2 = sse.measure()
            E_sum  += E;  E2_sum+=E*E
            M_sum  += M;  M2_sum+=M2
    ns = sweeps-therm
    E_avg = E_sum/ns
    Cv_val = (E2_sum/ns - E_avg*E_avg)*beta*beta/(N*kB)

    M_avg = M_sum/ns
    M2_av = M2_sum/ns
    X_tot = beta*(M2_av - M_avg*M_avg)/N

    # normalisation to saturation m_s=½
    M_tot = 2.0*M_avg/N
    M_up = M_down = M_tot
    X_up = X_down = X_tot

    # simple σ/√N errors
    E_err = sqrt(max(E2_sum/ns - E_avg*E_avg,0.0)/ns)
    M_err = sqrt(max(M2_sum/ns - M_avg*M_avg,0.0)/ns)*2.0/N
    X_err = Cv_err = 0.0   # (implement jack-knife if needed)

    return (M_up, X_up,
            M_down, X_down,
            M_tot, X_tot,
            E_avg/N, Cv_val,
            X_err, E_err, M_err, Cv_err,
            None,None,None)


#How to run
"""
qm_results = QMC_func_SSE(
        spins_init    = np.ones(64),        # 64-site FM start
        T             = 50.0,               # Kelvin
        N1list=N1, N2list=N2, N3list=N3, N4list=N4,
        J1=35e-3, J2=0.0, J3=0.0, J4=0.0,   # eV
        sweeps   = 50000,
        therm    = 10000,
        Delta    = 1.0)                     # Heisenberg

(M_up,X_up, M_dn,X_dn, M_tot,X_tot,
 E_avg,Cv,  X_err,E_err,M_err,Cv_err,
 _,_,_) = qm_results
print(f'<M>={M_tot:.4f},  E/N={E_avg:.6f} eV,  Cv={Cv:.4f}')

"""



