""" Class to visualize audio data
    Author: Zander Blasingame """

import locale
import curses
import numpy as np
from scipy import signal

# settings
locale.setlocale(locale.LC_ALL, '')

# Global Vars
VELOCTIY = 1


class Visualizer:
    def __init__(self):
        self._setup_ncurses()
        self._init_lines()

    def _setup_ncurses(self):
        self.window = curses.initscr()
        self.window.nodelay(1)
        self.nlines = self.window.getmaxyx()[0]
        self.ncols = self.window.getmaxyx()[1]
        curses.curs_set(False)

    def _init_lines(self):
        self.lines = {}
        self.lines['left'] = [self.Line(x=i, negative=False, velocity=VELOCTIY)
                              for i in range(self.ncols)]
        self.lines['right'] = [self.Line(x=i, negative=True, velocity=VELOCTIY)
                               for i in range(self.ncols)]

    def _map(self, x, interval, new_dim):
        if interval == 0:
            interval = 1E-9

        return (x - np.min(x)) * (new_dim / interval)

    def _get_magnitudes(self, data, frequency_band):
        x = self._map(data['freqs'], frequency_band, self.ncols)
        y = self._map(data['fft'], np.max(data['fft']), self.nlines)

        avg_fft = []

        for i in range(self.ncols-1):
            avg_fft.append(np.max(np.append(0, [y[j]
                                                for j in range(len(x))
                                                if int(x[j]) == i])))

        # Smoothing filter and moving average
        # Not sure if I need moving average or not
        # avg_fft = self._moving_average(avg_fft, 3)
        avg_fft = signal.savgol_filter(avg_fft, 11, 3)

        return avg_fft

    def _moving_average(self, x, window):
        return np.convolve(x, np.repeat(1.0, window)/window)

    def render(self, get_data):
        try:
            data = get_data()
        except ValueError:
            return

        self._resize_term()

        self.window.clear()

        frequency_band = data['range'][1] - data['range'][0]

        left = self._get_magnitudes(data['left'], frequency_band)
        right = self._get_magnitudes(data['right'], frequency_band)

        for i in range(self.ncols-1):
            self.lines['left'][i].draw_line(left[i],
                                            self.window,
                                            self.nlines/2,
                                            [0, self.nlines])

            self.lines['right'][i].draw_line(right[i],
                                             self.window,
                                             self.nlines/2,
                                             [0, self.nlines])

        self.window.refresh()

    def toggle_log_scale(self):
        self.log_scale = not self.log_scale

    def _resize_term(self):
        if curses.is_term_resized(self.nlines, self.ncols):
            self.nlines = self.window.getmaxyx()[0]
            self.ncols = self.window.getmaxyx()[1]

            self.window.clear()
            curses.resize_term(self.nlines, self.ncols)
            self.window.refresh()

            self._init_lines()

    def shut_down(self):
        self.window.clear()
        self.window.refresh()
        curses.curs_set(True)
        curses.reset_shell_mode()

    def get_ch(self):
        return self.window.getch()

    class Line:
        def __init__(self, x=0, negative=False, velocity=1):
            self.height = 0
            self.x = x
            self.negative = negative
            self.velocity = velocity

        def draw_line(self, value, window, zero_line, bounds):
            # update line height
            self._update(value, bounds)

            # print('value: {}\n'.format(value), file=open('log', 'a'))

            window.addch(int(zero_line), self.x, '\u2588')

            if not self.negative:
                h = 1
                while h < self.height:
                    window.addch(int(zero_line - h), self.x, '\u2588')
                    h += 1
            else:
                h = 1
                while h < self.height:
                    window.addch(int(h + zero_line), self.x, '\u2588')
                    h += 1

        def _update(self, value, bounds):
            self.height -= self.velocity

            if value > self.height:
                self.height = value

            if self.height > bounds[1]/2:
                self.height = bounds[1]/2 - 1
            elif self.height < bounds[0]/2:
                self.height = bounds[0]/2 + 1
