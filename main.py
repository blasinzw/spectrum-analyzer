""" Project to create an audio visualizer using Python and the STFT
    Author: Zander Blasingame """

import locale
import sys
import threading
import time

import stft
import Visualizer

# default setting for utf-8
locale.setlocale(locale.LC_ALL, '')

# Get command line arguments
use_log_scale = False

if len(sys.argv) > 1:
    if sys.argv[1] == 'log':
        use_log_scale = True


###############################################################################
#
# Functions
#
###############################################################################
# Handles input
def input_handler(vis, audio_proc):
    char = vis.get_ch()
    if char == -1:
        return

    char = chr(char)

    switcher = {
        'q': {'func': exit,
              'params': {'vis': vis, 'audio_proc': audio_proc}}
    }

    if char in list(switcher.keys()):
        entry = switcher[char]
        entry['func'](**entry['params'])


# exit function
def exit(vis, audio_proc):
    audio_proc.halt()
    vis.shut_down()
    sys.exit()


###############################################################################
#
# Main Method
#
###############################################################################
def main():
    # Audio processing class
    audio_proc = stft.STFT(7)

    # Visualizer
    vis = Visualizer.Visualizer()

    # Create and start audio thread
    audio_thread = threading.Thread(target=audio_proc.record_monitor)
    # vis_thread = threading.Thread(target=vis.render,
    #                               args=[audio_proc.get_stft])

    audio_thread.start()
    # vis_thread.start()

    while True:
        # listen for input keys
        input_handler(vis, audio_proc)

        # render
        vis.render(audio_proc.get_stft)

        time.sleep(0.025)

if __name__ == '__main__':
    main()
