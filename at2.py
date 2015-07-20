from array import array
import pyaudio

chunk = 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22100
VOLUME = 6000


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=chunk)

print "* recording"
while True:
    for i in range(0, 22100 / chunk):
        data = array('h', stream.read(chunk))
        vol = max(data)
        if vol > VOLUME:
            print vol,


print "* done"

stream.stop_stream()
stream.close()
p.terminate()
