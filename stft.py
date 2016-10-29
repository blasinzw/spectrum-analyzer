""" Class to pull audio and implement Short Term Fourier Transform
    Author: Zander Blasingame """

import pyaudio
import numpy as np
from scipy import signal

# Constants
BUFFER_SIZE = 1024
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
                        frames_per_buffer=BUFFER_SIZE)

        while not self.exit:
            self.current_buffer = stream.read(BUFFER_SIZE)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def _stft(self, audio_signal, log_scale=False):
        fft = abs(np.fft.fft(audio_signal))
        # multiply 1/RATE by a half because magic ?
        freqs = np.fft.fftfreq(audio_signal.size, 1/RATE)
        # freqs = np.fft.fftshift(freqs)

        data = [dict(freq=freq, fft=fft[i])
                for i, freq in enumerate(freqs)
                if freq > FREQUENCY_RANGE[0] and freq < FREQUENCY_RANGE[1]]

        freqs = np.array([d['freq'] for d in data])
        fft = np.array([d['fft'] for d in data])

        # Reverse frequencies to fix error
        # freqs = freqs[::-1]

        if log_scale:
            freqs = np.log10(freqs)

        # Makes graph look better
        fft = np.power(fft, 2)

        return freqs, fft

    def get_stft(self, log_scale=False):
        if self.current_buffer == '':
            raise ValueError

        audio_signal = np.fromstring(self.current_buffer, dtype=np.int16)

        audio_signal = np.reshape(audio_signal, (BUFFER_SIZE, 2))

        left = audio_signal[:, 0]
        right = audio_signal[:, 1]

        data = {}

        freqs, fft = self._stft(left, log_scale)
        data['left'] = {'fft': fft, 'freqs': freqs}

        freqs, fft = self._stft(right, log_scale)
        data['right'] = {'fft': fft, 'freqs': freqs}

        return data

    def halt(self):
        self.exit = True
