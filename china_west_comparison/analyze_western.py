"""
Analyze Western tracks to find the most representative 45-second excerpt.
Computes RMS energy, spectral centroid, and zero-crossing rate over time,
then recommends the best segment based on emotional target.
"""
import librosa, numpy as np, os, glob

SR = 22050
SEGMENT = 45  # seconds
AUDIO_DIR = os.path.dirname(os.path.abspath(__file__)) + "/audio"

TRACKS = [
    ("west_01", "aggressive-hard-dark-trap", "high arousal: peak energy + brightness"),
    ("west_02", "energetic-cinematic-trap", "mid-high: strong energy, less aggressive"),
    ("west_03", "dreaming-about-space", "neutral: steady, balanced, lo-fi"),
    ("west_04", "emotional-soul-lofi", "mid-low: warm, lower energy"),
    ("west_05", "celestial-drift-space", "low arousal: quietest, most ambient"),
]

def find_file(keyword):
    for f in glob.glob(f"{AUDIO_DIR}/*.mp3"):
        if keyword.lower() in os.path.basename(f).lower():
            return f
    return None

def analyze_track(filepath, target):
    y, sr = librosa.load(filepath, sr=SR)
    duration = len(y) / sr
    print(f"\n  Track: {os.path.basename(filepath)}")
    print(f"  Duration: {duration:.0f}s")

    # Compute features over time
    hop = int(SR * 0.5)  # 0.5s hop
    n_frames = (len(y) - SR * SEGMENT) // hop + 1
    if n_frames <= 0:
        print(f"  WARNING: Track shorter than {SEGMENT}s, using full track")
        return 0

    scores = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop
        end = start + int(SR * SEGMENT)
        seg = y[start:end]
        rms = np.mean(librosa.feature.rms(y=seg))
        cent = np.mean(librosa.feature.spectral_centroid(y=seg, sr=sr))
        zcr = np.mean(librosa.feature.zero_crossing_rate(seg))

        if target == "high":
            # Prefer high energy + high brightness
            scores[i] = rms * 0.4 + cent / 3000 * 0.4 + zcr * 0.2
        elif target == "mid-high":
            # High energy but slightly less extreme
            scores[i] = rms * 0.35 + cent / 3500 * 0.35 + zcr * 0.15
        elif target == "neutral":
            # Steady, balanced — prefer medium values
            scores[i] = -abs(rms - np.median([np.mean(librosa.feature.rms(y=y[start:start+int(SR*SEGMENT)])) for start in range(0, len(y)-int(SR*SEGMENT), hop)]))
            if len(scores) > 10: scores[i] += 0.01 * np.random.rand()
        elif target == "mid-low":
            # Low energy preferred
            scores[i] = (1 - rms) * 0.5 + (1 - zcr) * 0.3
        elif target == "low":
            # Lowest energy, lowest brightness
            scores[i] = (1 - rms) * 0.5 + (1 - cent / 5000) * 0.3 + (1 - zcr) * 0.2

    best_idx = np.argmax(scores)
    best_start = best_idx * hop / sr
    best_score = scores[best_idx]

    # Print top 3 candidates
    top3 = np.argsort(scores)[-3:][::-1]
    print(f"  Top 3 start times: {[f'{top3[j]*hop/sr:.0f}s (score={scores[t]:.3f})' for j, t in enumerate(top3)]}")
    print(f"  Recommended: start at {best_start:.0f}s, duration {SEGMENT}s")

    # Print segment features
    seg = y[int(best_start*sr):int(best_start*sr)+int(SR*SEGMENT)]
    print(f"  Segment RMS={np.mean(librosa.feature.rms(y=seg)):.3f}, Centroid={np.mean(librosa.feature.spectral_centroid(y=seg,sr=sr)):.0f}Hz, ZCR={np.mean(librosa.feature.zero_crossing_rate(seg)):.4f}")

    return best_start

for name, keyword, desc in TRACKS:
    fp = find_file(keyword)
    if not fp:
        print(f"  NOT FOUND: {keyword}")
        continue
    target_type = desc.split(":")[0].strip().split(" ")[0]  # "high", "mid-high", etc.
    if "high" in target_type and "mid" not in target_type: target_type = "high"
    elif "mid-high" in target_type: target_type = "mid-high"
    elif "neutral" in target_type: target_type = "neutral"
    elif "mid-low" in target_type: target_type = "mid-low"
    else: target_type = "low"
    start = analyze_track(fp, target_type)
    print(f"  → ffmpeg -i \"{fp}\" -ss {start:.0f} -t 45 -ac 1 -ar 22050 -b:a 64k {name}_best.mp3")

print("\nDone. Recommendations above.")
