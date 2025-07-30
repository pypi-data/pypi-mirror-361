import numpy as np


def bandpass_filter_trace(trace, trace_sampling, f_min, f_max, sample_axis=0):
    """
    Bandpass filter a trace between `f_min` and `f_max`. Both should be provided in the internal unit
    system, just like the `trace_sampling` parameter. The `trace` array can be multidimensional, in
    which case the `sample_axis` parameter indicates which dimension should be taken as the time
    samples (ie this parameter is passed on to the `np.fft.rfft` call).

    Parameters
    ----------
    trace : np.ndarray
        The array containing the time traces to be filtered
    trace_sampling : float
        The sampling interval of the time traces, in internal units
    f_min : float
        The lower frequency to filter by, in internal units
    f_max : float
        The upper frequency to filter by, in internal units
    sample_axis : int, default=0
        The axis of `trace` which contains the time samples

    Returns
    -------
    filtered_trace : np.ndarray
        The filtered traces, in the same shape as `trace`

    Notes
    -----
    To avoid issues when the maximum of the trace is too close to the edge, all traces are first
    shifted to have their maxima more or less in the middle. After the filter has been applied,
    the traces are rolled back so that they are on same time axis as the input traces.
    """
    # Assuming `trace_sampling` has the correct internal unit, freq is already in the internal unit system
    freq = np.fft.rfftfreq(trace.shape[sample_axis], d=trace_sampling)
    freq_range = np.logical_and(freq > f_min, freq < f_max)

    # Find the median maximum sample number of the traces
    max_index = np.median(np.argmax(trace, axis=sample_axis))
    to_roll = int(trace.shape[sample_axis] / 2 - max_index)

    # Roll all traces such that max is in the middle
    roll_pulse = np.roll(trace, to_roll, axis=sample_axis)

    # FFT, filter, IFFT
    spectrum = np.fft.rfft(roll_pulse, axis=sample_axis)
    spectrum = np.apply_along_axis(
        lambda ax: ax * freq_range.astype("int"), sample_axis, spectrum
    )
    filtered = np.fft.irfft(spectrum, axis=sample_axis)

    return np.roll(filtered, -to_roll, axis=sample_axis)


def transform_traces_on_vxB(my_geo, my_ce, x, y, vxB_axis_mode="replace"):
    """
    Adjust the (synthesised) traces on the vxB axis.

    This function is meant to alter the traces on the vxB axis, as in the current
    version of the SMIET software the vxB axis cannot be synthesised. There are several
    strategies to handle this, and applying them should be facilitated by this function.

    Parameters
    ----------
    my_geo: np.ndarray
        The electric field traces of the geomagnetic component, shaped as (NANTS, NSAMPLES)
    my_ce: np.ndarray
        The electric field traces of the charge-excess component, shaped as (NANTS, NSAMPLES)
    x : np.ndarray
        the x-coordinates of the antennas in the vxB axis, shaped as (NANTS,).
    y : np.ndarray
        the y-coordinates of the antennas in the vxvxB axis, shaped as (NANTS,).
    vxB_axis_mode : {"replace", "zero"}
        Operation to perform on the vxB axis. If "replace" (the default), the traces from the
        vxvxB component will be copied over to the vxB component. If "zero", the vxB component
        will be set to zero.

    Returns
    -------
    my_geo_adjusted : np.ndarray
        The adjusted geomagnetic component traces, shaped as (NANTS, NSAMPLES)
    my_ce_adjusted : np.ndarray
        The adjusted charge-excess component traces, shaped as (NANTS, NSAMPLES)
    """
    ant_at_vB_axis = np.abs(y) < 1e-3
    ant_at_vvB_axis = np.abs(x) < 1e-3

    if vxB_axis_mode == "replace":
        # for the vxB component, replace with the vxvxB component
        my_geo[ant_at_vB_axis,:] = my_geo[ant_at_vvB_axis,:]
        my_ce[ant_at_vB_axis, :] = my_ce[ant_at_vvB_axis, :]
    elif vxB_axis_mode == "zero":
        # for the vxB component, set to zero
        my_geo[ant_at_vB_axis,:] = 0.0
        my_ce[ant_at_vB_axis, :] = 0.0
    else:
        raise ValueError(f"Unknown vxB_axis_mode: {vxB_axis_mode}. Must be one of 'replace' or 'zero'.")
    
    return my_geo, my_ce
