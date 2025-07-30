import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from cr_pulse_interpolator import signal_interpolation_fourier as sigF
from cr_pulse_interpolator import interpolation_fourier as interpF

from smiet import units
from smiet.numpy import geo_ce_to_e, SlicedShower, TemplateSynthesis

# Selections (to be put in main)
F_MIN, F_MAX, F_0 = np.array([30, 80, 50]) * units.MHz
INTERPOLATION = 'trace'


# Convenience functions
def rot_matrix(angle):
    matrix = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return matrix


# Variables
shower_path = '/home/mitjadesmet/Data/ShowersSKA/OriginShowers'
shower_origin = 130165
shower_target = 130188

origin = SlicedShower(f'{shower_path}/SIM{shower_origin}.hdf5')
target = SlicedShower(f'{shower_path}/SIM{shower_target}.hdf5')

synthesis = TemplateSynthesis()
synthesis.read_spectral_file(
    f'spectral_parameters_{int(F_MIN / units.MHz)}_{int(F_MAX / units.MHz)}_{int(F_0 / units.MHz)}.hdf5'
)
synthesis.make_template(origin)

total_geo_synth, total_ce_synth = synthesis.map_template(target)

transformer = origin.get_transformer()

x, y, z = transformer.transform_to_vxB_vxvxB(synthesis.antenna_information['position'], core=origin.core).T

# Check starshape
radius = np.linspace(20.0, 100.0, 5)
radius_ext = np.linspace(125.0, 225.0, 5)
radius = np.concatenate((radius, radius_ext))

fig, ax = plt.subplots(1, 1, figsize=(10, 10))
for r in radius[:-1]:
    # Starshape of SKA simulations is off, but still on concentric circles
    circle = plt.Circle((0, 0), r, color='r', fill=False)
    ax.add_patch(circle)
ax.scatter(x, y, s=5)
ax.set_aspect('equal')

plt.show()

# Convert GEO/CE back to on-sky
on_sky_star_shape = geo_ce_to_e(np.stack((total_geo_synth, total_ce_synth), axis=2), x, y)
footprint_star_shape = np.zeros((*total_geo_synth.shape, 3))
for ind in range(footprint_star_shape.shape[0]):
    footprint_star_shape[ind] = transformer.transform_from_ground_to_onsky(
        on_sky_star_shape[ind].T
    ).T

# Make signal interpolator
interpolator = sigF.interp2d_signal(
    x, y,
    footprint_star_shape,
    lowfreq=F_MIN / units.MHz,
    highfreq=F_MAX / units.MHz,
    verbose=True,
    phase_method='phasor',
    sampling_period=target.coreas_settings['time_resolution'] / units.s
)

# SKA shower set is rotated, so generate normal starshape from interpolator
one_arm_distances = np.concatenate((
    [12.5 / 8, 12.5 / 4, 12.5 / 2],
    np.arange(12.5, 200, 12.5),
    np.arange(200, 300, 25)
))

starshape_pos_x = []
starshape_pos_y = []
for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
    x, y = np.matmul(rot_matrix(np.deg2rad(angle)), np.stack((one_arm_distances, np.zeros_like(one_arm_distances))))
    starshape_pos_x.extend(x)
    starshape_pos_y.extend(y)

starshape_pos_x = np.array(starshape_pos_x)
starshape_pos_y = np.array(starshape_pos_y)

starshape_values = np.zeros((len(starshape_pos_x), *footprint_star_shape.shape[1:]))
for ind in range(len(starshape_pos_x)):
    starshape_values[ind, :, :] = interpolator(starshape_pos_x[ind], starshape_pos_y[ind])

starshape_fluences = np.sum(starshape_values ** 2, axis=(1, 2))

# And now we make a fluence interpolator to check the footprint
fluence_interpolator = interpF.interp2d_fourier(starshape_pos_x, starshape_pos_y, starshape_fluences)

# Calculate footprint
dist_scale = 300.0
ti = np.linspace(-dist_scale, dist_scale, 1000)
XI, YI = np.meshgrid(ti, ti)

ZI = fluence_interpolator(XI, YI)
maxp = np.max(ZI)

# Plot footprint
norm = mcolors.Normalize(
    vmin=0,
    vmax=maxp
)
cmap = mpl.colormaps.get_cmap('jet')

fig, ax = plt.subplots(1, 1, figsize=(10, 10))

ax.pcolor(XI, YI, ZI, cmap=cmap, norm=norm)
ax.scatter(starshape_pos_x, starshape_pos_y, marker='+', s=3, color='w')

mm = mpl.cm.ScalarMappable(cmap=cmap)
mm.set_array([0.0, maxp])

cbar = fig.colorbar(mm, ax=ax)
cbar.set_label('Values of f(x, y)')

ax.set_xlabel('x [ m ]')
ax.set_ylabel('y [ m ]')
ax.set_xlim(-300, 300)
ax.set_ylim(-300, 300)
ax.set_aspect('equal')

plt.savefig(f'Footprint_synthesis_{shower_origin}_{shower_target}.png')

print("Done")
