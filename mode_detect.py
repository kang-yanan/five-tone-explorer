#!/usr/bin/env python3
"""
五声调式自动检测：基于 librosa 主音检测
Method: pitch histogram + chroma template matching → tonic → pentatonic mode
"""
import librosa
import numpy as np
import json
import os
import sys

AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"
SR = 22050
PENTATONIC_INTERVALS = [0, 2, 4, 7, 9]  # semitones: do re mi sol la

# Track list with filenames
TRACKS = [
    # Gong pool
    ("gong_01", "平湖秋月"), ("gong_02", "浏阳河"), ("gong_03", "紫竹调"),
    ("gong_04", "花三六"), ("gong_05", "踏雪寻梅"),
    # Shang pool
    ("shang_01", "十面埋伏"), ("shang_02", "广陵散"), ("shang_03", "拔根芦柴花"),
    ("shang_05", "阳关三叠"),
    # Jue pool
    ("jue_01", "列子御风"), ("jue_02", "姑苏行"), ("jue_03", "胡笳十八拍"),
    ("jue_04", "花好月圆"), ("jue_05", "霓裳曲"),
    # Zhi pool
    ("zhi_01", "喜洋洋"), ("zhi_02", "新春乐"), ("zhi_03", "春节序曲"),
    ("zhi_04", "步步高"), ("zhi_05", "解放军进行曲"),
    # Yu pool
    ("yu_01", "乌夜啼"), ("yu_02", "二泉映月"), ("yu_03", "寒鸦戏水"),
    ("yu_04", "梁祝"), ("yu_05", "江河水"),
]

MODE_NAMES = {0: "宫 Gōng", 2: "商 Shāng", 4: "角 Jué", 7: "徵 Zhǐ", 9: "羽 Yǔ"}
MODE_KEYS = {0: "gong", 2: "shang", 4: "jue", 7: "zhi", 9: "yu"}

def detect_tonic_pitch_histogram(y, sr):
    """Method 1: Pitch tracking → pitch class histogram → tonic"""
    try:
        # Use pYIN for fundamental frequency estimation
        f0, voiced_flag, voiced_prob = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'), sr=sr
        )
        # Filter voiced frames with high confidence
        mask = (voiced_flag & (voiced_prob > 0.7))
        if mask.sum() < 100:
            # Fallback: use piptrack
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr, fmin=80, fmax=2000)
            pitches = pitches[magnitudes > np.median(magnitudes)]
        else:
            pitches = f0[mask]

        if len(pitches) < 50:
            return None

        # Convert Hz to MIDI note numbers
        midi = librosa.hz_to_midi(pitches)
        # Get pitch class (0=C, 1=C#, ... 11=B)
        pitch_class = np.round(midi) % 12
        # Build histogram
        hist = np.bincount(pitch_class.astype(int), minlength=12)

        # Find dominant pitch class
        tonic_candidate = np.argmax(hist)
        confidence = hist[tonic_candidate] / hist.sum()
        return {"tonic_pc": int(tonic_candidate), "confidence": float(confidence),
                "hist": hist.tolist(), "method": "pYIN+pitch_histogram"}
    except Exception as e:
        return {"error": str(e), "method": "pYIN+pitch_histogram"}


def detect_tonic_chroma_template(y, sr):
    """Method 2: Chroma CQT → pentatonic template matching → tonic"""
    try:
        # Chroma from CQT (better for music)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=12)
        mean_chroma = chroma.mean(axis=1)  # average over time
        # Normalize
        mean_chroma = mean_chroma / (mean_chroma.sum() + 1e-10)

        # For each possible tonic pitch class (0-11), create pentatonic template
        # and compute correlation
        scores = np.zeros(12)
        for tonic in range(12):
            template = np.zeros(12)
            for interval in PENTATONIC_INTERVALS:
                template[(tonic + interval) % 12] = 1.0
            template = template / template.sum()
            # Correlation between template and observed chroma
            scores[tonic] = np.corrcoef(template, mean_chroma)[0, 1]

        best_tonic = np.argmax(scores)
        return {"tonic_pc": int(best_tonic), "confidence": float(scores[best_tonic]),
                "scores": [float(s) for s in scores], "method": "chroma_template"}
    except Exception as e:
        return {"error": str(e), "method": "chroma_template"}


def detect_tonic_ending(y, sr):
    """Method 3: Check the ending segment — tonic often = last prominent note"""
    try:
        # Analyze last 5 seconds
        end_samples = min(5 * sr, len(y))
        y_end = y[-end_samples:]

        # Pitch track on ending
        f0, vf, vp = librosa.pyin(y_end, fmin=librosa.note_to_hz('C2'),
                                   fmax=librosa.note_to_hz('C7'), sr=sr)
        mask = (vf & (vp > 0.5))
        if mask.sum() < 5:
            return None

        pitches_end = f0[mask]
        midi_end = librosa.hz_to_midi(pitches_end)
        pc_end = np.round(midi_end).astype(int) % 12
        hist = np.bincount(pc_end, minlength=12)
        if hist.sum() == 0:
            return None
        ending_tonic = np.argmax(hist)
        return {"tonic_pc": int(ending_tonic), "confidence": float(hist[ending_tonic]/hist.sum()),
                "method": "ending_segment"}
    except Exception as e:
        return {"error": str(e), "method": "ending_segment"}


def consensus(results):
    """Combine multiple detection methods, return consensus tonic"""
    valid = [r for r in results if r and "error" not in r]
    if not valid:
        return None, None, "all_methods_failed"

    # Weighted vote by confidence
    votes = np.zeros(12)
    for r in valid:
        votes[r["tonic_pc"]] += r.get("confidence", 0.5)

    tonic = int(np.argmax(votes))
    # Determine pentatonic mode: position of tonic in the pentatonic set
    tonic_interval = tonic % 12
    # Find which pentatonic interval this tonic corresponds to
    # The mode tells us the role of the tonic in the pentatonic system
    # If tonic is the root of the pentatonic scale → 宫
    # We need to find the best fitting pentatonic "key"

    # For each possible 宫 (root of the pentatonic scale), compute fit
    pentatonic_fits = {}
    for gong_pc in range(12):
        pent_set = {(gong_pc + i) % 12 for i in PENTATONIC_INTERVALS}
        # Compute chroma energy on pentatonic notes
        energy = 0
        if valid:
            # Use the histogram from first valid method
            for r in valid:
                if "hist" in r:
                    for pc in pent_set:
                        energy += r["hist"][pc]
                    break
        pentatonic_fits[gong_pc] = energy

    best_gong = max(pentatonic_fits, key=pentatonic_fits.get)

    # Now determine the mode: relationship between tonic and 宫
    # interval from 宫 to tonic
    interval = (tonic - best_gong) % 12

    if interval in MODE_NAMES:
        mode_name = MODE_NAMES[interval]
        mode_key = MODE_KEYS[interval]
    else:
        # Find closest pentatonic interval
        closest = min(PENTATONIC_INTERVALS, key=lambda x: abs(x - interval))
        mode_name = MODE_NAMES.get(closest, f"unknown_int={interval}")
        mode_key = MODE_KEYS.get(closest, "unknown")

    # Pitch names for display
    pitch_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    tonic_name = pitch_names[tonic]
    gong_name = pitch_names[best_gong]

    return {
        "tonic_pc": tonic,
        "tonic_name": tonic_name,
        "gong_pc": best_gong,
        "gong_name": gong_name,
        "mode_interval": interval,
        "mode": mode_key,
        "mode_name": mode_name,
        "confidence": float(np.mean([r.get("confidence", 0) for r in valid])),
        "methods_used": [r["method"] for r in valid],
        "method_details": valid
    }


def main():
    results = {}
    for filename, track_name in TRACKS:
        filepath = os.path.join(AUDIO_DIR, filename + ".mp3")
        if not os.path.exists(filepath):
            print(f"  SKIP {filename} ({track_name}): file not found", file=sys.stderr)
            results[filename] = {"name": track_name, "error": "file_not_found"}
            continue

        print(f"  Analyzing {filename} ({track_name})...", file=sys.stderr)
        try:
            y, sr = librosa.load(filepath, sr=SR, duration=50)  # Load up to 50s

            r1 = detect_tonic_pitch_histogram(y, sr)
            r2 = detect_tonic_chroma_template(y, sr)
            r3 = detect_tonic_ending(y, sr)

            cons = consensus([r1, r2, r3])

            results[filename] = {
                "name": track_name,
                "tonic": cons["tonic_name"] if cons else None,
                "gong": cons["gong_name"] if cons else None,
                "mode": cons["mode"] if cons else None,
                "mode_name": cons["mode_name"] if cons else None,
                "confidence": cons["confidence"] if cons else 0,
                "pitch_hist": r1,
                "chroma_template": r2,
                "ending": r3
            }
            print(f"    → {track_name}: tonic={cons['tonic_name']}, "
                  f"宫={cons['gong_name']}, mode={cons['mode_name']} "
                  f"(conf={cons['confidence']:.3f})", file=sys.stderr)
        except Exception as e:
            print(f"    ERROR: {e}", file=sys.stderr)
            results[filename] = {"name": track_name, "error": str(e)}

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
