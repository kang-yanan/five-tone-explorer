"""Process new Western classical tracks: 45s trim, 44100Hz mono 64kbps."""
import os, subprocess, shutil

SRC = r"E:\0. Sumhs\2 教研\曲库\西式五音"
DST = r"F:\Claude project\five_tone_experiment\china_west_comparison\audio\embed25"

# Select one representative track per mode folder
# Picking the more emotionally distinctive piece from each pair
SELECTIONS = [
    ("宫调", "欢乐颂.mp3", "Ode to Joy — uplifting, grand"),
    ("商调", "小夜曲第一乐章.mp3", "Serenade — introspective, gentle"),
    ("角调", "月光奏鸣曲.mp3", "Moonlight Sonata — flowing, melancholic"),
    ("徵调", "花之圆舞曲.mp3", "Waltz of the Flowers — exciting, bright"),
    ("羽调", "吉姆诺佩蒂第一首.mp3", "Gymnopédie — quiet, sparse"),
]

for i, (folder, filename, desc) in enumerate(SELECTIONS, 1):
    src = os.path.join(SRC, folder, filename)
    dst = os.path.join(DST, f"west_0{i}.mp3")
    # Trim to 45s from 10s in (skip intro), 44100Hz mono 64kbps
    subprocess.run([
        "ffmpeg", "-y", "-i", src,
        "-ss", "10", "-t", "45",
        "-ac", "1", "-ar", "44100", "-b:a", "64k",
        dst
    ], capture_output=True)
    size_kb = os.path.getsize(dst) / 1024
    print(f"west_0{i}.mp3 — {desc} ({size_kb:.0f} KB)")

# Verify sample rates
print("\nVerification:")
for i in range(1, 6):
    dst = os.path.join(DST, f"west_0{i}.mp3")
    result = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "stream=sample_rate", "-of", "default=noprint_wrappers=1:nokey=1", dst], capture_output=True, text=True)
    print(f"  west_0{i}.mp3: {result.stdout.strip()}Hz, {os.path.getsize(dst)//1024}KB")

print("\nDone. Ready to deploy.")
