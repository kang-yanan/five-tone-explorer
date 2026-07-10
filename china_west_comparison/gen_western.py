"""
Generate 5 synthetic Western-style tracks with controlled acoustic profiles.
Synthesizes audio with specific tempo, brightness, and noisiness parameters
to match 5 emotional targets: high arousal → low arousal.
Output: 45-second 64kbps mono MP3 files in audio/western/
"""
import numpy as np
import soundfile as sf
import os, subprocess

SR = 22050
DURATION = 45
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "western")
os.makedirs(OUT_DIR, exist_ok=True)

def sine(freq, duration, sr=SR):
    t = np.arange(int(sr * duration)) / sr
    return np.sin(2 * np.pi * freq * t)

def noise(duration, sr=SR):
    return np.random.randn(int(sr * duration))

def env_decay(n_samples, decay):
    return np.exp(-np.arange(n_samples) * decay)

def pitch_slide(start_freq, end_freq, duration, sr=SR):
    n = int(sr * duration)
    freqs = np.linspace(start_freq, end_freq, n)
    phase = 2 * np.pi * np.cumsum(freqs) / sr
    return np.sin(phase)

def normalize(y):
    return y / (np.max(np.abs(y)) + 1e-10)

def to_mp3(wav_path, mp3_path):
    subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-ac", "1", "-ar", str(SR), "-b:a", "64k", mp3_path],
                   capture_output=True)
    os.remove(wav_path)

def add_element(target, start_sample, waveform):
    """Safely add waveform to target at start_sample position."""
    end = min(start_sample + len(waveform), len(target))
    target[start_sample:end] += waveform[:end - start_sample]
    return target

def make_track(name, tempo_bpm, brightness, noisiness):
    """Generate one track with specified acoustic profile."""
    y = np.zeros(int(SR * DURATION))
    bp = 60.0 / tempo_bpm  # beat period in seconds

    if brightness == "high":
        # Fast percussive beats + bright synth
        n_beats = int(DURATION / bp)
        for i in range(n_beats):
            st = int(i * bp * SR)
            # kick
            d = min(int(0.12 * SR), len(y) - st)
            if d > 0:
                y[st:st+d] += sine(55, d/SR)[:d] * env_decay(d, 0.025) * 0.5
            # snare on backbeats
            if i % 2 == 1:
                sd = min(int(0.08 * SR), len(y) - st)
                if sd > 0:
                    y[st:st+sd] += noise(sd/SR)[:sd] * env_decay(sd, 0.05) * 0.3
        # Bright synth pad
        pad = sine(880, DURATION) * 0.06 + sine(1320, DURATION) * 0.04 + sine(1760, DURATION) * 0.02
        pad *= np.linspace(0, 1, len(pad))
        pad *= np.linspace(1, 0.3, len(pad))
        y += pad
        if noisiness == "high":
            y += noise(DURATION) * 0.06

    elif brightness == "medium":
        n_beats = int(DURATION / bp)
        for i in range(n_beats):
            st = int(i * bp * SR)
            d = min(int(0.15 * SR), len(y) - st)
            if d > 0:
                y[st:st+d] += sine(80, d/SR)[:d] * env_decay(d, 0.015) * 0.35
        # Mid-range pad
        for f in [330, 440, 523]:
            y += sine(f, DURATION) * 0.04
        y *= np.linspace(0.3, 1, len(y))
        y *= np.linspace(1, 0.5, len(y))
        if noisiness == "medium":
            y += noise(DURATION) * 0.03

    else:  # low brightness
        n_beats = int(DURATION / bp)
        for i in range(0, n_beats, 2):
            st = int(i * bp * SR)
            d = min(int(0.25 * SR), len(y) - st)
            if d > 0:
                y[st:st+d] += sine(45, d/SR)[:d] * env_decay(d, 0.01) * 0.25
        # Low warm pad
        for f in [131, 165, 196]:
            y += sine(f, DURATION) * 0.05
        y *= np.linspace(0.5, 1, len(y))
        y *= np.linspace(1, 0.7, len(y))

    y = normalize(y)
    wav = os.path.join(OUT_DIR, f"{name}.wav")
    mp3 = os.path.join(OUT_DIR, f"{name}.mp3")
    sf.write(wav, y, SR)
    to_mp3(wav, mp3)
    print(f"  {name}.mp3 — {tempo_bpm}BPM, bright={brightness}, noise={noisiness}")

print("Generating 5 Western tracks...")
make_track("west_01", 140, "high",   "high")    # Aggressive trap
make_track("west_02", 110, "high",   "medium")  # Melodic rap
make_track("west_03",  90, "medium", "medium")  # Lo-fi hip-hop
make_track("west_04",  75, "medium", "low")     # Soulful R&B
make_track("west_05",  60, "low",    "low")     # Ambient
print(f"\nDone. Files in: {OUT_DIR}")
