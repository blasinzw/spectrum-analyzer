""" Class to pull audio and implement Short Term Fourier Transform
    Author: Zander Blasingame """

import pyaudio
import numpy as np

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
FREQUENCY_RANGE = [20, 20E3]


class STFT:
    def __init__(self, input_device_index=9):
        self.current_buffer = ''  # byte string
        self.input_device_index = input_device_index
        self.exit = False

    def record_monitor(self):
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        input=True,
                        rate=RATE,
                        input_device_index=self.input_device_index,
                        frames_per_buffer=CHUNK)

        while not self.exit:
            self.current_buffer = stream.read(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stft(self, log=False):
        if self.current_buffer == '':
            raise ValueError

        signal = np.fromstring(self.current_buffer, dtype=np.int16)

        fft = abs(np.fft.fft(signal))
        # multiply 1/RATE by a half because magic ?
        freqs = np.fft.fftfreq(signal.size, 0.5/RATE)
        freqs = np.fft.fftshift(freqs)

        data = [dict(freq=freq, fft=fft[i])
                for i, freq in enumerate(freqs)
                if freq > FREQUENCY_RANGE[0] and freq < FREQUENCY_RANGE[1]]

        freqs = np.array([d['freq'] for d in data])
        fft = np.array([d['fft'] for d in data])

        if log:
            freqs = np.log10(freqs)
            # fft = np.log10(fft)

        return freqs, fft

    def halt(self):
        self.exit = True
