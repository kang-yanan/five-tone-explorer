"""
Refined analysis: Multiple regression, PCA visualization, and age-group sensitivity
"""
import json
import numpy as np
import os
import sys

SR = 22050
AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"

TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

def main():
    # Load acoustic results
    with open('F:/Claude project/five_tone_experiment/acoustic_emotion_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    tracks = data['track_summary']

    # Build feature matrix and emotion vectors
    # Features: tempo, centroid_mean, rms_mean, zcr_mean, harmonic_ratio,
    #           chroma_entropy, chroma_dominance, dynamic_range, onset_rate, bandwidth_mean, flatness_mean
    feature_names = ['tempo','centroid_mean','rms_mean','zcr_mean','harmonic_ratio',
                     'chroma_entropy','chroma_dominance','dynamic_range','onset_rate',
                     'bandwidth_mean','flatness_mean']
    feature_labels = ['速度','频谱质心(亮度)','响度','过零率(噪感)','和谐比',
                      '音高多样性','主音占优度','动态范围','音符密度','频谱宽度','频谱平坦度']

    emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
    emotion_labels = ['安定','内省','舒畅','振奋','宁静']

    # Build matrices
    valid_tracks = [t for t in tracks if t['tempo'] > 0]

    X_raw = np.array([[t[f] for f in ['tempo','centroid_mean','rms_mean','zcr_mean','harmonic_ratio',
                                        'chroma_entropy','chroma_dominance','dynamic_range','onset_rate',
                                        'bandwidth_mean','flatness_mean']] for t in valid_tracks])
    Y_raw = np.array([[t[e] for e in emotions] for t in valid_tracks])

    # Z-score normalize
    X_mean = X_raw.mean(axis=0)
    X_std = X_raw.std(axis=0) + 1e-10
    X = (X_raw - X_mean) / X_std

    track_names_list = [TRACK_NAMES.get(t['track'], t['track']) for t in valid_tracks]

    print("=" * 80)
    print("COMPREHENSIVE ANALYSIS: Acoustic Features -> Emotion Perception")
    print(f"Tracks analyzed: {len(valid_tracks)}")
    print("=" * 80)

    # ==========================================
    # 1. MULTIPLE LINEAR REGRESSION (exploratory)
    # ==========================================
    print("\n" + "=" * 80)
    print("1. EXPLORATORY MULTIPLE REGRESSION")
    print("   (N=24, 11 features, no train/test split - exploratory only)")
    print("=" * 80)

    XtX = X.T @ X
    try:
        XtX_inv = np.linalg.inv(XtX)
    except:
        ridge = XtX + np.eye(11) * 0.1
        XtX_inv = np.linalg.inv(ridge)

    for ei, elabel in enumerate(emotion_labels):
        y = Y_raw[:, ei]
        y_standardized = (y - y.mean()) / (y.std() + 1e-10)

        beta = XtX_inv @ X.T @ y_standardized

        y_pred = X @ beta
        ss_res = np.sum((y_standardized - y_pred) ** 2)
        ss_tot = np.sum((y_standardized - np.mean(y_standardized)) ** 2)
        r2 = 1 - ss_res / (ss_tot + 1e-10)
        r2_adj = 1 - (1 - r2) * (23) / (12)  # Adj for N=24, p=11

        print(f"\n  [{elabel}] R2={r2:.3f} (adjusted={r2_adj:.3f})")
        print(f"  {'Feature':<18} {'Beta':>8} {'Direction':<10}")
        print(f"  {'-'*18} {'-'*8} {'-'*10}")

        ranked = sorted(zip(feature_labels, beta), key=lambda x: abs(x[1]), reverse=True)
        for flabel, b in ranked[:5]:
            direction = '↑ 更多' + elabel if b > 0 else '↓ 更少' + elabel
            print(f"  {flabel:<18} {b:>+8.3f} {direction:<10}")

    # ==========================================
    # 2. PCA: Reduce to 2D acoustic space
    # ==========================================
    print("\n" + "=" * 80)
    print("2. PCA: 2D ACOUSTIC-EMOTION SPACE")
    print("=" * 80)

    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    PC = X @ Vt.T

    pc1_var = (S[0]**2) / np.sum(S**2) * 100
    pc2_var = (S[1]**2) / np.sum(S**2) * 100

    print(f"  PC1 explains {pc1_var:.1f}% variance")
    print(f"  PC2 explains {pc2_var:.1f}% variance")
    print(f"  Together: {pc1_var+pc2_var:.1f}%")

    # PC1 loadings (top features)
    print(f"\n  PC1 dominant features:")
    pc1_ranked = sorted(zip(feature_labels, Vt[0]), key=lambda x: abs(x[1]), reverse=True)
    for flabel, loading in pc1_ranked[:4]:
        direction = "+" if loading > 0 else "-"
        print(f"    {flabel}: {loading:+.3f} {direction}")

    print(f"\n  PC2 dominant features:")
    pc2_ranked = sorted(zip(feature_labels, Vt[1]), key=lambda x: abs(x[1]), reverse=True)
    for flabel, loading in pc2_ranked[:4]:
        direction = "+" if loading > 0 else "-"
        print(f"    {flabel}: {loading:+.3f} {direction}")

    # ==========================================
    # 3. Track positions in 2D acoustic-emotion space
    # ==========================================
    print(f"\n{'Track':<12} {'Name':<10} {'PC1':>8} {'PC2':>8} {'振奋%':>8} {'宁静%':>8} {'安定%':>8}")
    print("-" * 70)

    pc_results = []
    for i, t in enumerate(valid_tracks):
        name = track_names_list[i]
        pc1 = PC[i, 0]
        pc2 = PC[i, 1]
        zf = t['zhenfen']
        nj = t['ningjing']
        ad = t['anding']
        nx = t['neixing']
        sc = t['shuchang']
        print(f"{t['track']:<12} {name:<10} {pc1:>+8.3f} {pc2:>+8.3f} {zf:>7.1f}% {nj:>7.1f}% {ad:>7.1f}%")
        pc_results.append({
            'track': t['track'], 'name': name,
            'pc1': float(pc1), 'pc2': float(pc2),
            'zhenfen': zf, 'ningjing': nj, 'anding': ad,
            'neixing': nx, 'shuchang': sc
        })

    # ==========================================
    # 4. Age group re-analysis
    # ==========================================
    print("\n" + "=" * 80)
    print("4. AGE GROUP CONTRAST")
    print("=" * 80)

    # Load raw participant data with ages
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        raw = f.read()
    idx = raw.index('"data"')
    raw_data = json.loads('{' + raw[idx:])
    participants = raw_data['data']['results'][0]

    # Get age-segmented emotion data
    teen_emotions = {}  # track -> {emotion: count}
    mid_emotions = {}
    for rec in participants:
        if 'participant' not in rec or 'summary' not in rec:
            continue
        age = int(rec['participant']['age']['$numberInt'])
        for s in rec['summary']:
            track = s.get('track', '')
            emotion = s.get('emotion', '')
            if not track:
                continue
            if age <= 22:
                teen_emotions.setdefault(track, {}).setdefault(emotion, 0)
                teen_emotions[track][emotion] += 1
            if age >= 40:
                mid_emotions.setdefault(track, {}).setdefault(emotion, 0)
                mid_emotions[track][emotion] += 1

    # Compute per-track emotion % by age
    print(f"\n{'Track':<12} {'Name':<10} {'Teen振奋%':>10} {'Mid振奋%':>10} {'Th差异':>8} {'Teen宁静%':>10} {'Mid宁静%':>10}")
    print("-" * 80)

    teen_vs_mid_zf = []
    for t in valid_tracks:
        tk = t['track']
        name = track_names_list[0] if i==0 else TRACK_NAMES.get(tk, tk)

        # Teen
        teen_total = sum(teen_emotions.get(tk, {}).values())
        teen_zf = teen_emotions.get(tk, {}).get('zhenfen', 0) / max(teen_total, 1) * 100
        teen_nj = teen_emotions.get(tk, {}).get('ningjing', 0) / max(teen_total, 1) * 100

        # Mid
        mid_total = sum(mid_emotions.get(tk, {}).values())
        mid_zf = mid_emotions.get(tk, {}).get('zhenfen', 0) / max(mid_total, 1) * 100
        mid_nj = mid_emotions.get(tk, {}).get('ningjing', 0) / max(mid_total, 1) * 100

        name = TRACK_NAMES.get(tk, tk)
        diff = teen_zf - mid_zf
        print(f"{tk:<12} {name:<10} {teen_zf:>9.1f}% {mid_zf:>9.1f}% {diff:>+7.1f} {teen_nj:>9.1f}% {mid_nj:>9.1f}%")
        teen_vs_mid_zf.append({'track': tk, 'name': name, 'teen_zf': teen_zf, 'mid_zf': mid_zf, 'diff': diff})

    # Top generational gaps
    sorted_by_gap = sorted(teen_vs_mid_zf, key=lambda x: abs(x['diff']), reverse=True)
    print(f"\n  Largest generation gaps (teen vs 40+):")
    for item in sorted_by_gap[:5]:
        direction = 'Teen higher' if item['diff'] > 0 else 'Mid higher'
        print(f"    {item['name']}: teen={item['teen_zf']:.0f}% mid={item['mid_zf']:.0f}% ({direction})")

    # ==========================================
    # 5. OUTPUT for visualization
    # ==========================================
    output = {
        'regression': {},
        'pca': {
            'pc1_var': float(pc1_var),
            'pc2_var': float(pc2_var),
            'pc1_top_features': [(f, float(l)) for f, l in pc1_ranked[:4]],
            'pc2_top_features': [(f, float(l)) for f, l in pc2_ranked[:4]],
            'track_positions': pc_results
        },
        'age_gaps': sorted_by_gap
    }

    outpath = 'F:/Claude project/five_tone_experiment/detailed_analysis.json'
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results saved: {outpath}")

if __name__ == '__main__':
    main()
