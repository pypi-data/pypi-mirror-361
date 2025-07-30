import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import radiotools.helper as hp

from smiet import units
from smiet.numpy import SlicedShowerCherenkov, SlicedShower, TemplateSynthesis
from smiet.numpy.utilities import angle_between


def calculate_distance_to_ant(the_slice, shower, ant):
    d_xmax = the_slice._atm.get_distance_xmax_geometric(
        shower.zenith / units.rad, the_slice.grammage, observation_level=shower.antenna_dict[ant][2]
    ) * units.m

    unit_shower_axis = hp.spherical_to_cartesian(shower.zenith / units.rad, shower.azimuth / units.rad)
    slice_vector = unit_shower_axis * d_xmax

    ant_pos = np.array([-1 * shower.antenna_dict[ant][1], shower.antenna_dict[ant][0], shower.antenna_dict[ant][2]])
    slice_to_ant_vector = ant_pos - slice_vector

    return np.linalg.norm(slice_to_ant_vector, axis=-1)


def calculate_viewing_angle(the_slice, shower, ant):
    d_xmax = the_slice._atm.get_distance_xmax_geometric(
        shower.zenith / units.rad, the_slice.grammage, observation_level=shower.antenna_dict[ant][2]
    ) * units.m

    unit_shower_axis = hp.spherical_to_cartesian(shower.zenith / units.rad, shower.azimuth / units.rad)
    slice_vector = unit_shower_axis * d_xmax

    ant_pos = np.array([-1 * shower.antenna_dict[ant][1], shower.antenna_dict[ant][0], shower.antenna_dict[ant][2]])
    slice_to_ant_vector = ant_pos - slice_vector

    cherenkov_angle = the_slice._calculate_cherenkov_angle(shower.zenith)

    return angle_between(slice_to_ant_vector, -1 * slice_vector) / cherenkov_angle


def calculate_viewing_angle_ant(the_slice, shower, ant):
    from radiotools.atmosphere.cherenkov_radius import get_cherenkov_angle
    ant_pos = shower.get_ant_position_showerplane(ant)

    viewing_angle = my_synthesis.atm.get_viewing_angle(
        shower.zenith / units.rad, np.linalg.norm(ant_pos[:2]),
        xmax=the_slice.grammage, observation_level=shower.antenna_dict[ant][2]
    )
    cherenkov_angle = get_cherenkov_angle(
        the_slice._atm.get_vertical_height(shower.zenith / units.rad, the_slice.grammage), (1 + 292e-6), 17
    )

    return viewing_angle / cherenkov_angle


GRAMMAGE = 900
# COPIED FROM GEN FILE
VIEWING_ANGLES = np.array([
    0.001, 0.004, 0.007,
    0.01, 0.05, 0.10, 0.50,
    0.97, 0.98, 0.99, 1.00,
    1.01, 1.02, 1.03, 1.50,
    2.00, 2.50, 3.00, 4.00,
    5.00, 6.00, 7.00, 8.00,
    9.00, 10.0,
])


if __name__ == '__main__':
    origin = SlicedShower('/home/mitjadesmet/Data/Showers/SIM130057.hdf5')
    my_shower = SlicedShowerCherenkov('/home/mitjadesmet/Data/Showers/SIM160000.hdf5')
    my_shower_2 = SlicedShowerCherenkov('/home/mitjadesmet/Data/Showers/SIM160001.hdf5')

    my_synthesis = TemplateSynthesis(freq_ar=[30, 500, 100])
    my_synthesis.make_template(origin)

    my_slice = my_synthesis.slices[GRAMMAGE // 5 - 1]

    matching_index_viewing_angles = {
        angle: np.abs(angle - my_synthesis.viewing_angles).argmin()
        for angle in VIEWING_ANGLES
    }

    my_ant = np.array([el for el in my_shower.antenna_names if el.split('x')[1] == f'{GRAMMAGE}'])
    my_pos = np.array([my_shower.get_ant_position_showerplane(ant) for ant in my_ant])
    my_dist = np.sqrt(np.sum(my_pos[:, :2] ** 2, axis=1))
    my_sorted_ind = np.argsort(my_dist)

    ant_per_viewing = {
        angle: my_ant[my_sorted_ind[(idx * 8):((idx + 1) * 8)]]
        for idx, angle in enumerate(VIEWING_ANGLES)
    }

    # vxvxB arm
    pos_vvB = angle_between(my_pos[my_sorted_ind, :2], np.array([0, 1])) < 1e-1
    neg_vvB = np.abs(np.pi - angle_between(my_pos[my_sorted_ind, :2], np.array([0, 1]))) < 1e-1
    tot_vvB = np.logical_or(pos_vvB, neg_vvB)

    ant_per_viewing_vvB = {
        angle: my_ant[my_sorted_ind][tot_vvB][(idx * 2):((idx + 1) * 2)]
        for idx, angle in enumerate(VIEWING_ANGLES)
    }

    for angle, ants in ant_per_viewing_vvB.items():
        print('=====')
        print(angle)
        print('----')
        for ant in ants:
            print(f'{calculate_viewing_angle(my_slice, my_shower, ant):.3f}')
        print('-----')
        for ant in ants:
            print(f'{calculate_viewing_angle_ant(my_slice, my_shower, ant):.3f}')


    cmap = mpl.colormaps.get_cmap('viridis')
    norm = mpl.colors.Normalize(vmin=min(VIEWING_ANGLES), vmax=max(VIEWING_ANGLES))

    # plt.scatter(my_pos[:, 0], my_pos[:, 1], c='k')
    # for angle, ants in ant_per_viewing_vvB.items():
    #     for ant in ants:
    #         plt.scatter(
    #             *my_shower.ant_position_showerplane(ant)[:2], color=cmap(norm(angle))
    #         )
    # plt.show()

    # Evaluate spectral functions
    delta_xmax_origin = GRAMMAGE - my_shower.xmax
    delta_xmax_target = GRAMMAGE - my_shower_2.xmax
    freq_range = np.logical_and(
        my_synthesis.frequency_range[0] <= my_synthesis.frequencies,
        my_synthesis.frequencies <= my_synthesis.frequency_range[1]
    )

    geo_origin, ce_origin, ce_lin_origin = my_slice.get_spectra(
        delta_xmax_origin, my_synthesis.frequencies[freq_range] - my_synthesis.frequency_range[2]
    )
    geo_target, ce_target, ce_lin_target = my_slice.get_spectra(
        delta_xmax_target, my_synthesis.frequencies[freq_range] - my_synthesis.frequency_range[2]
    )

    geo_factor, ce_factor = my_slice.get_normalisation_factors(my_shower)
    for angle in ant_per_viewing_vvB.keys():
        fig, ax = plt.subplots(2, 2, figsize=(14, 10))
        for ant in ant_per_viewing_vvB[angle]:
            trace_slice_geo, trace_slice_ce = my_shower.get_trace_slice(ant)
            trace_slice_geo_2, trace_slice_ce_2 = my_shower_2.get_trace_slice(ant)
            distance = calculate_distance_to_ant(my_slice, my_shower, ant)

            geo_corr = 2 * distance / geo_factor / (units.microvolt / units.m)
            ax[0, 0].plot(
                trace_slice_geo * geo_corr, label=ant
            )
            ax[0, 0].plot(
                trace_slice_geo_2 * geo_corr, '--', label=ant
            )
            ax[1, 0].plot(
                my_synthesis.frequencies / units.MHz, np.abs(np.fft.rfft(trace_slice_geo, norm='ortho')) * geo_corr,
                label=ant
            )
            ax[1, 0].plot(
                my_synthesis.frequencies / units.MHz, np.abs(np.fft.rfft(trace_slice_geo_2, norm='ortho')) * geo_corr,
                '--', label=ant
            )

            ce_corr = 2 * distance / ce_factor / (units.microvolt / units.m)
            ax[0, 1].plot(
                trace_slice_ce * ce_corr, label=ant
            )
            ax[0, 1].plot(
                trace_slice_ce_2 * ce_corr, '--', label=ant
            )
            ax[1, 1].plot(
                my_synthesis.frequencies / units.MHz, np.abs(np.fft.rfft(trace_slice_ce, norm='ortho')) * ce_corr,
                label=ant
            )
            ax[1, 1].plot(
                my_synthesis.frequencies / units.MHz, np.abs(np.fft.rfft(trace_slice_ce_2, norm='ortho')) * ce_corr,
                '--', label=ant
            )

        ax[1, 0].plot(
            my_synthesis.frequencies[freq_range] / units.MHz, geo_origin[matching_index_viewing_angles[angle]], 'k'
        )
        ax[1, 0].plot(
            my_synthesis.frequencies[freq_range] / units.MHz, geo_target[matching_index_viewing_angles[angle]], 'k--'
        )

        ax[1, 1].plot(
            my_synthesis.frequencies[freq_range] / units.MHz, ce_lin_origin[matching_index_viewing_angles[angle]], 'k'
        )
        ax[1, 1].plot(
            my_synthesis.frequencies[freq_range] / units.MHz, ce_lin_target[matching_index_viewing_angles[angle]], 'k--'
        )

        ax[0, 0].set_xlim([50, 1000])
        ax[0, 1].set_xlim([50, 1000])
        ax[1, 0].set_xlim([0, 500])
        ax[1, 1].set_xlim([0, 500])

        ax[1, 1].legend()

        ax[0, 0].set_title('Geomagnetic component')
        ax[0, 1].set_title('Charge-excess component')

        fig.suptitle(
            f'Angle = {angle} \n'
            f'Solid Delta = {delta_xmax_origin:.3f} \n'
            f'Dashed Delta = {delta_xmax_target:.3f}'
        )

        fig.savefig(f'output/Compare_spectra_{my_shower.name}_{my_shower_2.name}_{GRAMMAGE}_{int(angle * 1000)}.png',
                    bbox_inches='tight', dpi=200)

        plt.close(fig)
