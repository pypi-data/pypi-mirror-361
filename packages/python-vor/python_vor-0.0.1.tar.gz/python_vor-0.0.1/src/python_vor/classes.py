class Signal:
    """Class to hold a signal with its sample rate and delay."""

    samples: int
    rate: int
    delay: int

    def __init__(self, samples, rate, delay=0):
        """
        Keeps the data of a signal and sample rate tied together.

        Also keeps track of the delay that this signal has, each FIR filter adds
        a delay of N/2 being N the number of taps. At the end I need the delays
        of each signal to compare the phase of them.
        """
        self.samples = samples
        self.rate = rate
        self.delay = delay
