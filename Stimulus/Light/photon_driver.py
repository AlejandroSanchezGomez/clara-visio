# ============================================================
# Project: CLARA_VISIO
# File: photon_drive.py
# Date: 2025.08.27
# ------------------------------------------------------------
# Description:
# Utilities to convert Photon objects into per-receptor light
# drive L(t, i) for cones/rods (normalized 0..1).
# ============================================================

from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import numpy as np
from photon import Photon

# If cones.py lives next to this file:
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from Cells.Retina import cones

def _time_bin_index(t: float, t0: float, dt: float, T: float) -> Optional[int]:
    """Map a photon time (s) to a frame index; returns None if out of window."""
    if t is None:
        return None
    if t < t0 or t >= t0 + T:
        return None
    return int((t - t0) // dt)

def _gaussian_psf_weights(px_um: float, py_um: float,
                          rx_um: np.ndarray, ry_um: np.ndarray,
                          sigma_um: float) -> np.ndarray:
    """
    Compute spatial weights from photon position (px,py) to receptor positions (rx,ry)
    using a circular Gaussian PSF with std = sigma_um.
    Returns shape (N,) weights (unnormalized).
    """
    if sigma_um <= 0:
        # nearest-neighbor if sigma is zero/neg
        d2 = (rx_um - px_um)**2 + (ry_um - py_um)**2
        idx = np.argmin(d2)
        w = np.zeros_like(rx_um)
        w[idx] = 1.0
        return w

    dx = rx_um - px_um
    dy = ry_um - py_um
    r2 = dx*dx + dy*dy
    # Unnormalized Gaussian; we’ll normalize per photon so sum(weights)=1
    w = np.exp(-0.5 * r2 / (sigma_um**2))
    s = w.sum()
    if s > 0:
        w /= s
    return w

def build_L_series_for_cones(
    photons: List[Photon],
    cone_positions: Dict[str, np.ndarray],
    *,
    T: float,
    dt: float,
    t0: float = 0.0,
    sigma_um: float = 10.0,
    # normalization cap: number of effective photons for L=1.0 at the peak cone
    photons_per_L1: float = 50.0,
) -> Dict[str, np.ndarray]:
    """
    Build time series L(t, i) for S/M/L cone groups from a list of photons.

    Parameters
    ----------
    photons : list[Photon]
    cone_positions : {'S': array(Ns,2), 'M': array(Nm,2), 'L': array(Nl,2)}
        Positions in micrometers for each cone type (can be empty arrays).
    T : float
        Total duration in seconds.
    dt : float
        Timestep in seconds (simulation step to match Brian2 defaultclock.dt).
    t0 : float
        Start time for the window (s).
    sigma_um : float
        Spatial spread (PSF sigma) for a photon → cone mapping.
    photons_per_L1 : float
        How many *effective* photons (after spectral & spatial weighting) make L≈1
        for a single cone within one dt.

    Returns
    -------
    {'S': Ls, 'M': Lm, 'L': Ll} where each L* has shape (n_steps, N_type) in [0..1].
    """
    n_steps = int(np.ceil(T / dt))

    L_series: Dict[str, np.ndarray] = {}
    for tkey, pos in cone_positions.items():
        N = 0 if pos is None else (0 if pos.size == 0 else pos.shape[0])
        L_series[tkey] = np.zeros((n_steps, N), dtype=float)

    # Pre-split positions for speed
    S_pos = cone_positions.get('S', np.zeros((0, 2)))
    M_pos = cone_positions.get('M', np.zeros((0, 2)))
    L_pos = cone_positions.get('L', np.zeros((0, 2)))

    # Accumulate photons
    for ph in photons:
        # Time bin
        k = _time_bin_index(ph.t if ph.t is not None else t0, t0, dt, T)
        if k is None:
            continue

        # Missing spatial coords? skip (or you could broadcast uniformly)
        if ph.x is None or ph.y is None:
            continue

        px = float(ph.x)
        py = float(ph.y)

        # Spectral weights per cone type
        wS = cone_sensitivity_nm(ph.lambda_nm, 'S')
        wM = cone_sensitivity_nm(ph.lambda_nm, 'M')
        wL = cone_sensitivity_nm(ph.lambda_nm, 'L')

        # Distribute spatially within each cone map
        if S_pos.size:
            w_sp = _gaussian_psf_weights(px, py, S_pos[:,0], S_pos[:,1], sigma_um)
            if wS > 0:
                L_series['S'][k] += (wS * w_sp)
        if M_pos.size:
            w_sp = _gaussian_psf_weights(px, py, M_pos[:,0], M_pos[:,1], sigma_um)
            if wM > 0:
                L_series['M'][k] += (wM * w_sp)
        if L_pos.size:
            w_sp = _gaussian_psf_weights(px, py, L_pos[:,0], L_pos[:,1], sigma_um)
            if wL > 0:
                L_series['L'][k] += (wL * w_sp)

    # Normalize to [0..1] using photons_per_L1 per dt-bin
    eps = 1e-12
    for tkey in ['S', 'M', 'L']:
        if L_series[tkey].size:
            L_series[tkey] = np.clip(L_series[tkey] / (photons_per_L1 + eps), 0.0, 1.0)

    return L_series


def build_L_series_for_rods(
    photons: List[Photon],
    rod_positions: np.ndarray,
    *,
    T: float,
    dt: float,
    t0: float = 0.0,
    sigma_um: float = 10.0,
    photons_per_L1: float = 10.0,
) -> np.ndarray:
    """
    Build time series L(t, i) for rods from a list of photons.
    Same spatial binning as cones, but a lower photons_per_L1 (more sensitive).
    """
    n_steps = int(np.ceil(T / dt))
    N = 0 if rod_positions is None else (0 if rod_positions.size == 0 else rod_positions.shape[0])
    Lr = np.zeros((n_steps, N), dtype=float)

    if N == 0:
        return Lr

    rx = rod_positions[:,0]
    ry = rod_positions[:,1]

    for ph in photons:
        k = _time_bin_index(ph.t if ph.t is not None else t0, t0, dt, T)
        if k is None or ph.x is None or ph.y is None:
            continue
        px = float(ph.x); py = float(ph.y)
        w_sp = _gaussian_psf_weights(px, py, rx, ry, sigma_um)
        Lr[k] += w_sp  # no spectral split for rods

    Lr = np.clip(Lr / (photons_per_L1 + 1e-12), 0.0, 1.0)
    return Lr
