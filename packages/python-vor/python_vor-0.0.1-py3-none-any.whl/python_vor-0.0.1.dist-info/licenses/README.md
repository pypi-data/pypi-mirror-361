# Python VOR Decoder

This repository contains a pure Python implementation of a VOR (VHF Omnidirectional Range) radio navigation signal decoder. The code is based on and adapted from the work of [martinber](https://github.com/martinber/vor-python-decoder), with additional comments, explanations, and minor modifications for clarity and usability.

## Overview

VOR is a type of radio navigation system for aircraft, allowing pilots to determine their position and bearing relative to a ground-based VOR station. This decoder processes a WAV file recording of a VOR signal and extracts the bearing information using digital signal processing techniques.

## Features

- **Pure Python implementation** using NumPy, SciPy, and Matplotlib
- **Signal processing pipeline** including:
  - Lowpass and bandpass FIR filtering
  - Sample rate decimation
  - FM subcarrier demodulation and phase extraction
  - Cross-correlation for phase comparison
- **Visualization** of signals in both time and frequency domains at each processing step
- **Calibration support** for phase alignment

## Testing

I tested the code using the signal from the VRN airport in Verona, Italy. The code successfully decoded the VOR signal and displayed the correct bearing with a small approximation.

### Test points

![Map of the test points](https://raw.githubusercontent.com/iu2frl/PythonVOR/main/imgs/VRN_map.png)

The following test points were used, with their respective bearings:

- **45.377740N 10.880124E**: Measured 211° - Displays 208°
- **45.392627N 10.905900E**: Measured 181° - Displays 176°
- **45.409503N 10.883784E**: Measured 275° - Displays 270°
- **45.412321N 10.900993E**: Measured 322° - Displays 315°
- **45.418328N 10.930478E**: Measured 58° - Displays 52°

## Usage

### WAV recording

**Record a VOR signal** as a WAV file (mono or stereo). The recording should capture both the AM reference and FM variable signals.

- The receiver should be set to AM mode with a bandwidth of 22KHz
- Recording should be saved with a minimum sample rate of 48KHz (96KHz preferred)
- There is no need to record more than 1 second of audio, as the decoder processes the signal in chunks.

### Calculating using Jupyter Notebook

The Jupyter Notebook at [VOR_Decoder.ipynb](https://github.com/iu2frl/PythonVOR/blob/main/VOR_Decoder.ipynb) provides an interactive environment to process the recorded WAV file and extract the bearing.

It displays the decoding steps, including the original signal, filtered signals, and the final bearing result with visualizations.

1. **Set the `FILENAME` variable** in the notebook or script to point to your WAV file.
1. **Run the notebook or script** to process the signal and extract the bearing.

### Calculating using Python library

1. Install the library using pip: `pip install python-vor`
2. Import the `get_bearing` function from the library: `from python_vor import get_bearing`
3. Call the function with the WAV file path and optional parameters:

```python
from python_vor import get_bearing
offset = 216  # Optional offset to add in the VOR calculation
bearing = get_bearing(str(wav_file), offset=offset)
print(f"Bearing for {wav_file.name}: {bearing:.2f}°")
```

### Processing details

The processing steps include:

- Loading and displaying audio statistics
- Filtering and decimating the reference and variable signals
- Demodulating the FM subcarrier
- Extracting and filtering the variable signal phase
- Comparing phases to compute the bearing

## Dependencies

- numpy
- scipy
- matplotlib (only for the Jupyter Notebook visualization)

Install them via pip if needed:

```bash
pip install scipy==1.16.0
pip install numpy==2.3.1
```

## Contributing

Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on contributing to this project.

## Attribution

Original code and algorithm by [martinber](https://github.com/martinber/vor-python-decoder).  
This repository provides a cleaned-up and commented version for educational and practical use.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
