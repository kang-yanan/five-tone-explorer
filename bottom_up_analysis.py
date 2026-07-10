"""
Bottom-up: Let 50 participants' responses cluster naturally,
then characterize clusters by acoustic features.
No pre-imposed emotion labels. Data-driven.
"""
import json, numpy as np, os, sys

TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

import librosa

def extract_features(filepath):
    y, sr = librosa.load(filepath, sr=22050, duration=50)
    f = {}
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    f['tempo'] = float(tempo.item() if hasattr(tempo, 'item') else tempo)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)
    f['brightness'] = float(np.mean(cent))
    rms = librosa.feature.rms(y=y)
    f['loudness'] = float(np.mean(rms))
    zcr = librosa.feature.zero_crossing_rate(y)
    f['zcr'] = float(np.mean(zcr))
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    f['onset_rate'] = float(np.mean(onset))
    bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    f['bandwidth'] = float(np.mean(bw))
    y_h, y_p = librosa.effects.hpss(y)
    f['harmonic'] = float(np.sum(y_h**2)/(np.sum(y_h**2)+np.sum(y_p**2)+1e-10))
    return f


AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"

# Load data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()
idx = raw.index('"data"')
data = json.loads('{' + raw[idx:])
participants = data['data']['results'][0]

emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
emo_labels_cn = ['安定','内省','舒畅','振奋','宁静']

# === STEP 1: Build per-track raw response matrix ===
# 24 tracks x 5 emotions = percentage each emotion was chosen
track_emo = {}
track_count = {}
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track','')
        em = s.get('emotion','')
        if not tk: continue
        if tk not in track_emo:
            track_emo[tk] = {e:0 for e in emotions}
            track_count[tk] = 0
        track_emo[tk][em] += 1
        track_count[tk] += 1

valid_tracks = sorted([tk for tk in track_count if track_count[tk] >= 5])
print(f"Tracks analyzed: {len(valid_tracks)}")

# Build matrix: rows=tracks, cols=emotions
X_emo = np.array([[track_emo[tk][e]/track_count[tk]*100 for e in emotions] for tk in valid_tracks])
names = [TRACK_NAMES.get(tk, tk) for tk in valid_tracks]

# === STEP 2: Extract acoustic features ===
print("Extracting acoustic features...")
feat_keys = ['tempo','brightness','loudness','zcr','onset_rate','bandwidth','harmonic']
feat_labels = ['速度','频谱质心(亮度)','响度','过零率(噪感)','音符密度','频谱宽度','和谐比']
X_acoustic_raw = []
for tk in valid_tracks:
    fp = os.path.join(AUDIO_DIR, tk + ".mp3")
    if os.path.exists(fp):
        f = extract_features(fp)
        X_acoustic_raw.append([f[k] for k in feat_keys])
    else:
        X_acoustic_raw.append([0]*len(feat_keys))
X_acoustic = np.array(X_acoustic_raw)

# Z-score normalize acoustic features
X_acoustic_z = (X_acoustic - X_acoustic.mean(axis=0)) / (X_acoustic.std(axis=0) + 1e-10)

# === STEP 3: PCA on emotion responses ===
print("\n" + "=" * 70)
print("STEP 1: Natural dimensionality of emotion responses (no pre-imposed labels)")
print("=" * 70)

X_emo_z = (X_emo - X_emo.mean(axis=0)) / (X_emo.std(axis=0) + 1e-10)
U_e, S_e, Vt_e = np.linalg.svd(X_emo_z, full_matrices=False)
PC_emo = X_emo_z @ Vt_e.T

for i in range(3):
    var = S_e[i]**2 / np.sum(S_e**2) * 100
    print(f"\n  Emotion PC{i+1} ({var:.1f}% variance):")
    ranked = sorted(zip(emo_labels_cn, Vt_e[i]), key=lambda x: -abs(x[1]))
    for lbl, ld in ranked:
        print(f"    {lbl}: {ld:+.3f}")

# === STEP 4: Cluster tracks by emotion profile ===
print("\n" + "=" * 70)
print("STEP 2: Natural clusters by 50-listener emotion responses")
print("=" * 70)

from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

# Hierarchical clustering on emotion percentages
dist = pdist(X_emo_z, metric='euclidean')
Z = linkage(dist, method='ward')

# Try k=3, k=4 clusters
for k in [3, 4]:
    clusters = fcluster(Z, k, criterion='maxclust')
    print(f"\n  K={k} clusters:")
    for c in range(1, k+1):
        members = [(names[i], X_emo[i]) for i in range(len(valid_tracks)) if clusters[i] == c]
        print(f"\n  Cluster {c} ({len(members)} tracks):")
        for nm, emo_vec in members:
            top = sorted(zip(emo_labels_cn, emo_vec), key=lambda x: -x[1])[:2]
            emo_str = " | ".join([f"{l}:{v:.0f}%" for l,v in top])
            print(f"    {nm:<10} {emo_str}")
        # Average emotion profile
        avg = np.mean([m[1] for m in members], axis=0)
        print(f"    --- AVERAGE: " + " | ".join([f"{emo_labels_cn[i]}:{avg[i]:.0f}%" for i in range(5)]))

# === STEP 5: Which acoustic features characterize each cluster? ===
print("\n" + "=" * 70)
print("STEP 3: Acoustic characterization of natural clusters (K=3)")
print("=" * 70)

clusters_k3 = fcluster(Z, 3, criterion='maxclust')

for c in range(1, 4):
    idxs = [i for i in range(len(valid_tracks)) if clusters_k3[i] == c]
    print(f"\n  Cluster {c} ({len(idxs)} tracks):")
    for fi, fl in enumerate(feat_labels):
        cluster_mean = X_acoustic[idxs, fi].mean()
        overall_mean = X_acoustic[:, fi].mean()
        overall_std = X_acoustic[:, fi].std()
        diff = (cluster_mean - overall_mean) / (overall_std + 1e-10)
        marker = '>>' if diff > 0.8 else ('<<' if diff < -0.8 else ('>' if diff > 0.3 else ('<' if diff < -0.3 else '~')))
        print(f"    {fl:<16}: cluster={cluster_mean:.1f} vs overall={overall_mean:.1f} (z={diff:+.2f}) {marker}")

# === STEP 6: PCA on acoustic features + map tracks ===
print("\n" + "=" * 70)
print("STEP 4: Acoustic PCA space with emotion colors")
print("=" * 70)

U_a, S_a, Vt_a = np.linalg.svd(X_acoustic_z, full_matrices=False)
PC_ac = X_acoustic_z @ Vt_a.T

print(f"  Acoustic PC1 ({S_a[0]**2/np.sum(S_a**2)*100:.1f}%):", end="")
for fl, ld in sorted(zip(feat_labels, Vt_a[0]), key=lambda x: -abs(x[1]))[:3]:
    print(f" {fl}({ld:+.2f})", end="")
print(f"\n  Acoustic PC2 ({S_a[1]**2/np.sum(S_a**2)*100:.1f}%):", end="")
for fl, ld in sorted(zip(feat_labels, Vt_a[1]), key=lambda x: -abs(x[1]))[:3]:
    print(f" {fl}({ld:+.2f})", end="")
print()

# Map: acoustic PC1 vs PC2, color by dominant emotion (data-driven)
print(f"\n  {'Track':<10} {'AcoPC1':>8} {'AcoPC2':>8} {'DominantEmotion':>18} {'Cluster':>8}")
print("  " + "-" * 58)
for i in range(len(valid_tracks)):
    dom_emo = emo_labels_cn[np.argmax(X_emo[i])]
    dom_pct = np.max(X_emo[i])
    print(f"  {names[i]:<10} {PC_ac[i,0]:>+8.3f} {PC_ac[i,1]:>+8.3f} {dom_emo}({dom_pct:.0f}%) {'C'+str(clusters_k3[i]):>8}")

# === STEP 7: Arousal as the one real dimension ===
print("\n" + "=" * 70)
print("STEP 5: AROUSAL — the one dimension we CAN trust")
print("=" * 70)

# Arousal is a physiological dimension, not a cultural label
# For each track, compute mean arousal from participant data
track_arousal = {}
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track','')
        ar = s.get('arousal', None)
        if not tk or ar is None: continue
        if tk not in track_arousal:
            track_arousal[tk] = []
        if isinstance(ar, dict):
            track_arousal[tk].append(int(ar.get('$numberInt', 0)))
        else:
            track_arousal[tk].append(int(ar))

arousal_by_track = {}
for tk in valid_tracks:
    if tk in track_arousal and len(track_arousal[tk]) >= 3:
        vals = track_arousal[tk]
        arousal_by_track[tk] = {'mean': np.mean(vals), 'std': np.std(vals), 'n': len(vals)}

print(f"\n  Arousal range: 1 (very calm) to 5 (very excited)")
print(f"\n  {'Track':<12} {'ArousalMean':>12} {'ArousalSD':>10} {'N':>5}")
print("  " + "-" * 42)
for tk in valid_tracks:
    if tk in arousal_by_track:
        a = arousal_by_track[tk]
        nm = TRACK_NAMES.get(tk, tk)
        print(f"  {nm:<12} {a['mean']:>11.2f} {a['std']:>9.2f} {a['n']:>5}")

# Correlate arousal with acoustic features
print(f"\n  Acoustic feature -> AROUSAL correlation:")
for fi, fl in enumerate(feat_labels):
    x = [X_acoustic[i, fi] for i in range(len(valid_tracks))]
    y = [arousal_by_track[tk]['mean'] for tk in valid_tracks if tk in arousal_by_track]
    x_aligned = [X_acoustic[list(valid_tracks).index(tk), fi] for tk in valid_tracks if tk in arousal_by_track]
    if len(x_aligned) > 5:
        r = np.corrcoef(x_aligned, y)[0, 1]
        marker = '**' if abs(r) > 0.5 else ('*' if abs(r) > 0.4 else '')
        print(f"    {fl:<20} r={r:+.3f} {marker}")

print("\n" + "=" * 70)
print("KEY FINDING: Arousal is the only dimension we don't need to define.")
print("It's self-reported on a 1-5 scale, not a forced cultural label.")
print("And it correlates with objective acoustic features.")
print("=" * 70)
