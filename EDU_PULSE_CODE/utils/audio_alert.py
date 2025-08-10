import sys
import os
from config import BEEP_FREQ, BEEP_DURATION

if sys.platform == "win32":
    import winsound

    def beep():
        winsound.Beep(BEEP_FREQ, BEEP_DURATION)
else:
    def beep():
        os.system(f'play -nq -t alsa synth {BEEP_DURATION / 1000} sine {BEEP_FREQ}')
