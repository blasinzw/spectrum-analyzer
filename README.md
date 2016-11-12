# Spectrum Analyzer
This is a audio visualizer written in Python designed to be run in the command line. This was designed using the curses library along with the NumPy, SciPy, and PyAudio libraries in Python 3.5.2. This was designed to work with PulseAudio; it has yet to be tested with anything else. 

## Setup
Add the following lines to either ```/etc/asound.conf``` or ```~/.asoundrc```:
```
pcm.pulse_monitor {
  type pulse
  device alsa_output.pci-0000_00_1b.0.analog-stereo.monitor
}

ctl.pulse_monitor {
  type pulse
  device alsa_output.pci-0000_00_1b.0.analog-stereo.monitor
}
```

## Execution
To run the program simply type the following command into the terminal once inside the project directory
```
python main.py
```

## Options
During the runtime of the program pressing the ```o``` key will display the signal in an octave scale, $log_2$. Similarly, pressing the ```l``` and ```i``` key will display the signal in log and linear scales respectively. Pressing the ```q``` key will close the program.

## Screenshot
The following figure is a screenshot of the program running on my computer
![Alt text](/images/screenshot_1.png)
