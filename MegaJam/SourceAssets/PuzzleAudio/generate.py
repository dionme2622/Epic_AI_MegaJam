"""Render the original 48 kHz mono foley and feedback cues for Director's Cut."""

import array
import math
from pathlib import Path
import random
import sys
import wave


RATE = 48_000
OUTPUT = Path(__file__).resolve().parent


class Cue:
    def __init__(self, name, duration, peak):
        self.name = name
        self.samples = [0.0] * round(RATE * duration)
        self.rng = random.Random(name)
        self.peak = peak

    def ring(self, start, duration, pitch, gain, modes=(1., 2.03, 3.17), slide=0., decay=5.):
        offset = round(start * RATE)
        count = min(round(duration * RATE), len(self.samples) - offset)
        for n in range(count):
            t = n / RATE
            u = t / duration
            phase = math.tau * pitch * t * (1. + slide * u / 2.)
            voice = sum(math.sin(phase * mode) / (index + 1.) ** 1.75
                        for index, mode in enumerate(modes))
            envelope = min(1., t / .003) * math.exp(-decay * u) * (1. - u)
            self.samples[offset + n] += gain * envelope * voice

    def scrape(self, start, duration, gain, color, tail=2.2, flutter=0.):
        offset = round(start * RATE)
        count = min(round(duration * RATE), len(self.samples) - offset)
        low = high = 0.0
        for n in range(count):
            t = n / RATE
            u = t / duration
            noise = self.rng.uniform(-1., 1.)
            high += (noise - high) * color
            low += (noise - low) * (color * .16)
            envelope = min(1., t / .009) * (1. - u) ** tail
            modulation = .72 + .28 * math.cos(math.tau * flutter * t) if flutter else 1.
            self.samples[offset + n] += gain * (high - low) * envelope * modulation

    def ticks(self, times, pitch, gain):
        for index, t in enumerate(times):
            self.ring(t, .095, pitch * (1. + .07 * (index % 3)), gain, (1., 2.41, 3.91), -.15)
            self.scrape(t, .031, gain * .31, .34)

    def chord(self, start, pitches, gain):
        for index, pitch in enumerate(pitches):
            self.ring(start + index * .057, .37, pitch, gain / (1. + index * .10), (1., 2.005, 3.99), 0., 2.8)

    def save(self, *, loop=False):
        peak = max(map(abs, self.samples))
        assert peak > .01, self.name
        scale = 32767 * self.peak / peak
        if loop:
            pcm = array.array('h', (round(v * scale) for v in self.samples))
        else:
            assert self.samples[0] == 0., self.name
            fade = round(.012 * RATE)
            end = len(self.samples) - 1
            pcm = array.array('h', (round(v * scale * min(1., (end - n) / fade))
                                    for n, v in enumerate(self.samples)))
        if sys.byteorder == 'big':
            pcm.byteswap()
        with wave.open(str(OUTPUT / f'SFX_Puzzle_{self.name}.wav'), 'wb') as out:
            out.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
            out.writeframes(pcm.tobytes())


def render_chair_roll():
    c = Cue('ChairRoll', 2.5, .17)
    count = len(c.samples)
    noise = [c.rng.uniform(-1., 1.) for _ in c.samples]
    grit = body = rumble = 0.
    # Prime the filters using the end of the same noise before writing the loop.
    for n in range(-round(.18 * RATE), count):
        sample = noise[n]
        grit += .16 * (sample - grit)
        body += .040 * (sample - body)
        rumble += .006 * (sample - rumble)
        if n < 0:
            continue

        phase = math.tau * n / count
        tread = .5 + .5 * math.cos(9. * phase + .51 * math.sin(2. * phase))
        axle_load = .5 + .5 * math.cos(5. * phase + .74 * math.sin(3. * phase))
        bearing = math.sin(263. * phase + 1.2 * math.sin(8. * phase))
        stone_friction = (.78 + .22 * tread) * (.48 * (grit - body) + .89 * (body - rumble))
        c.samples[n] = stone_friction + .27 * rumble + .018 * axle_load ** 3 * bearing

    # Start at a quiet crossing so the initial playback also starts cleanly.
    start = min(range(1, RATE // 12), key=lambda n: abs(c.samples[n - 1]) + abs(c.samples[n]))
    c.samples = c.samples[start:] + c.samples[:start]
    c.save(loop=True)


def render():
    c = Cue('ControlTick', .105, .145)
    c.ticks([0], 406, .26)
    c.save()

    c = Cue('ChairEquip', .49, .27)
    c.scrape(0, .25, .24, .067, 1.8)
    c.ring(.055, .28, 86, .48, (1., 1.85, 2.51), -.18)
    c.ticks([.13, .20, .25], 341, .25)
    c.save()

    c = Cue('WheelLatch', .34, .25)
    c.ring(0, .31, 96, .65, (1., 1.63, 2.77), -.31)
    c.ticks([.023, .092], 208, .35)
    c.scrape(0, .13, .53, .12)
    c.save()

    c = Cue('LiftStart', .68, .34)
    c.ring(.023, .58, 64, .44, (1., 1.98, 3.3), .35, 2.4)
    c.ticks([0, .138, .207, .267, .326, .374], 151, .23)
    c.scrape(.04, .59, .54, .09, 1.8, 22.)
    c.save()

    c = Cue('LiftLock', .49, .32)
    c.ticks([0, .07, .17], 179, .36)
    c.ring(.08, .39, 79, .62, (1., 2.22, 3.54), -.18)
    c.ring(.17, .31, 393, .13)
    c.save()

    c = Cue('HeroLegs', .72, .32)
    c.ticks([0, .046, .15, .23], 359, .33)
    c.scrape(0, .30, .32, .15, 1.4)
    c.chord(.20, (392, 523.25, 659.25), .16)
    c.save()

    c = Cue('FocusMove', .147, .17)
    c.ticks([0, .038], 471, .18)
    c.scrape(0, .09, .27, .37)
    c.save()

    c = Cue('FocusLock', .73, .37)
    c.ticks([0, .09], 338, .33)
    c.chord(.115, (493.88, 659.25, 783.99, 987.77), .22)
    c.save()

    c = Cue('TakeRecord', .38, .28)
    c.ticks([0, .049, .122], 299, .28)
    c.scrape(.041, .29, .49, .21, .95, 34.)
    c.ring(.093, .23, 117, .12, (1., 2.7), .15)
    c.save()

    c = Cue('TakeReplay', .53, .29)
    c.ring(0, .42, 185, .34, (1., 1.51, 2.02), -.55, 2.4)
    c.scrape(0, .48, .37, .21, 1.45, 28.)
    c.ticks([.056, .15, .215, .258, .287], 279, .17)
    c.save()

    c = Cue('TakeLock', .72, .35)
    c.ring(0, .26, 111, .42, (1., 2.41, 3.2), -.22)
    c.ticks([.023, .108], 338, .22)
    c.chord(.15, (392, 523.25, 783.99), .22)
    c.save()

    c = Cue('FilmNotch', .145, .19)
    c.ticks([0, .045], 616, .24)
    c.scrape(.013, .098, .30, .45)
    c.save()

    c = Cue('FilmLock', .83, .36)
    c.ticks([0, .049, .10, .16], 269, .23)
    c.scrape(0, .27, .27, .16, 1.8, 24.)
    c.chord(.16, (349.23, 466.16, 698.46, 880), .22)
    c.save()

    c = Cue('ArchiveCrate', .64, .28)
    c.ticks([0, .084], 282, .29)
    c.ring(.077, .33, 105, .52, (1., 1.69, 2.43), .13)
    c.scrape(.112, .46, .44, .078, 1.6, 12.)
    c.save()

    c = Cue('RgbDial', .157, .175)
    c.ticks([0], 342, .22)
    c.ring(.024, .13, 592, .13, (1., 2.17), .15, 3.5)
    c.save()

    c = Cue('RgbLock', .71, .35)
    c.ticks([0], 437, .29)
    c.chord(.063, (392, 493.88, 587.33, 783.99), .20)
    c.save()

    c = Cue('LampAim', .30, .19)
    c.scrape(0, .25, .47, .085, 1.4, 19.)
    c.ticks([.017, .08, .17], 227, .18)
    c.ring(.02, .22, 103, .16, (1., 1.85, 3.14), -.13)
    c.save()

    c = Cue('RetakeLock', .53, .35)
    c.scrape(0, .07, .55, .49)
    c.ring(0, .15, 184, .44, (1., 1.52, 2.59), -.15)
    c.ticks([.09, .177, .22], 211, .28)
    c.ring(.21, .29, 92, .41, (1., 1.8, 3.14), -.24)
    c.save()

    c = Cue('StandSwitch', .23, .22)
    c.ticks([0, .043], 386, .28)
    c.ring(.034, .18, 680, .12, (1., 2.02), .07, 3.1)
    c.save()

    c = Cue('FerryMotor', .74, .29)
    c.ticks([0, .10, .197, .295], 179, .23)
    c.scrape(.035, .66, .62, .08, 1.18, 27.)
    c.ring(.04, .64, 54, .39, (1., 2.2, 3.75), .25, 2.1)
    c.save()

    c = Cue('BridgeLock', .77, .35)
    c.ticks([0, .08, .158, .244], 188, .25)
    c.scrape(0, .46, .44, .09, 1.52, 16.)
    c.ring(.21, .46, 74, .53, (1., 1.91, 2.61), -.22)
    c.ring(.302, .41, 349.23, .16, (1., 2.01, 3.5))
    c.save()

    c = Cue('CrawlStep', .205, .155)
    c.ring(0, .14, 86, .40, (1., 1.73, 2.67), -.28)
    c.scrape(.009, .18, .54, .105, 1.5)
    c.ticks([.046], 326, .095)
    c.save()

    render_chair_roll()

    c = Cue('HeroStep', .218, .194)
    c.ring(0, .158, 109, .26, (1., 1.89, 2.71), -.32)
    c.ticks([.01, .046], 438, .19)
    c.ring(.053, .14, 391, .18, (1., 1.61, 3.91), -.16)
    c.scrape(0, .088, .27, .27, 2.2)
    c.save()

    c = Cue('DragonStep', .232, .206)
    c.ring(0, .211, 76, .56, (1., 1.60, 2.48), -.33, 4.5)
    c.scrape(.007, .15, .48, .14, 2.2)
    c.ticks([.036, .056], 313, .105)
    c.save()


if __name__ == '__main__':
    render()
