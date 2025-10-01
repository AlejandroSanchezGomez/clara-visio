# ============================================================
# Project: CLARA_VISIO
# File: cones.py
# Date: 2025.08.27
# ------------------------------------------------------------
# Description:
# TODO
# ============================================================

from brian2 import *

def cone_sensitivity_nm(lambda_nm: float, cone_type: str = "L") -> float:
    """
    Very simple (Gaussian) spectral sensitivity approximation in the visible range.
    Returns a unitless sensitivity in [0..1].

    Peaks (nm):  L≈560, M≈530, S≈420.  Bandwidth is coarse; refine later if needed.
    """
    cone_type = cone_type.upper()
    mu = {"L": 560.0, "M": 530.0, "S": 420.0}.get(cone_type, 560.0)
    sigma = {"L": 40.0,  "M": 40.0,  "S": 35.0}.get(cone_type, 40.0)
    x = (lambda_nm - mu) / sigma
    return float(exp(-0.5 * x * x))


def create_cone_layer(
    N: int,
    cone_type: str = "L",
    V_dark_mV: float = -40.0,   # depolarized in darkness
    V_rest_mV: float = -65.0,   # hyperpolarized in strong light
    tau_m_ms: float = 10.0,     # membrane time constant (inner segment)
    tau_photo_ms: float = 5.0,  # phototransduction low-pass (outer segment)
    g_photo_nA: float = 0.6,    # max hyperpolarizing "conductance-like" gain
    rel_max: float = 1.0,       # max glutamate release (arbitrary units)
    V_half_mV: float = -50.0,   # half-activation for vesicle release curve
    k_rel_mV: float = 4.0,      # slope for release curve
    default_L: float = 0.0,     # initial light drive (0=dark, 1=bright)
    method: str = "euler",
) -> NeuronGroup:
    """
    Build a graded-potential cone population (no spikes).

    State variables
    --------------
    V : volt
        Membrane potential (graded). Dark baseline ~ -40 mV; hyperpolarizes with light.
    P : 1
        Phototransduction activation (0..1) — a low-pass of the instantaneous light drive L.
    L : 1
        External "light drive" (0..1). You set this over time from your stimulus pipeline.
        In a later pass, you can compute L from photons via spatial binning + spectral sensitivity.
    rel_glu : 1
        Continuous glutamate release proxy (unitless, 0..rel_max), decreases with light.

    Equations (coarse but useful)
    -----------------------------
    dP/dt = (-P + L)/tau_photo
    I_photo = -g_photo * P               (hyperpolarizing; more light → more negative current)
    dV/dt = ((V_dark - V)/tau_m) + I_photo/Cm
    rel_glu = rel_max / (1 + exp((V - V_half)/k_rel))

    Notes
    -----
    • This model is deliberately simple: one low-pass “outer segment” (P) driving a hyperpolarizing
      current into a leaky “inner segment” (V). It captures: dark depolarization, light hyperpolarization,
      fast cone kinetics, and continuous transmitter release.
    • There are no spikes here by design. Spikes begin at retinal ganglion cells.

    Returns
    -------
    cones : brian2.NeuronGroup
        A NeuronGroup with fields: V, P, L, rel_glu.
        You can connect `rel_glu` into bipolar cells later.

    Example
    -------
    >>> from brian2 import *
    >>> cones = create_cone_layer(100, cone_type="L")
    >>> Mv = StateMonitor(cones, ['V','rel_glu','L','P'], record=[0])
    >>> # Dark for 50 ms, then step to bright light for 150 ms
    >>> cones.L = 0.0
    >>> run(50*ms)
    >>> cones.L = 1.0
    >>> run(150*ms)
    >>> # Now Mv.V[0], Mv.rel_glu[0] hold your traces
    """
    # Units
    V_dark = V_dark_mV * mV
    V_rest = V_rest_mV * mV  # currently unused but kept for clarity / future clamps
    tau_m = tau_m_ms * ms
    tau_photo = tau_photo_ms * ms
    g_photo = g_photo_nA * nA
    Cm = 20 * pF  # small cone inner-segment capacitance (coarse)

    # Core graded-photoreceptor equations
    eqs = Equations('''
    dP/dt = (-P + L)/tau_photo : 1
    I_photo = -g_photo * P : amp
    dV/dt = ((V_dark - V)/tau_m) + I_photo/Cm : volt
    L : 1  # external light drive [0..1], set by you
    # continuous glutamate release (more in dark, less in light)
    rel_glu = rel_max / (1 + exp((V - V_half)/k_rel)) : 1
    V_dark : volt (constant)
    tau_m : second (constant)
    tau_photo : second (constant)
    g_photo : amp (constant)
    Cm : farad (constant)
    rel_max : 1 (constant)
    V_half : volt (constant)
    k_rel : volt (constant)
    ''')

    cones = NeuronGroup(
        N, eqs,
        method=method,
        name=f'cones_{cone_type.upper()}'
    )

    # Initialize parameters and states
    cones.V = V_dark                       # start in dark depolarized state
    cones.P = default_L                    # match low-pass to starting light
    cones.L = default_L
    cones.V_dark = V_dark
    cones.tau_m = tau_m
    cones.tau_photo = tau_photo
    cones.g_photo = g_photo
    cones.Cm = Cm
    cones.rel_max = rel_max
    cones.V_half = V_half_mV * mV
    cones.k_rel = k_rel_mV * mV

    return cones



