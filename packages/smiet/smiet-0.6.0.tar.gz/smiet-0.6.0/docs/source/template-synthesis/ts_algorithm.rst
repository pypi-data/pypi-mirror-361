The template synthesis algorithm
================================

The algorithm used in template synthesis is described in "SMIET: Fast and accurate synthesis of radio pulses
from extensive air shower using simulated templates", submitted to `Astroparticle Physics`_, available as a
preprint on `ArXiv`_.

.. _Astroparticle Physics: https://astroparticlephysics.sciencedirect.com/journal/astroparticle-physics
.. _ArXiv: https://arxiv.org/abs/2505.10459

Template generation
-------------------

Everything starts with an :doc:`origin shower <ts_origin_showers>`, which is a sliced CoREAS
simulation. This is provided as an HDF5 file to the algorithm. The raw CoREAS output can be
converted to an HDF5 file using the `coreas_to_hdf5.py` script provided with the CORSIKA package.

To generate a template, the radiation from each slice in the origin shower is processed. First,
the emission is split into the geomagnetic and charge-excess components, using the antenna's
position in the shower plane. Throughout the package, electric fields are given in these two
components (including the output of the synthesis). The components can be combined to get the
three-dimensional electric field assuming there is no emission along the shower axis.

Each component is then normalised using a set of scaling relations. Both geomagnetic and charge-
excess traces are multiplied by the distance to slice and divided by the number of electrons and
positrons in the slice. The geomagnetic trace is also multiplied by the air density in the slice,
and divided by the sine of the geomagnetic angle. The charge-excess trace is divided by the sine
of the Cherenkov angle of the slice.

After this, the traces are transformed to the frequency domain using a real-valued Fourier transform.
The amplitudes outside of the configured frequency range are set to zero. All other entries are
then normalised using the interpolated spectral functions. These are interpolated in viewing angle,
for each frequency bin separately. Before the template generation is complete, we still need to
adjust the phases. To the phases we add a linear component which corresponds to the expected arrival
time of the signal in the antenna. This essentially puts the signal at :math:`t=0`.

After this, the template is ready for synthesis. In order to reuse the template at a later time,
it can be saved to disk.

Mapping to a target
-------------------

The mapping process essentially performs the same steps as detailed above, but in reverse order.
Of course we use the properties of the target shower now. Therefore the operations will not be
cancelled exactly. Changes to the number of particles, the atmosphere or the magnetic field are
all accounted for. Also the viewing angles of the antennas could be different, if for example the
geometry or the Cherenkov angle in the slice changed.

When changing the geometry, it is particularly important to make sure the phases are correct. The
expected arrival times are recalculated. This yields good enough results to use synthesis within
a few degrees in zenith angle. Note that in general it is not a good idea to synthesise showers
with a zenith angle larger than the origin, as those have more slices than the origin provides.
The algorithm will not fail, but instead simply synthesise the emission for every slice present in
the origin. This could lead to some missing radiation.

.. caution::
    The phase calculation is not perfect. The arrival times are calculated with respect to some
    fixed point, which typically is the bottom of the slice. However, slices do have a physical
    extent. The closer they are to the ground, the more this matters. We have observed some
    cases where the pulses are synthesised away from the main pulse for the slices closest to the
    ground. Calculating the arrival times with respect to the centre of the slice changes the times
    at bit, but not enough to have all pulses aling in time.

The outcome of the mapping process is an array of geomagnetic and charge-excess traces, one for each
antenna which was in the origin shower.
