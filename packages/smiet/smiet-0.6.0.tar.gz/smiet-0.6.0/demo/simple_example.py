import argparse
import os.path

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


def get_target_traces(target, ant_name_select, freq_range):
    geo_target, ce_target, start_target = target.get_trace(
        ant_name_select, return_start_time=True
    )
    geo_target_filtered = target.filter_trace(np.sum(geo_target, axis=0), *freq_range)
    ce_target_filtered = target.filter_trace(np.sum(ce_target, axis=0), *freq_range)

    return geo_target_filtered, ce_target_filtered, start_target[0]


def plot_synth_coreas_comparison(
    synthesis: TemplateSynthesis,
    target: SlicedShower,
    geo_synth: np.ndarray,
    geo_target_filtered: np.ndarray,
    ce_synth: np.ndarray,
    ce_target_filtered: np.ndarray,
    ant_select,
):
    # Time axis for the synthesised traces
    time_axis = synthesis.get_time_axis()

    # Time axis for the target shower
    sampling_time = target.coreas_settings["time_resolution"]
    target_time_axis = (
        start_target + np.arange(len(geo_target_filtered)) * sampling_time
    )

    # Plotting
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    ax[0].plot(
        target_time_axis / units.ns,
        geo_target_filtered / (units.mV / units.m),
        c="k",
        alpha=0.5,
    )
    ax[0].plot(
        time_axis[ant_select] / units.ns,
        geo_synth[ant_select] / (units.mV / units.m),
        c="magenta",
    )

    ax[1].plot(
        target_time_axis / units.ns,
        ce_target_filtered / (units.mV / units.m),
        c="k",
        alpha=0.5,
    )
    ax[1].plot(
        time_axis[ant_select] / units.ns,
        ce_synth[ant_select] / (units.mV / units.m),
        c="magenta",
    )

    ax[0].set_xlim([target_time_axis[0], target_time_axis[200]])
    ax[1].set_xlim([target_time_axis[0], target_time_axis[200]])

    ax[0].set_xlabel("Time [ns]")
    ax[1].set_xlabel("Time [ns]")

    ax[0].set_ylabel("Geomagnetic trace [mV / m]")
    ax[1].set_ylabel("Charge-excess trace [mV / m]")

    return fig


if __name__ == "__main__":
    args = parse_arguments()

    # Check if the showers exist
    if not os.path.exists(args.origin) or not os.path.exists(args.target):
        raise FileNotFoundError(
            f"Either {args.origin} or {args.target} could not be found. "
            f"Did you download them using download_origin_showers.sh?"
        )

    ## Load in the showers
    # Both are SlicedShowers in this case, such that we can easily compare the synthesis result to CoREAS
    # But technically the target only needs to be a Shower object
    origin = SlicedShower(args.origin)
    target = SlicedShower(args.target)

    ## Do the synthesis
    # Create the synthesis object
    synthesis = TemplateSynthesis(freq_ar=list(args.frequencies))

    # Make the template from the origin - optionally set `ce_lin=False` to use quadratic term for CE
    synthesis.make_template(origin)  # process into template

    # Map the template onto the target -> output shape = (ant, samples)
    geo, ce = synthesis.map_template(target)  # map onto the target shower

    ## analysis
    # The synthesis is done! Now we can use the results in our analysis
    # Here we just show a plot to compare synth to CoREAS

    # Retrieve the traces from the target shower -> shape (slices, samples)
    ant_names = synthesis.get_antenna_names()
    ant_name_select = ant_names[args.ant]

    ant_pos_select = synthesis.antenna_information["position_showerplane"][
        synthesis.antenna_information["name"] == ant_name_select
    ]
    geo_target_filtered, ce_target_filtered, start_target = get_target_traces(
        target, ant_name_select, synthesis.frequency_range[:2]
    )

    figure = plot_synth_coreas_comparison(
        synthesis, target, geo, geo_target_filtered, ce, ce_target_filtered, args.ant
    )

    figure.suptitle(
        f"Synthesis from {synthesis.template_information['xmax']:.2f} g/cm2 to {target.xmax:.2f} g/cm2 \n Antenna is {ant_name_select} at {np.linalg.norm(ant_pos_select):.1f} m in shower plane",
        size=20,
    )

    plt.show()
