""" Project to create an audio visualizer using Python and the STFT
    Author: Zander Blasingame """

import curses
import locale
import sys
import threading
import time
import numpy as np

import STFT

# default setting for utf-8
locale.setlocale(locale.LC_ALL, '')


###############################################################################
#
# Functions
#
###############################################################################
def _plot_signal(x, y, zero_line, window):
    height = int(y)
    x = int(x)
    zero_line = int(zero_line)

    bounds = window.getmaxyx()

    while (height > 0):
        if (zero_line + height < bounds[0] - 1 and x < bounds[1] - 1):
            window.addch(zero_line + height, x, '\u2588')
        if (zero_line - height > 1 and x > 1):
            window.addch(zero_line - height, x, '\u2588')
        height -= 1

    window.addch(zero_line, x, '\u2588')


plot_signal = np.vectorize(_plot_signal)


# Handles input
def input_handler(char, window, stft):
    if char == -1:
        return

    char = chr(char)

    switcher = {
        'q': {'func': exit,
              'params': {'window': window, 'stft': stft}}
    }

    if char in list(switcher.keys()):
        entry = switcher[char]
        entry['func'](**entry['params'])


# exit function
def exit(window, stft):
    stft.halt()
    window.clear()
    window.refresh()
    curses.reset_shell_mode()
    sys.exit()


###############################################################################
#
# Main Method
#
###############################################################################
def main():
    # variables
    window = curses.initscr()
    window.nodelay(1)  # do not wait for character input
    curses.curs_set(False)

    screen_height, screen_width = window.getmaxyx()
    zero_line = screen_height/2

    # Audio processing class
    stft = STFT.STFT()

    # Create and start audio thread
    thread = threading.Thread(target=stft.record_monitor)
    thread.start()

    # helper functions
    x_transform = np.vectorize(lambda x, width: x * (screen_width / width))
    y_transform = np.vectorize(lambda y, amp: y * (zero_line / amp))

    while True:
        # listen for input keys
        input_handler(window.getch(), window, stft)

        # handle resize
        if curses.is_term_resized(screen_height, screen_width):
            screen_height, screen_width = window.getmaxyx()
            window.clear()
            curses.resizeterm(screen_height, screen_width)
            window.refresh()

        # grab signal
        try:
            freqs, fft = stft.stft()

            x = x_transform(freqs, np.max(freqs) + 1E-9)
            y = y_transform(fft, np.max(fft) + 1E-9)

            window.clear()
            plot_signal(x, y, zero_line, window)

            window.refresh()

            time.sleep(0.05)

        except ValueError:
            pass

if __name__ == '__main__':
    main()
