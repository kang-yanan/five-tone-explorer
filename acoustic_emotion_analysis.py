"""
Acoustic feature extraction + emotion correlation analysis
Extract objective acoustic features from 24 tracks,
correlate with 50 participants' emotional ratings.
"""
import librosa
import numpy as np
import json
import os
import sys

# Fix Unicode encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"
SR = 22050

TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

def extract_features(filepath):
    """Extract comprehensive acoustic features from an audio file"""
    y, sr = librosa.load(filepath, sr=SR, duration=50)

    features = {}

    # 1. Tempo
    try:
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo.item()) if hasattr(tempo, 'item') else float(tempo)
    except:
        features['tempo'] = 0.0

    # 2. Spectral centroid
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    if centroid.size > 0:
        features['centroid_mean'] = float(np.mean(centroid))
        features['centroid_std'] = float(np.std(centroid))
    else:
        features['centroid_mean'] = 0.0
        features['centroid_std'] = 0.0

    # 3. Spectral bandwidth
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    if bandwidth.size > 0:
        features['bandwidth_mean'] = float(np.mean(bandwidth))
        features['bandwidth_std'] = float(np.std(bandwidth))
    else:
        features['bandwidth_mean'] = 0.0
        features['bandwidth_std'] = 0.0

    # 4. Spectral rolloff
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    if rolloff.size > 0:
        features['rolloff_mean'] = float(np.mean(rolloff))
    else:
        features['rolloff_mean'] = 0.0

    # 5. RMS Energy
    rms = librosa.feature.rms(y=y)
    if rms.size > 0:
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        features['dynamic_range'] = float(np.max(rms) - np.min(rms))
    else:
        features['rms_mean'] = 0.0
        features['rms_std'] = 0.0
        features['dynamic_range'] = 0.0

    # 6. ZCR
    zcr = librosa.feature.zero_crossing_rate(y)
    if zcr.size > 0:
        features['zcr_mean'] = float(np.mean(zcr))
    else:
        features['zcr_mean'] = 0.0

    # 7. Harmonic/Percussive
    try:
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        h_energy = float(np.sum(y_harmonic**2))
        p_energy = float(np.sum(y_percussive**2))
        features['harmonic_ratio'] = h_energy / (h_energy + p_energy + 1e-10)
    except:
        features['harmonic_ratio'] = 0.5

    # 8. MFCCs
    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f'mfcc{i+1}_mean'] = float(np.mean(mfcc[i]))
            features[f'mfcc{i+1}_std'] = float(np.std(mfcc[i]))
    except:
        for i in range(13):
            features[f'mfcc{i+1}_mean'] = 0.0
            features[f'mfcc{i+1}_std'] = 0.0

    # 9. Chroma
    try:
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        chroma_norm = chroma_mean / (np.sum(chroma_mean) + 1e-10)
        features['chroma_entropy'] = float(-np.sum(chroma_norm * np.log2(chroma_norm + 1e-10)))
        features['chroma_dominance'] = float(np.max(chroma_mean) / (np.mean(chroma_mean) + 1e-10))
    except:
        features['chroma_entropy'] = 0.0
        features['chroma_dominance'] = 1.0

    # 10. Onset rate
    try:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        features['onset_rate'] = float(np.mean(onset_env))
        features['onset_std'] = float(np.std(onset_env))
    except:
        features['onset_rate'] = 0.0
        features['onset_std'] = 0.0

    # 11. Spectral flatness
    flatness = librosa.feature.spectral_flatness(y=y)
    if flatness.size > 0:
        features['flatness_mean'] = float(np.mean(flatness))
    else:
        features['flatness_mean'] = 0.0

    # 12. Spectral contrast
    try:
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        features['contrast_mean'] = float(np.mean(contrast))
    except:
        features['contrast_mean'] = 0.0

    return features


def load_emotion_data():
    """Load participant emotion ratings from cloud database export"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Skip CLI header — find JSON start
    idx = raw.index('"data"')
    data = json.loads('{' + raw[idx:])
    results = data['data']['results'][0]

    # Aggregate per-track emotion distribution
    track_emotions = {}  # track -> {emotion: count}
    track_total = {}     # track -> total count

    for rec in results:
        if 'summary' not in rec:
            continue
        for s in rec['summary']:
            track = s.get('track', '')
            emotion = s.get('emotion', '')
            if not track or track == '_rest':
                continue
            if track not in track_emotions:
                track_emotions[track] = {}
                track_total[track] = 0
            track_emotions[track][emotion] = track_emotions[track].get(emotion, 0) + 1
            track_total[track] += 1

    # Convert to percentages
    emotion_pcts = {}
    emotions_list = ['anding', 'neixing', 'shuchang', 'zhenfen', 'ningjing']
    emotion_labels_cn = {'anding': '安定', 'neixing': '内省', 'shuchang': '舒畅', 'zhenfen': '振奋', 'ningjing': '宁静'}

    for track, total in track_total.items():
        emotion_pcts[track] = {'total': total}
        for e in emotions_list:
            count = track_emotions[track].get(e, 0)
            emotion_pcts[track][e] = round(count / total * 100, 1)

    return emotion_pcts, emotions_list, emotion_labels_cn


def main():
    print("=" * 80)
    print("ACOUSTIC FEATURE → EMOTION CORRELATION ANALYSIS")
    print("=" * 80)

    # Load emotion data
    print("\n[1/3] Loading emotion data...")
    emotion_pcts, emotions_list, emotion_labels = load_emotion_data()
    print(f"  Tracks with emotion data: {len(emotion_pcts)}")

    # Extract acoustic features
    print("\n[2/3] Extracting acoustic features...")
    acoustic = {}
    for track_id in emotion_pcts.keys():
        filepath = os.path.join(AUDIO_DIR, track_id + ".mp3")
        if os.path.exists(filepath):
            try:
                features = extract_features(filepath)
                acoustic[track_id] = features
                name = TRACK_NAMES.get(track_id, track_id)
                print(f"  {track_id} ({name}): tempo={features['tempo']:.0f}, "
                      f"centroid={features['centroid_mean']:.0f}, "
                      f"rms={features['rms_mean']:.4f}")
            except Exception as e:
                print(f"  ERROR {track_id}: {e}")
        else:
            print(f"  SKIP {track_id}: file not found")

    # Build correlation matrix
    print("\n[3/3] Computing correlations...")

    # Select key acoustic features
    key_features = [
        ('tempo', '速度 BPM'),
        ('centroid_mean', '频谱质心 (亮度)'),
        ('rms_mean', '响度 RMS'),
        ('zcr_mean', '过零率 (噪音感)'),
        ('harmonic_ratio', '和谐比'),
        ('chroma_entropy', '音高多样性'),
        ('chroma_dominance', '主音占优度'),
        ('dynamic_range', '动态范围'),
        ('onset_rate', '音符密度'),
        ('bandwidth_mean', '频谱宽度'),
        ('flatness_mean', '频谱平坦度'),
    ]

    correlations = {}
    for feat_key, feat_name in key_features:
        x = []
        for track_id in acoustic:
            if track_id in emotion_pcts:
                x.append(acoustic[track_id][feat_key])

        for e in emotions_list:
            y = []
            for track_id in acoustic:
                if track_id in emotion_pcts:
                    y.append(emotion_pcts[track_id][e])

            if len(x) > 5 and np.std(x) > 0 and np.std(y) > 0:
                r = np.corrcoef(x, y)[0, 1]
                key = f"{feat_key}_{e}"
                correlations[key] = {
                    'feature': feat_name,
                    'emotion': emotion_labels[e],
                    'r': round(float(r), 3),
                    'n': len(x)
                }

    # Print top correlations
    print("\n" + "=" * 80)
    print("TOP CORRELATIONS: Acoustic Feature ↔ Emotion")
    print("=" * 80)

    # Sort by absolute correlation
    sorted_corrs = sorted(correlations.values(), key=lambda x: abs(x['r']), reverse=True)

    print(f"\n{'Feature':<20} {'Emotion':<10} {'r':>8} {'Strength':<12}")
    print("-" * 55)
    for c in sorted_corrs[:30]:
        strength = 'strong' if abs(c['r']) > 0.5 else ('moderate' if abs(c['r']) > 0.3 else 'weak')
        print(f"{c['feature']:<20} {c['emotion']:<10} {c['r']:>+8.3f} {strength:<12}")

    # Build summary: what predicts each emotion best?
    print("\n" + "=" * 80)
    print("WHAT ACOUSTIC FEATURES PREDICT EACH EMOTION?")
    print("=" * 80)

    for e in emotions_list:
        label = emotion_labels[e]
        print(f"\n  [{label}]  best predictors:")
        e_corrs = [c for c in sorted_corrs if c['emotion'] == label]
        for c in e_corrs[:5]:
            direction = '↑ 更多' if c['r'] > 0 else '↓ 更少'
            print(f"    {c['feature']:<25} r={c['r']:+.3f}  {direction}")

    # Build a per-track summary for visualization
    print("\n" + "=" * 80)
    print("PER-TRACK SUMMARY (for visualization)")
    print("=" * 80)
    print(f"\n{'Track':<12} {'Name':<10} {'Tempo':>6} {'Bright':>8} {'Loud':>8} {'振奋%':>8} {'宁静%':>8} {'安定%':>8}")
    print("-" * 80)

    track_summary = []
    for track_id in acoustic:
        if track_id in emotion_pcts:
            name = TRACK_NAMES.get(track_id, track_id)
            t = acoustic[track_id]['tempo']
            b = acoustic[track_id]['centroid_mean']
            l = acoustic[track_id]['rms_mean']
            zf = emotion_pcts[track_id].get('zhenfen', 0)
            nj = emotion_pcts[track_id].get('ningjing', 0)
            ad = emotion_pcts[track_id].get('anding', 0)
            print(f"{track_id:<12} {name:<10} {t:>6.0f} {b:>8.0f} {l:>8.4f} {zf:>7.1f}% {nj:>7.1f}% {ad:>7.1f}%")
            track_summary.append({
                'track': track_id, 'name': name,
                'tempo': t, 'brightness': b, 'loudness': l,
                'zhenfen': zf, 'ningjing': nj, 'anding': ad,
                'neixing': emotion_pcts[track_id].get('neixing', 0),
                'shuchang': emotion_pcts[track_id].get('shuchang', 0)
            })

    # Save results
    output = {
        'correlations': sorted_corrs[:30],
        'track_summary': track_summary
    }
    outpath = 'F:/Claude project/five_tone_experiment/acoustic_emotion_results.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved: {outpath}")
    print(f"Tracks analyzed: {len(track_summary)}")
    print(f"Top 5 correlations:")
    for c in sorted_corrs[:5]:
        print(f"  {c['feature']} -> {c['emotion']}: r={c['r']:.3f}")

if __name__ == '__main__':
    main()
