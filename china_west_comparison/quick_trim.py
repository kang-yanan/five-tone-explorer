"""Quick trim: scan every 2s, find best 45s excerpt, re-encode."""
import librosa, numpy as np, os, glob, subprocess

SR, SEG = 11025, 45  # half-res for speed
AUDIO = os.path.dirname(os.path.abspath(__file__)) + "/audio"
OUT = AUDIO + "/embed25"

TRACKS = [
    ("west_01", "aggressive-hard-dark", "high", "peak energy + brightness"),
    ("west_02", "energetic-cinematic", "mid", "strong but less aggressive"),
    ("west_03", "dreaming-about-space", "balanced", "steady lo-fi groove"),
    ("west_04", "emotional-soul-lofi", "low", "warm, soulful mid-low"),
    ("west_05", "celestial-drift-space", "quiet", "most ambient, lowest energy"),
]

def find(keyword):
    for f in glob.glob(f"{AUDIO}/*.mp3"):
        if keyword.lower() in os.path.basename(f).lower(): return f
    return None

for name, kw, style, desc in TRACKS:
    fp = find(kw)
    if not fp: print(f"  SKIP {name}: not found"); continue

    y, sr = librosa.load(fp, sr=SR)
    dur = len(y)/sr
    print(f"\n{name}: {dur:.0f}s total")

    # Scan every 2 seconds
    hop = int(SR*2)
    n_frames = max(1, (len(y) - SR*SEG) // hop + 1)
    scores = np.zeros(n_frames)
    for i in range(n_frames):
        s = y[i*hop : i*hop + SR*SEG]
        rms = np.sqrt(np.mean(s**2))
        cent = np.mean(librosa.feature.spectral_centroid(y=s, sr=sr))
        if style == "high": scores[i] = rms*0.5 + cent/2000*0.5
        elif style == "mid": scores[i] = rms*0.4 + cent/2500*0.4
        elif style == "balanced": scores[i] = -abs(rms - np.median(scores)) if n_frames>5 else rms*0.3
        elif style == "low": scores[i] = -rms
        else: scores[i] = -(rms + cent/3000)

    best = int(np.argmax(scores) * hop / sr)
    print(f"  Best start: {best}s (score={scores.max():.3f})")
    alt_starts = sorted(range(n_frames), key=lambda i: scores[i], reverse=True)[:3]
    print(f"  Alt starts: {[f'{int(alt_starts[j]*hop/sr)}s'for j in range(min(3,len(alt_starts)))]}")

    # Re-encode
    dst = f"{OUT}/{name}.mp3"
    subprocess.run(["ffmpeg","-y","-i",fp,"-ss",str(best),"-t","45","-ac","1","-ar","22050","-b:a","64k",dst],capture_output=True)
    print(f"  → {dst} ({os.path.getsize(dst)//1024}KB)")

print("\nDone.")
