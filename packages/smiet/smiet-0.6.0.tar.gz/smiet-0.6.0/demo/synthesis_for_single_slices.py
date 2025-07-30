import os.path
import argparse
import bisect
import numpy as np
import matplotlib.pyplot as plt

from smiet import units
from smiet.numpy import SlicedShower, TemplateSynthesis


## Plotting settings
plt.style.use("seaborn-v0_8-paper")
plt.rc("font", size=10)  # controls default text size
plt.rc("font", **{"family": "serif", "serif": ["Computer Modern"]})
plt.rc("axes", titlesize=12)  # fontsize of the title
plt.rc("axes", labelsize=16)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=12)  # fontsize of the x ticks
plt.rc("ytick", labelsize=12)  # fontsize of the y ticks
plt.rc("text", usetex=True)


## Create some functions for later
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Simple example of using template synthesis, comparing to CoREAS"
    )

    parser.add_argument(
        "--frequencies",
        "-f",
        type=float,
        nargs=3,
        default=[30, 500, 100],
        help="The frequency range to use for synthesis",
    )
    parser.add_argument(
        "--ant",
        type=int,
        default=1,
        help="The index of the antenna to plot, in the synthesis arrays",
    )

    parser.add_argument(
        "--origin",
        type=str,
        default="SIM145024.hdf5",
        help="Path to the origin shower",
    )

    parser.add_argument(
        "--target",
        type=str,
        default="SIM145060.hdf5",
        help="Path to the target shower",
    )

    return parser.parse_args()


def get_target_slice_trace(
    target: SlicedShower,
    slice_grammage: int,
    ant_name_select: str,
    freq_range: list[float],
):
    geo_target, ce_target, start_target = target.get_trace_slice(
        ant_name_select, slice_grammage, return_start_time=True
    )
    geo_target_filtered = target.filter_trace(geo_target, *freq_range)
    ce_target_filtered = target.filter_trace(ce_target, *freq_range)

    return geo_target_filtered, ce_target_filtered, start_target


def plot_slice_synthesis(ant_select: int):
    # TODO: maybe also show slice specific antenna information as example of getter?
    fig, ax = plt.subplots(2, 2, figsize=(5, 5))
    ax = ax.flatten()

    # Time axis for the synthesised traces
    time_axis = synthesis.get_time_axis()

    # Time axis for the target shower
    sampling_time = target.coreas_settings["time_resolution"]

    for i, my_slice in enumerate([500, 700, 900, 1100]):
        # Search slice index knowing that the synthesis.slices_grammage list is sorted
        # Alternative: my_slice // slice_grammage - 1
        my_slice_ind = bisect.bisect_left(synthesis.slices_grammage, my_slice)
        geo_synth, ce_synth = synthesis.slice_map_template(my_slice_ind, target)

        geo_target_filtered, ce_target_filtered, start_target = get_target_slice_trace(
            target, my_slice, ant_name_select, synthesis.frequency_range[:2]
        )

        target_time_axis = (
            start_target + np.arange(len(geo_target_filtered)) * sampling_time
        )

        geo = ax[i].plot(
            target_time_axis / units.ns,
            geo_target_filtered / (units.mV / units.m),
            c="k",
            alpha=0.5,
            label="CoREAS",
        )
        ax[i].plot(
            time_axis[ant_select] / units.ns,
            geo_synth[ant_select] / (units.mV / units.m),
            c="magenta",
            label="synthesis",
        )

        ce = ax[i].plot(
            target_time_axis / units.ns,
            ce_target_filtered / (units.mV / units.m),
            linestyle="--",
            c="k",
            alpha=0.5,
        )
        ax[i].plot(
            time_axis[ant_select] / units.ns,
            ce_synth[ant_select] / (units.mV / units.m),
            linestyle="--",
            c="magenta",
        )

        ax[i].set_xlim([target_time_axis[0], target_time_axis[200]])
        ax[i].set_xlabel("Time [ns]")
        ax[i].set_ylabel("Electric field trace [mV / m]")
        ax[i].set_title(f"Slice at {my_slice} g/cm2")

        ax[i].legend()
        # ax[i].legend([geo, ce], ["Geomagnetic", "Charge-excess"])

    return fig


if __name__ == "__main__":
    args = parse_arguments()

    # Check if the showers exist
    if not os.path.exists(args.origin) or not os.path.exists(args.target):
        raise FileNotFoundError(
            f"Either {args.origin} or {args.target} could not be found. "
            f"Did you download them using download_origin_showers.sh?"
        )

    # Load in the showers
    # Both are SlicedShowers in this case, such that we can compare per slice
    origin = SlicedShower(args.origin)
    target = SlicedShower(args.target)

    # Create the synthesis object
    synthesis = TemplateSynthesis(freq_ar=list(args.frequencies))

    # Make the template from the origin - optionally set `ce_lin=False` to use quadratic term for CE
    synthesis.make_template(origin)  # process into template

    # Get the information about the antenna we are plotting
    ant_names = synthesis.get_antenna_names()
    ant_name_select: str = ant_names[args.ant]

    ant_pos_select = synthesis.antenna_information["position_showerplane"][
        synthesis.antenna_information["name"] == ant_name_select
    ]

    # Perform and plot the synthesis for 4 different slices
    figure = plot_slice_synthesis(args.ant)

    figure.suptitle(
        f"Synthesis per slice from {synthesis.template_information['xmax']:.2f} g/cm2 to {target.xmax:.2f} g/cm2 \n Antenna is {ant_name_select} at {np.linalg.norm(ant_pos_select):.1f} m in shower plane",
        size=20,
    )
    plt.show()
