# ============================================================
# Project: CLARA_VISIO
# File: hexagonal_layer.py
# Date: 2025.08.27
# ------------------------------------------------------------
# Description:
# Generate circular hexagonal lattices (retinal patches) as
# dataclass objects, preserving parameters and coordinates.
# Includes plotting utilities for visualization.
# ============================================================

from __future__ import annotations
import numpy as np
from typing import Optional, Tuple
from hexalattice.hexalattice import create_hex_grid
import matplotlib.pyplot as plt
from dataclasses import dataclass, field


@dataclass
class HexPatch:
    """Container for a circular hexagonal retinal patch."""

    radius_um: float
    pitch_um: float
    jitter_um: float = 0.0
    seed: Optional[int] = None
    center: Tuple[float, float] = (0.0, 0.0)
    coords: np.ndarray = field(default_factory=lambda: np.zeros((0, 2)))

    def plot(self, show: bool = True):
        """Plot the hex patch with boundary circle."""
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.scatter(self.coords[:, 0], self.coords[:, 1], s=10, c="royalblue", alpha=0.8)
        circ = plt.Circle(self.center, self.radius_um, color="gray", fill=False, linestyle="--")
        ax.add_patch(circ)
        ax.set_aspect("equal")
        ax.set_title(f"Hex Patch (r={self.radius_um} µm, pitch={self.pitch_um} µm, n={len(self.coords)})")
        ax.set_xlabel("x (µm)")
        ax.set_ylabel("y (µm)")
        if show:
            plt.show()
        else:
            return fig, ax


def make_hex_circular_patch(
    radius_um: float,
    pitch_um: float,
    jitter_um: float = 0.0,
    seed: Optional[int] = None,
    center: Tuple[float, float] = (0.0, 0.0),
) -> HexPatch:
    """
    Factory function: generate a circular hexagonal patch as a HexPatch dataclass.
    """
    if radius_um <= 0:
        return HexPatch(radius_um, pitch_um, jitter_um, seed, center, np.zeros((0, 2)))

    width_um = height_um = 2 * radius_um
    nx = int(np.ceil(width_um / pitch_um)) + 2
    ny = int(np.ceil(height_um / (pitch_um * np.sqrt(3) / 2))) + 2

    coords, _ = create_hex_grid(nx=nx, ny=ny, min_diam=pitch_um, do_plot=False)
    coords = np.asarray(coords, dtype=float)

    coords[:, 0] -= coords[:, 0].mean()
    coords[:, 1] -= coords[:, 1].mean()

    r2 = radius_um**2
    mask = coords[:, 0]**2 + coords[:, 1]**2 <= r2
    coords = coords[mask]

    if jitter_um > 0:
        rng = np.random.default_rng(seed)
        coords += rng.normal(0.0, jitter_um, size=coords.shape)

    coords[:, 0] += center[0]
    coords[:, 1] += center[1]

    r = np.sqrt(coords[:, 0]**2 + coords[:, 1]**2)
    theta = np.arctan2(coords[:, 1], coords[:, 0])
    order = np.lexsort((r, theta))
    coords = coords[order]

    return HexPatch(radius_um, pitch_um, jitter_um, seed, center, coords)
