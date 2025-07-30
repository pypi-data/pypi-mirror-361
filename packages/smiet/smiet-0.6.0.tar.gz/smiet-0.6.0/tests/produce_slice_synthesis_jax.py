import time

import numpy as np
import matplotlib.pyplot as plt

import jax
jax.config.update('jax_platform_name', 'cpu')

from smiet import units
from smiet.jax import SlicedShower, TemplateSynthesis


# Selections (to be put in main)
FREQ = [30, 80, 50]

# Variables
# shower_path = '/user/mitjadesmet/CrData/Showers50'
# shower_path = '/home/mitjadesmet/Data/Showers/'
shower_path = '/home/kwatanabe/Projects/radio-ift/resources/template_synthesis/OriginShowers'
# shower_path = "/home/mdesmet/Data/Showers50"
shower_origin = 130165
shower_target = 130188

origin = SlicedShower(f'{shower_path}/SIM{shower_origin}.hdf5')
target = SlicedShower(f'{shower_path}/SIM{shower_target}.hdf5')

time0 = time.time()

synthesis = TemplateSynthesis(freq_ar=FREQ)

time1 = time.time()

synthesis.make_template(origin)

time2 = time.time()

total_geo_synth, total_ce_synth = synthesis.map_template(target)

time3 = time.time()

print(f'Spent {time1 - time0:.4f} initialising, \n'
      f'{time2 - time1:.4f} making template and \n'
      f'{time3 - time2:.4f} mapping it')

# Get the target trace for comparison
ant_names = synthesis.get_ant_names()
origin_time = synthesis.get_time_axis()

dt_res = target.get_coreas_settings()['time_resolution']

geo_origin, ce_origin, start_origin = origin.get_traces(return_start_time=True)
geo_target, ce_target, start_target = target.get_traces(return_start_time=True)

# PLOTTING
plt.style.use('seaborn-v0_8-paper')
plt.rc('font', size=10)  # controls default text size
plt.rc('axes', titlesize=12)  # fontsize of the title
plt.rc('axes', labelsize=16)  # fontsize of the x and y labels
plt.rc('xtick', labelsize=12)  # fontsize of the x ticks
plt.rc('ytick', labelsize=12)  # fontsize of the y ticks
# plt.rc("text", usetex=True)

for ant_idx, ant_name in enumerate(ant_names):
    # Filter target trace
    trace_filtered_geo = np.sum(
        target.filter_trace(
            geo_target[ant_idx,:], *synthesis.frequency_range[:2]
        ),
        axis=1
    )

    trace_filtered_ce = np.sum(
        target.filter_trace(
            ce_target[ant_idx,:], *synthesis.frequency_range[:2]
        ),
        axis=1
    )

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax = ax.flatten()

    ax[0].plot(
        np.arange(len(trace_filtered_geo)) * dt_res + start_target[ant_idx],
        trace_filtered_geo / (units.microvolt / units.m),
        c='k', label='CoREAS',
        alpha=0.5
    )
    ax[1].plot(
        np.arange(len(trace_filtered_ce)) * dt_res + start_target[ant_idx],
        trace_filtered_ce / (units.microvolt / units.m),
        c='k', label='CoREAS',
        alpha=0.5
    )

    ax[0].plot(
        origin_time[ant_idx],
        total_geo_synth[ant_idx,:] / (units.microvolt / units.m),
        '--',
        c='magenta', label='Template Synthesis',
    )
    ax[1].plot(
        origin_time[ant_idx],
        total_ce_synth[ant_idx,:] / (units.microvolt / units.m),
        '--',
        c='magenta', label='Template Synthesis',
    )

    ax[0].set_xlim([origin_time[ant_idx][20], origin_time[ant_idx][1020]])
    ax[1].set_xlim([origin_time[ant_idx][20], origin_time[ant_idx][1020]])

    ax[0].set_ylabel(r'$E [\mu \mathrm{V}/\mathrm{m}]$', size=16)
    ax[0].set_xlabel('Time [ns]')
    ax[1].set_xlabel('Time [ns]')

    ax[0].legend(fontsize=14)
    ax[1].legend(fontsize=14)

    ax[0].set_title('Geomagnetic component')
    ax[1].set_title('Charge-excess component')

    fig.suptitle(f'Signals for antenna {ant_name} \n'
                 r'$X^{\mathrm{origin}}_{\mathrm{max}}$ = ' + f' {origin.xmax:.1f} ' + r'$\mathrm{g}/\mathrm{cm}^2$' + ' - '
                 r' $X^{\mathrm{target}}_{\mathrm{max}}$ = ' + f' {target.xmax:.1f} ' + r'$\mathrm{g}/\mathrm{cm}^2$'
                 '\n', y=1.05, size=17)

    fig.savefig(f'SynthesisedPulse_JAX_{shower_origin}_{shower_target}_{ant_name}.png',
                bbox_inches='tight', dpi=200)

    plt.close(fig)

# plt.show()
print("Done")
