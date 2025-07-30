import logging
import scipy.io.wavfile
import numpy as np

from .classes import Signal
from .utils import lowpass, bandpass, decimate, compare_phases, get_audio_stats

logger = logging.getLogger("python-vor")

DECIMATED_RATE = 6000

def get_bearing(wav_file_path: str, offset: int = 223) -> float:
    """
    Calculate the bearing from a VOR audio file.
    
    This function processes a WAV file containing VOR audio, applies necessary filters,
    and calculates the bearing based on the phase difference between the reference and variable signals.
    It decimates the audio to speed up processing and applies lowpass and bandpass filters to isolate the relevant signals.
    The final bearing is adjusted by the provided offset.
    
    If a correction is needed, the default offset is set to 223 degrees, if the results are not as expected,
    you can adjust the offset using the `offset` parameter. The offset is calculated as follows:
    
    ```python
    new_offset = current_offset + (actual_bearing - calculated_bearing)
    ```
    
    Where `actual_bearing` is the expected bearing based on the recording location and `calculated_bearing`
    is the result from this function. 223 degrees is the calculated offset for my test VOR signals, it might
    not be the same for every VOR or location.
    
    Args:
        wav_file_path (str): Path to the WAV file containing VOR audio.
        offset (int): Offset to be added to the calculated bearing.
    Returns:
        float: Calculated bearing of the recording location to the VOR location in degrees.
    """
    
    # Load input from wav
    logger.debug("Loading WAV input from %s", wav_file_path)
    rate, samples = scipy.io.wavfile.read(wav_file_path)
    if samples.ndim > 1:
        # Keep only one channel if audio is stereo
        logger.debug("Input is stereo, keeping only one channel")
        samples = samples[:, 0]
    else:
        logger.debug("Input is mono, no need to keep only one channel")

    input_signal = Signal(samples, rate)
    get_audio_stats(samples, rate, logger)

    # If the recording is longer than 1 second, decimate it to speed up the processing
    if len(samples) / rate > 1:
        logger.debug("Recording is longer than 1 second, cutting it to %s samples", rate)
        samples = samples[:rate]
        input_signal = Signal(samples, rate)
        get_audio_stats(samples, rate, logger)
    else:
        logger.debug("Recording is shorter than 1 second, not decimating")


    # Filter and decimate reference signal, a 30Hz tone
    logger.debug("Applying lowpass filter to reference signal")
    ref_signal = lowpass(
        input_signal,
        width=500,
        attenuation=60,
        f=500,
        logger=logger
    )
    logger.debug("Decimating reference signal to %sHz", DECIMATED_RATE)
    ref_signal = decimate(signal=ref_signal, output_rate=DECIMATED_RATE, logger=logger)

    # Filter FM signal
    logger.debug("Applying bandpass filter to FM signal")
    fm_signal = bandpass(
        input_signal,
        width=1000,
        attenuation=60,
        f1=8500,
        f2=11500,
        logger=logger
    )

    # Center FM signal on 0Hz
    logger.debug("Centering FM signal on 0Hz")
    carrier = np.exp(-1.0j*2.0*np.pi*9960/fm_signal.rate*np.arange(len(fm_signal.samples)))
    fm_signal.samples = fm_signal.samples * carrier

    # Lowpass and decimate FM signal
    logger.debug("Applying lowpass filter to FM signal")
    fm_signal = lowpass(
        fm_signal,
        width=500,
        attenuation=60,
        f=1500,
        logger=logger
    )

    logger.debug("Decimating FM signal to %sHz", DECIMATED_RATE)
    fm_signal = decimate(signal=fm_signal, output_rate=DECIMATED_RATE, logger=logger)

    # Get phase of FM signal to get the variable signal
    logger.debug("Calculating phase of FM signal")
    var_signal = Signal(
        np.unwrap(np.angle(fm_signal.samples)),
        fm_signal.rate,
        fm_signal.delay
    )

    # Remove DC of variable signal
    logger.debug("Removing DC from variable signal")
    var_signal = bandpass(
        var_signal,
        width=15,
        attenuation=60,
        f1=15,
        f2=45,
        logger=logger
    )

    # Compare phases of reference and variable signals
    logger.debug("Comparing phases of reference and variable signals")
    bearing = compare_phases(ref_signal=ref_signal, var_signal=var_signal, logger=logger, angle_offset=offset)
    logger.debug("Calculated bearing: %s°", bearing)
    
    return bearing
