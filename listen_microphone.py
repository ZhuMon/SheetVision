#! /usr/bin/env python

# Use pyaudio to open the microphone and run aubio.pitch on the stream of
# incoming samples. If a filename is given as the first argument, it will
# record 5 seconds of audio to this location. Otherwise, the script will
# run until Ctrl+C is pressed.


import pyaudio
import sys
import numpy as np
import aubio

# todo sheet
todo_sheet = [44, 51, 56, 60, 61, 61, 63]

class ListenMusic():
    def __init__(self):
        self.setup_pyaudio()

    def setup_pyaudio(self):
        # initialise pyaudio
        self.p = pyaudio.PyAudio()

        # open stream
        self.buffer_size = 1024
        pyaudio_format = pyaudio.paFloat32
        n_channels = 1
        samplerate = 44100
        self.stream = self.p.open(format=pyaudio_format,
                        channels=n_channels,
                        rate=samplerate,
                        input=True,
                        frames_per_buffer=self.buffer_size)

        # setup pitch
        tolerance = 0.8
        win_s = 4096 # fft size
        hop_s = self.buffer_size # hop size
        self.pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
        self.pitch_o.set_unit("midi")
        self.pitch_o.set_tolerance(tolerance)

    def start_listen(self, target_pitch):
        while True:
            try:
                audiobuffer = self.stream.read(self.buffer_size)
                signal = np.fromstring(audiobuffer, dtype=np.float32)

                pitch = self.pitch_o(signal)[0]
                confidence = self.pitch_o.get_confidence()

                # if pitch != 0:
                # print("{} / {}".format(pitch,confidence))
                if round(pitch) == target_pitch:
                    return True


            except KeyboardInterrupt:
                print("*** Ctrl+C pressed, exiting")
                break
        self.close() 
        return False

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# print("*** done recording")
if __name__ == "__main__":
    l = ListenMusic()
    for n in todo_sheet:
        print("play", n)
        if l.start_listen(n):
            print("nice!")
            continue
        else:
            break
