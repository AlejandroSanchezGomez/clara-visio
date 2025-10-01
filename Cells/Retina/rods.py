# ============================================================
# Project: CLARA_VISIO
# File: rods.py
# Date: 2025.08.27
# ------------------------------------------------------------
# Description:
# Basic graded-potential rod photoreceptor model for Brian2.
# ============================================================

from brian2 import *

def create_rod_layer(
    N: int,
    *,
    V_dark_mV: float = -40.0,   # depolarized in darkness
    V_rest_mV: float = -65.0,   # hyperpolarized in strong light
    tau_m_ms: float = 50.0,     # slower membrane dynamics than cones
    tau_photo_ms: float = 60.0, # very slow phototransduction
    g_photo_nA: float = 2.0,    # higher sensitivity (stronger current)
    rel_max: float = 1.0,       # max glutamate release (arbitrary units)
    V_half_mV: float = -50.0,   # half-activation for vesicle release
    k_rel_mV: float = 4.0,      # slope for release curve
    default_L: float = 0.0,     # initial light drive (0=dark, 1=bright)
    method: str = "euler",
) -> NeuronGroup:
    """
    Build a graded-potential rod population (no spikes).
    Rods are more sensitive and slower than cones.

    State variables
    --------------
    V : volt
        Membrane potential (graded). Dark baseline ~ -40 mV; hyperpolarizes with light.
    P : 1
        Phototransduction activation (0..1) — a slow low-pass of the instantaneous light drive L.
    L : 1
        External "light drive" (0..1). You set this over time from your stimulus pipeline.
    rel_glu : 1
        Continuous glutamate release proxy (unitless, 0..rel_max), decreases with light.

    Key differences from cones
    --------------------------
    • Much slower time constants (tens of ms vs few ms).
    • Higher sensitivity (larger photo gain).
    • Only one rod type (no color coding).

    Example
    -------
    >>> from brian2 import *
    >>> from rods import create_rod_layer
    >>> rods = create_rod_layer(50)
    >>> Mv = StateMonitor(rods, ['V','rel_glu'], record=[0])
    >>> rods.L = 0.0   # dark
    >>> run(100*ms)
    >>> rods.L = 1.0   # flash of light
    >>> run(400*ms)
    >>> plot(Mv.t/ms, Mv.V[0]/mV)
    """
    # Units
    V_dark = V_dark_mV * mV
    V_rest = V_rest_mV * mV
    tau_m = tau_m_ms * ms
    tau_photo = tau_photo_ms * ms
    g_photo = g_photo_nA * nA
    Cm = 20 * pF  # inner segment capacitance (same order as cones)

    # Core rod equations
    eqs = Equations('''
    dP/dt = (-P + L)/tau_photo : 1
    I_photo = -g_photo * P : amp
    dV/dt = ((V_dark - V)/tau_m) + I_photo/Cm : volt
    L : 1  # external light drive [0..1]
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

    rods = NeuronGroup(
        N, eqs,
        method=method,
        name='rods'
    )

    # Initialization
    rods.V = V_dark
    rods.P = default_L
    rods.L = default_L
    rods.V_dark = V_dark
    rods.tau_m = tau_m
    rods.tau_photo = tau_photo
    rods.g_photo = g_photo
    rods.Cm = Cm
    rods.rel_max = rel_max
    rods.V_half = V_half_mV * mV
    rods.k_rel = k_rel_mV * mV

    return rods
