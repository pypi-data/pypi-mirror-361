from logging import Logger
import copy
import scipy.signal
import numpy as np

from .classes import Signal

def lowpass(signal: Signal, width, attenuation, f, logger: Logger):
    """
    FIR lowpass filter.

    Updates the delay attribute of the Signal object, indicating the delay that
    this filter has created.

    Arguments:
    - signal: Signal object
    - width [Hz]: Transition band width
    - attenuation [dB]: Positive decibels
    - f [Hz]: Cutoff frequency
    """

    nyq_rate = signal.rate / 2

    # Convert to normalized units (where 1 is the maximum frequency, equal to pi
    # radians per second, or equal to rate/2)
    width_norm = width/nyq_rate
    f_norm = f/nyq_rate

    # Calculate the number of taps and beta parameter for the Kaiser window
    logger.debug("Calculating filter parameters")
    filter_taps, beta = scipy.signal.kaiserord(attenuation, width_norm)

    # I prefer filters with odd number of taps
    if filter_taps % 2 == 0:
        filter_taps += 1

    # Design filter
    taps = scipy.signal.firwin(filter_taps, f_norm, window=("kaiser", beta))
    logger.debug("Lowpass filtering with %s taps", filter_taps)

    # Filter and create new Signal object
    result = Signal(
        scipy.signal.lfilter(taps, 1.0, signal.samples),
        signal.rate,
        signal.delay + (filter_taps - 1) // 2
    )
    
    logger.debug("New signal delay: %s", result.delay)
    return result

def bandpass(signal, width, attenuation, f1, f2, logger: Logger):
    """
    Bandpass, leaves frequencies between f1 and f2

    Arguments:
    - signal
    - width [Hz]: Transition band width
    - attenuation [dB]: Positive decibels
    - f1 [Hz]: Cutoff frequency 1
    - f2 [Hz]: Cutoff frequency 2
    """

    nyq_rate = signal.rate / 2

    # Convert to normalized units (where 1 is the maximum frequency, equal to pi
    # radians per second, or equal to rate/2)
    width_norm = width/nyq_rate
    f1_norm = f1/nyq_rate
    f2_norm = f2/nyq_rate

    # Calculate the number of taps and beta parameter for the Kaiser window
    logger.debug("Calculating filter parameters")
    filter_taps, beta = scipy.signal.kaiserord(attenuation, width_norm)

    # I prefer filters with odd number of taps
    if filter_taps % 2 == 0:
        filter_taps += 1

    # Design filter
    taps = scipy.signal.firwin(
        filter_taps,
        [f1_norm, f2_norm],
        window=("kaiser", beta),
        pass_zero=False
    )
    logger.debug("Bandpass filtering with %s taps", filter_taps)

    # Filter and create new Signal object
    result = Signal(
        scipy.signal.lfilter(taps, 1.0, signal.samples),
        signal.rate,
        signal.delay + (filter_taps - 1) // 2
    )

    logger.debug("New signal delay: %s", result.delay)
    return result

def decimate(signal, output_rate, logger: Logger):
    """
    Decimate to reach a given sample rate.

    Raises exception when input and output rate are not divisible.
    """
    assert signal.rate % output_rate == 0
    factor = signal.rate // output_rate

    logger.debug("Decimating signal from %s to %s Hz", signal.rate, output_rate)

    result = Signal(
        signal.samples[::factor],
        output_rate,
        signal.delay // factor
    )
    return result

def compare_phases(ref_signal, var_signal, logger: Logger, angle_offset=223):
    """
    Compare the phase of te reference and variable signals.

    Returns the difference, which should be the location of the receiver respect
    to the VOR transmitter.
    """
    assert ref_signal.rate == var_signal.rate
    rate = ref_signal.rate

    # Copy signals so I do not modify the objects given by the caller
    logger.debug("Copying signals to avoid modifying the originals")
    ref_signal = copy.copy(ref_signal)
    var_signal = copy.copy(var_signal)

    # Remove delays
    # Each succesive FIR filter adds a delay to the samples, so I store in the
    # signal object the delay in samples of each operation. Now I just cut the
    # start of the signal accordingly to leave both signals correctly aligned on
    # time
    logger.debug("Removing delays from signals")
    ref_signal.samples = ref_signal.samples[ref_signal.delay:]
    ref_signal.delay = 0
    var_signal.samples = var_signal.samples[var_signal.delay:]
    var_signal.delay = 0

    # Correct the delay on the var_signal, I don't know why
    logger.debug("Correcting variable signal delay with angle offset")
    delay = int(angle_offset / 360 * 1/30 * rate)
    var_signal.samples = var_signal.samples[delay:]

    # Cut the variable signal if necessary, because if the are the same length
    # we can't do valid correlations. At least leave a difference of 4 periods
    logger.debug("Cutting variable signal to match reference signal length")
    var_max_length = int(len(ref_signal.samples) - rate * 4 / 30)
    if len(var_signal.samples) > var_max_length:
        var_signal.samples = var_signal.samples[:var_max_length]

    # Get the angle difference
    # I'm doing the correlation between both signals and then I take a look at
    # the maximum
    logger.debug("Calculating correlation between signals")
    corr = np.correlate(ref_signal.samples, var_signal.samples, "valid")
    # Offset between signals in seconds
    offset = corr.argmax() / rate
    bearing = (offset / (1/30) * 360)
    bearing = bearing % 360

    # Normalize both signals a bit so the plot looks better
    logger.debug("Normalizing signals for better visualization")
    ref_signal.samples = ref_signal.samples / abs(ref_signal.samples.max())
    var_signal.samples = var_signal.samples / abs(var_signal.samples.max())

    # Return the bearing
    logger.debug("Calculated bearing: %s degrees", bearing)
    return bearing

def get_audio_stats(samples, rate, logger: Logger):
    """
    Returns the sample rate and number of samples in the audio file.
    """
    if not isinstance(samples, np.ndarray):
        raise TypeError("Samples must be a numpy array")
    if not isinstance(rate, int):
        raise TypeError("Rate must be an integer")

    logger.debug("Input sample rate:", rate)
    logger.debug("Input samples:", len(samples))
    logger.debug("Recording duration: %s seconds", len(samples) / rate)
