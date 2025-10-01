# ============================================================
# Project: CLARA_VISIO
# File: photon.py
# Date: 2025.08.25
# ------------------------------------------------------------
# Description:
# Photon entity class. Each photon has a wavelength (nm),
# and optionally position (x, y) and time of arrival (t).
# ============================================================

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Photon:
    """
    Photon object for CLARA_VISIO.

    Attributes:
        lambda_nm (float): Wavelength in nanometers (nm).
        x (int | None): Horizontal position on retina (optional).
        y (int | None): Vertical position on retina (optional).
        t (float | None): Time of arrival in seconds (optional).
    """
    lambda_nm: float
    x: int | None = None
    y: int | None = None
    t: float | None = None

    @property
    def energy_joule(self) -> float:
        """
        Compute photon energy in Joules: E = hc/λ
        where h = Planck’s constant, c = speed of light.

        Returns:
            Energy of the photon in Joules.
        """
        h = 6.62607015e-34  # Planck constant (J·s)
        c = 2.99792458e8    # speed of light (m/s)
        return (h * c) / (self.lambda_nm * 1e-9)

    def __str__(self) -> str:
        return f"Photon(λ={self.lambda_nm} nm, pos=({self.x},{self.y}), t={self.t})"
