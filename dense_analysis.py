"""
Lean analysis using reliably extracted features + emotion data.
Regression, PCA, age-group comparison, all from existing data.
"""
import json
import numpy as np
import os, sys

TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"

import librosa

def extract_robust_features(filepath):
    """Extract only the robust features that work reliably"""
    y, sr = librosa.load(filepath, sr=22050, duration=50)
    f = {}

    # Tempo
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    f['tempo'] = float(tempo.item() if hasattr(tempo, 'item') else tempo)

    # Spectral centroid (brightness)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    f['brightness'] = float(np.mean(cent))

    # RMS (loudness)
    rms = librosa.feature.rms(y=y)
    f['loudness'] = float(np.mean(rms))

    # ZCR (noisiness)
    zcr = librosa.feature.zero_crossing_rate(y)
    f['zcr'] = float(np.mean(zcr))

    # Onset rate (note density)
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    f['onset_rate'] = float(np.mean(onset))

    # Spectral bandwidth
    bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    f['bandwidth'] = float(np.mean(bw))

    # Spectral flatness
    flat = librosa.feature.spectral_flatness(y=y)
    f['flatness'] = float(np.mean(flat))

    # Harmonic ratio
    y_h, y_p = librosa.effects.hpss(y)
    f['harmonic'] = float(np.sum(y_h**2) / (np.sum(y_h**2) + np.sum(y_p**2) + 1e-10))

    # Chroma entropy
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    cm = np.mean(chroma, axis=1)
    cm = cm / (cm.sum() + 1e-10)
    f['chroma_entropy'] = float(-np.sum(cm * np.log2(cm + 1e-10)))

    return f


def main():
    # Load track-level emotion data from acoustic_emotion_results.json
    with open('F:/Claude project/five_tone_experiment/acoustic_emotion_results.json', 'r', encoding='utf-8') as f:
        emo_data = json.load(f)
    tracks = [t for t in emo_data['track_summary'] if t['tempo'] > 0]
    print(f"Valid tracks: {len(tracks)}")

    # Extract robust features for each track
    print("Extracting acoustic features...")
    features = {}
    for t in tracks:
        tk = t['track']
        fp = os.path.join(AUDIO_DIR, tk + ".mp3")
        if os.path.exists(fp):
            try:
                features[tk] = extract_robust_features(fp)
            except Exception as e:
                print(f"  FAIL {tk}: {e}")
                features[tk] = None
        else:
            features[tk] = None

    # Filter to tracks with features
    valid = []
    for t in tracks:
        tk = t['track']
        if features.get(tk):
            valid.append(t)

    feat_keys = ['tempo','brightness','loudness','zcr','onset_rate','bandwidth','flatness','harmonic','chroma_entropy']
    feat_labels = ['速度BPM','频谱质心(亮度)','响度RMS','过零率(噪感)','音符密度','频谱宽度','频谱平坦度','和谐比','音高多样性']
    emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
    emotion_labels = ['安定','内省','舒畅','振奋','宁静']

    # Build matrices
    X_raw = np.array([[features[t['track']][fk] for fk in feat_keys] for t in valid])
    Y_raw = np.array([[t[e] for e in emotions] for t in valid])
    names = [TRACK_NAMES.get(t['track'], t['track']) for t in valid]

    # Z-score normalize
    X = (X_raw - X_raw.mean(axis=0)) / (X_raw.std(axis=0) + 1e-10)

    N = len(valid)
    P = len(feat_keys)

    print(f"\nN={N} tracks, P={P} features, {len(emotions)} emotions")
    print("=" * 75)

    # ========== PEARSON CORRELATION MATRIX ==========
    print("\n--- PEARSON CORRELATION: Feature vs Emotion ---")
    print(f"{'Feature':<18}", end="")
    for el in emotion_labels:
        print(f"{el:>8}", end="")
    print()
    print("-" * (18 + 8*5))

    for fi, fl in enumerate(feat_labels):
        print(f"{fl:<18}", end="")
        for ei in range(len(emotions)):
            r = np.corrcoef(X_raw[:, fi], Y_raw[:, ei])[0, 1]
            marker = "**" if abs(r) > 0.5 else ("*" if abs(r) > 0.4 else " ")
            print(f"{r:>+7.3f}{marker}", end="")
        print()

    print("\n  ** |r|>0.5   * |r|>0.4")

    # ========== PCA ==========
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    PC = X @ Vt.T
    pc1_var = S[0]**2 / np.sum(S**2) * 100
    pc2_var = S[1]**2 / np.sum(S**2) * 100

    print(f"\n--- PCA ---")
    print(f"PC1: {pc1_var:.1f}%  PC2: {pc2_var:.1f}%  Total: {pc1_var+pc2_var:.1f}%")
    print(f"\nPC1 loadings (bright<->dark spectrum):")
    for fl, ld in sorted(zip(feat_labels, Vt[0]), key=lambda x: -abs(x[1]))[:4]:
        print(f"  {fl}: {ld:+.3f}")
    print(f"PC2 loadings (fast/dense<->slow/sparse):")
    for fl, ld in sorted(zip(feat_labels, Vt[1]), key=lambda x: -abs(x[1]))[:4]:
        print(f"  {fl}: {ld:+.3f}")

    # ========== MULTIPLE REGRESSION ==========
    print(f"\n--- EXPLORATORY REGRESSION (N={N}, P={P}) ---")
    XtX = X.T @ X + np.eye(P) * 0.5  # Ridge with lambda=0.5
    XtX_inv = np.linalg.inv(XtX)

    for ei, el in enumerate(emotion_labels):
        y = Y_raw[:, ei]
        y_std = (y - y.mean()) / (y.std() + 1e-10)
        beta = XtX_inv @ X.T @ y_std
        y_pred = X @ beta
        r2 = 1 - np.sum((y_std - y_pred)**2) / np.sum((y_std - y_std.mean())**2)
        r2_adj = 1 - (1-r2) * (N-1) / (N-P-1)

        print(f"\n  {el}: R2={r2:.3f} (adj={r2_adj:.3f})")
        ranked = sorted(zip(feat_labels, beta), key=lambda x: -abs(x[1]))
        for fl, b in ranked[:4]:
            direc = 'more' if b > 0 else 'less'
            print(f"    {fl}: {b:+.3f} -> {direc} {el}")

    # ========== TRACK SPACE ==========
    print(f"\n--- 2D ACOUSTIC-EMOTION SPACE ---")
    print(f"{'Track':<12} {'PC1':>8} {'PC2':>8} {'振奋%':>7} {'宁静%':>7} {'安定%':>7} {'内省%':>7}")
    print("-" * 60)
    for i, t in enumerate(valid):
        nm = names[i]
        print(f"{nm:<12} {PC[i,0]:>+8.3f} {PC[i,1]:>+8.3f} {t['zhenfen']:>6.1f} {t['ningjing']:>6.1f} {t['anding']:>6.1f} {t['neixing']:>6.1f}")

    # ========== AGE GROUP ==========
    print(f"\n--- AGE GROUP CONTRAST (Teen <=22 vs 40+) ---")
    with open("F:/Claude project/five_tone_experiment/latest_data.json", 'r', encoding='utf-8') as f:
        raw = f.read()
    idx = raw.index('"data"')
    raw_data = json.loads('{' + raw[idx:])
    participants = raw_data['data']['results'][0]

    # Tally by age
    teen_emo = {}; mid_emo = {}
    for rec in participants:
        if 'participant' not in rec or 'summary' not in rec:
            continue
        age = int(rec['participant']['age']['$numberInt'])
        for s in rec['summary']:
            tk = s.get('track','')
            em = s.get('emotion','')
            if not tk: continue
            if age <= 22:
                teen_emo.setdefault(tk, {})
                teen_emo[tk][em] = teen_emo[tk].get(em, 0) + 1
            if age >= 40:
                mid_emo.setdefault(tk, {})
                mid_emo[tk][em] = mid_emo[tk].get(em, 0) + 1

    print(f"{'Track':<12} {'Name':<10} {'Teen振奋%':>9} {'Mid振奋%':>9} {'Gap':>6} {'Teen安定%':>9} {'Mid安定%':>9}")
    print("-" * 70)
    gaps = []
    for t in valid:
        tk = t['track']; nm = TRACK_NAMES.get(tk, tk)
        tt = sum(teen_emo.get(tk, {}).values())
        mt = sum(mid_emo.get(tk, {}).values())
        tz = teen_emo.get(tk, {}).get('zhenfen', 0) / max(tt, 1) * 100
        mz = mid_emo.get(tk, {}).get('zhenfen', 0) / max(mt, 1) * 100
        ta = teen_emo.get(tk, {}).get('anding', 0) / max(tt, 1) * 100
        ma = mid_emo.get(tk, {}).get('anding', 0) / max(mt, 1) * 100
        g = tz - mz
        print(f"{tk:<12} {nm:<10} {tz:>8.1f}% {mz:>8.1f}% {g:>+5.1f} {ta:>8.1f}% {ma:>8.1f}%")
        gaps.append({'name': nm, 'teen_zf': tz, 'mid_zf': mz, 'gap': g, 'teen_ad': ta, 'mid_ad': ma})

    print("\n  Largest generational gaps (excitement):")
    for g in sorted(gaps, key=lambda x: abs(x['gap']), reverse=True)[:5]:
        d = 'teens more' if g['gap'] > 0 else '40+ more'
        print(f"    {g['name']}: teen={g['teen_zf']:.0f}% mid={g['mid_zf']:.0f}% ({d})")

    print("\nDone.")


if __name__ == '__main__':
    main()
