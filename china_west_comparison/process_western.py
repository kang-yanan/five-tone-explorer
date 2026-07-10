"""
Process downloaded Western tracks: trim 45s, normalize, 64kbps mono MP3.
Maps to west_01 ~ west_05 in order of emotional arousal (high → low).
"""
import subprocess, os, glob

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__)) + "/audio"
OUT_DIR = AUDIO_DIR + "/western_processed"
EMBED_DIR = AUDIO_DIR + "/embed25"
os.makedirs(OUT_DIR, exist_ok=True)

# Downloaded files → west_XX mapping (high arousal → low arousal)
# Order by emotional target
MAPPING = [
    ("west_01", "aggressive-hard-dark-trap-beat",        "high arousal: aggressive trap"),
    ("west_02", "energetic-cinematic-trap",              "mid-high: cinematic trap"),
    ("west_03", "dreaming-about-space-chill-hip-hop",     "neutral: chill lo-fi hip-hop"),
    ("west_04", "emotional-soul-lofi-rnb",               "mid-low: soulful R&B"),
    ("west_05", "celestial-drift-space-ambient",         "low arousal: ambient"),
]

def find_file(keyword):
    """Find the downloaded file matching keyword"""
    for f in glob.glob(f"{AUDIO_DIR}/*.mp3"):
        if keyword.lower() in os.path.basename(f).lower():
            return f
    # Search in subdirectories too
    for root, dirs, files in os.walk(AUDIO_DIR):
        for f in files:
            if f.endswith('.mp3') and keyword.lower() in f.lower():
                return os.path.join(root, f)
    return None

for name, keyword, desc in MAPPING:
    src = find_file(keyword)
    if not src:
        print(f"  NOT FOUND: {keyword}")
        continue

    wav_tmp = f"{OUT_DIR}/{name}_tmp.wav"
    wav_trim = f"{OUT_DIR}/{name}_trim.wav"
    mp3_out = f"{OUT_DIR}/{name}.mp3"

    # Step 1: Convert to WAV, trim first 10s, take 45s
    subprocess.run([
        "ffmpeg", "-y", "-i", src,
        "-ss", "10", "-t", "45",  # skip 10s intro, take 45s
        "-ac", "1", "-ar", "22050",
        wav_trim
    ], capture_output=True)

    # Step 2: Loudness normalize
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_trim,
        "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
        wav_tmp
    ], capture_output=True)

    # Step 3: Encode 64kbps mono MP3
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_tmp,
        "-ac", "1", "-ar", "22050", "-b:a", "64k",
        mp3_out
    ], capture_output=True)

    # Cleanup temp WAVs
    for tmp in [wav_tmp, wav_trim]:
        if os.path.exists(tmp):
            os.remove(tmp)

    # Copy to embed25 for CDN deployment
    dst = f"{EMBED_DIR}/{name}.mp3"
    import shutil
    shutil.copy(mp3_out, dst)

    size_kb = os.path.getsize(mp3_out) / 1024
    print(f"  {name}.mp3 — {desc} ({size_kb:.0f} KB)")

# Also clean up: remove old synthetic western files from embed25
for old in glob.glob(f"{EMBED_DIR}/west_0*.mp3"):
    os.remove(old)
    print(f"  Removed synthetic: {os.path.basename(old)}")

print(f"\nDone. Processed files in: {OUT_DIR}")
print(f"Copied to: {EMBED_DIR}")
