"""Tạo nhạc nền tự tổng hợp (không dùng nhạc của bên thứ ba): piano rải hợp âm chậm + pad + bass, có vang.

  python tools/tao_nhac_nen.py channels/kigyo_shi/assets/nhac_nen.wav [--bpm 64] [--seed 4]

Bản nhạc dài đúng số ô nhịp và vang được tính vòng tròn, nên engine lặp lại (stream_loop) không bị hụt ở chỗ nối.
"""
import argparse
import wave

import numpy as np

SR = 44100
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
# Hợp âm (gốc, các nốt tính theo nửa cung từ gốc). Giọng thứ, buồn nhẹ và trang trọng.
PROG = [("A", (0, 3, 7)), ("F", (0, 4, 7)), ("C", (0, 4, 7)), ("G", (0, 4, 7)),
        ("D", (0, 3, 7)), ("A", (0, 3, 7)), ("E", (0, 5, 7)), ("E", (0, 4, 7))]


def hz(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def piano(f, dur, vel):
    t = np.arange(int(SR * dur)) / SR
    tone = np.zeros_like(t)
    for k, a in enumerate((1.0, .45, .22, .12, .06, .03), start=1):
        fk = f * k * (1 + .0004 * k * k)          # hơi lệch bội âm như dây đàn
        tone += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.1 + .7 * k))
    env = np.minimum(1, t / .006)
    return vel * tone * env


def pad(freqs, dur):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            out += np.sin(2 * np.pi * (f * (1 + det / 100)) * t + det * 7)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.2)
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t)
    return out * env * lfo / (3 * len(freqs))


def add(buf, sig, start):
    i = int(start * SR) % len(buf)
    n = len(sig)
    if i + n <= len(buf):
        buf[i:i + n] += sig
    else:                                          # tràn qua cuối thì vòng về đầu (để lặp liền)
        k = len(buf) - i
        buf[i:] += sig[:k]
        buf[:n - k] += sig[k:]


def reverb_circular(x, seconds=2.6, mix=.28, seed=0):
    rng = np.random.default_rng(seed)
    n = int(SR * seconds)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR / (seconds / 5))
    ir /= np.sqrt((ir ** 2).sum())
    h = np.zeros(len(x))
    h[:n] = ir
    wet = np.real(np.fft.ifft(np.fft.fft(x) * np.fft.fft(h)))
    return (1 - mix) * x + mix * wet


def lowpass(x, cutoff=3200):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def compose(bpm=64, loops=4, seed=4):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    bar = 4 * beat
    total = bar * len(PROG) * loops
    L = np.zeros(int(SR * total))
    R = np.zeros_like(L)
    for b in range(len(PROG) * loops):
        root, ivs = PROG[b % len(PROG)]
        t0 = b * bar
        base = hz(root, 3)
        chord = [base * 2 ** (i / 12) for i in ivs]
        # bass: nốt gốc kéo dài
        bass = piano(hz(root, 2), bar * 1.1, .55)
        add(L, bass, t0)
        add(R, bass, t0)
        # pad: chồng hợp âm ở quãng giữa
        p = pad([f * 2 for f in chord], bar + .8) * .5
        add(L, p, t0 - .2)
        add(R, p, t0 - .2)
        # piano rải: 8 nốt móc đơn, lên rồi xuống, nhẹ dần ở phách yếu
        arp = [chord[0] * 2, chord[1] * 2, chord[2] * 2, chord[0] * 4, chord[2] * 2, chord[1] * 2, chord[2] * 2, chord[1] * 2]
        section = (b // len(PROG)) % loops
        for j, f in enumerate(arp):
            if section == 0 and j % 2:              # vòng đầu thưa hơn
                continue
            vel = (.32 if j % 4 == 0 else .2) * (0.9 + .2 * rng.random())
            pan = .5 + .25 * np.sin(j)
            s = piano(f, 2.4, vel)
            tt = t0 + j * beat / 2 + rng.normal(0, .006)
            add(L, s * (1 - pan) * 2, tt)
            add(R, s * pan * 2, tt)
        # giai điệu thưa ở vòng 3 và 4
        if section >= 2 and b % 2 == 0:
            mel = chord[rng.integers(0, 3)] * 4
            s = piano(mel, 3.0, .26)
            add(L, s, t0 + beat * rng.choice([0, 1, 2]))
            add(R, s, t0 + beat * rng.choice([0, 1, 2]))
    L, R = lowpass(reverb_circular(L, seed=1)), lowpass(reverb_circular(R, seed=2))
    peak = max(np.abs(L).max(), np.abs(R).max())
    g = 10 ** (-3 / 20) / peak
    return np.stack([L * g, R * g], axis=1), total


def write_wav(path, stereo):
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bpm", type=float, default=64)
    ap.add_argument("--seed", type=int, default=4)
    a = ap.parse_args()
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    audio, sec = compose(a.bpm, seed=a.seed)
    write_wav(a.out, audio)
    print(f"Ghi {a.out}: {sec:.1f} giây, lặp liền")
