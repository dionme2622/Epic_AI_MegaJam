import math
import random
import wave
import struct
from pathlib import Path

output = Path(__file__).resolve().parent
rate = 44100
rng = random.Random(49)
for name, duration, pulses in [
    ("FlyRatchet", .42, [(0,.18, 126),(.12,.19,96),(.22,.17,172)]),
    ("Recovery", 2.2, [(0,.32,164),(.2,.6,233),(.8,.7,329),(1.27,.8,440),(1.5,.62,659)]),
]:
    audio = []
    for n in range(int(rate*duration)):
        t = n/rate
        v = 0
        for start,length,pitch in pulses:
            d = t-start
            if 0 <= d < length:
                envelope = min(1,d*180) * (1-d/length)**2.6
                fundamental = math.sin(2*math.pi*d*pitch)
                metallic = math.sin(2*math.pi*d*pitch*2.7) * .18
                grain = rng.uniform(-.16,.16) if name=="FlyRatchet" else 0
                v += (fundamental*.38 + metallic + grain)*envelope*.62
        audio.append(int(max(-1,min(1,v))*32767))
    with wave.open(str(output/("S_Vault_"+name+".wav")),"wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(struct.pack(f"<{len(audio)}h",*audio))
