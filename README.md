# CLARA_VISIO

**CLARA_VISIO** is an exploratory project in computational neuroscience, aimed at simulating aspects of the human retina.  
The focus was on two components:  

- **Macula Lutea modeling**: creating a layered, region-specific representation (foveola, fovea, parafovea) using a hexagonal lattice.  
- **Photon influx simulation**: photons described by wavelength (nm), spatial position (x, y), and time of arrival (t).  

The core prototype implements **cone photoreceptor dynamics** in [Brian2](https://brian2.readthedocs.io), modeling graded potentials and neurotransmitter release.  

This is an **experimental prototype** rather than a finished simulation: it was developed as an exploration of how retinal preprocessing might be represented computationally. Future extensions would connect cones to bipolar, horizontal, and ganglion cells to capture the retina’s layered computations.  
