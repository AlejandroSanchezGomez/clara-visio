# ============================================================
# Date: 2025.09.08
# Description:
# Define the input layer of the neural retina. This module will
# build upon hexagonal patches to populate rods and cones in
# region-specific distributions (foveola, fovea, parafovea, etc.)
# and serve as the entry point for visual information.
# ============================================================

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from Utils import hexagonal_layer

from typing import Dict

from typing import Dict

def photoreceptor_profile(ecc_um: float) -> Dict[str, Dict[str, float]]:
    """
    Return normalized probabilities of photoreceptor types
    at a given eccentricity (µm), including cone subtypes.

    Subregions (Curcio et al. 1990):
        - Foveolar pit (0–100 µm): cone-only, virtually no S cones
        - Foveolar slope (100–350 µm): cones dominate, few S
        - Fovea (350–1500 µm): high cones, rods begin
        - Parafovea (1500–2750 µm): rods rise, cone density falls
        - Perifovea (2750–5500 µm): rod-dominated
        - Peripheral (>5500 µm): sparse cones, rods stable
    """

    # --- Base cone/rod densities (cells/mm²) ---
    if ecc_um < 100:          # Foveolar pit
        cone_density, rod_density = 200_000, 0
        lms_ratio = (0.50, 0.50, 0.00)  # no S
    elif ecc_um < 350:        # Foveolar slope
        cone_density, rod_density = 180_000, 0
        lms_ratio = (0.48, 0.48, 0.04)  # S minimal
    elif ecc_um < 1500:       # Fovea
        cone_density, rod_density = 100_000, 20_000
        lms_ratio = (0.50, 0.45, 0.05)
    elif ecc_um < 2750:       # Parafovea
        cone_density, rod_density = 40_000, 100_000
        lms_ratio = (0.50, 0.43, 0.07)
    elif ecc_um < 5500:       # Perifovea
        cone_density, rod_density = 15_000, 150_000
        lms_ratio = (0.50, 0.42, 0.08)
    else:                     # Peripheral retina
        cone_density, rod_density = 5_000, 120_000
        lms_ratio = (0.48, 0.44, 0.08)

    # --- Normalize cone vs rod ---
    total = cone_density + rod_density
    if total == 0:
        return {"cone": 0.0, "rod": 0.0, "cone_types": {"L": 0.0, "M": 0.0, "S": 0.0}}

    p_cone = cone_density / total
    p_rod = rod_density / total

    # --- Cone subtype split ---
    L, M, S = lms_ratio
    s = max(1e-12, L + M + S)
    cone_types = {
        "L": p_cone * (L / s),
        "M": p_cone * (M / s),
        "S": p_cone * (S / s),
    }

    return {
        "cone": p_cone,
        "rod": p_rod,
        "cone_types": cone_types,
    }

