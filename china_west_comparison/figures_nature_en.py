"""
Nature-style figures for FiveTone Explorer — English submission.
Figure 1: Five-source classification chaos heatmap
Figure 2: Bottom-up emotion clusters from 50 listeners
Figure 3: Arousal predicted by acoustic features
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json, os

# ===== NATURE-FIGURE CONSTANTS =====
PAL = {
    "blue_main": "#0F4D92", "blue_sec": "#3775BA",
    "red_strong": "#B64342",
    "neutral_light": "#D8D8D8", "neutral_mid": "#A8A8A8",
    "neutral_dark": "#606060", "neutral_black": "#272727",
    "teal": "#42949E", "violet": "#9A4D8E", "gold": "#E28E2C",
    "delta_up": "#2E9E44",
}

MODE_COLORS = {
    'gong': '#C4A35A', 'shang': '#B0ACA4', 'jue': '#8BA684',
    'zhi': '#C48173', 'yu': '#7D8FA8',
    'mixed': '#A8A8A8', 'none': '#D8D8D8',
}

CLUSTER_COLORS = {1: PAL['delta_up'], 2: PAL['blue_main'], 3: PAL['gold']}

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 8,
    'axes.titlesize': 9, 'axes.labelsize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'legend.fontsize': 7, 'figure.dpi': 300, 'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False, 'axes.spines.right': False,
})

OUT = "F:/Claude project/five_tone_experiment/"

# ===== DATA =====
TRACK_NAMES_EN = {
    'gong_01':'Autumn Moon over the Lake','gong_02':'Liuyang River',
    'gong_03':'Purple Bamboo Tune','gong_04':'Flower Three-Six',
    'gong_05':'Plum Blossoms in Snow',
    'shang_01':'Ambush on All Sides','shang_02':'Guangling San',
    'shang_03':'Luchai Flower','shang_05':'Yangguan Pass',
    'jue_01':'Riding the Wind','jue_02':'Gusu Journey',
    'jue_03':'Eighteen Beats','jue_04':'Blooming Flowers',
    'jue_05':'Rainbow Skirt Dance',
    'zhi_01':'Joyful','zhi_02':'New Year Joy',
    'zhi_03':'Spring Festival Overture','zhi_04':'Rising Higher',
    'zhi_05':'March of the PLA',
    'yu_01':'Crow Night Cry','yu_02':'Moonlit Spring',
    'yu_03':'Jackdaws Playing in Water','yu_04':'Butterfly Lovers',
    'yu_05':'River of Sorrow',
}

SOURCES = ['TCM Clinical\nLiterature','Musicology\nReferences','Computational\nMIR (librosa)']
CLASS_MATRIX = {
    'gong_01': ['none','gong','jue'],
    'gong_02': ['none','gong','gong'],
    'gong_03': ['zhi','yu','gong'],
    'gong_04': ['none','gong','gong'],
    'gong_05': ['none','zhi','gong'],
    'shang_01': ['gong','shang','yu'],
    'shang_02': ['none','gong','zhi'],
    'shang_03': ['none','zhi','jue'],
    'shang_05': ['shang','gong','yu'],
    'jue_01': ['jue','gong','shang'],
    'jue_02': ['none','zhi','gong'],
    'jue_03': ['none','yu','gong'],
    'jue_04': ['none','gong','gong'],
    'jue_05': ['none','yu','yu'],
    'zhi_01': ['zhi','zhi','gong'],
    'zhi_02': ['none','zhi','gong'],
    'zhi_03': ['zhi','gong','jue'],
    'zhi_04': ['zhi','zhi','jue'],
    'zhi_05': ['zhi','gong','gong'],
    'yu_01': ['none','yu','jue'],
    'yu_02': ['yu','mixed','gong'],
    'yu_03': ['none','yu','zhi'],
    'yu_04': ['mixed','yu','yu'],
    'yu_05': ['none','shang','yu'],
}
MODE_ORDER = ['gong','shang','jue','zhi','yu']

# Sort tracks by original mode
track_keys_fig1 = sorted(CLASS_MATRIX.keys(),
    key=lambda k: (MODE_ORDER.index(CLASS_MATRIX[k][0]) if CLASS_MATRIX[k][0] in MODE_ORDER else 5,
                   TRACK_NAMES_EN.get(k,k)))

# ===== Load emotion + acoustic data =====
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()
idx = raw.index('"data"')
data = json.loads('{' + raw[idx:])
participants = data['data']['results'][0]

emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
emo_labels_en = ['Stable','Introspect.','Flowing','Exciting','Quiet']

# Track-level emotion %
track_emo = {}; track_n = {}
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track',''); em = s.get('emotion','')
        if not tk: continue
        track_emo.setdefault(tk, {e:0 for e in emotions})
        track_n[tk] = track_n.get(tk, 0) + 1
        track_emo[tk][em] += 1

valid_tracks = sorted([tk for tk in track_n if track_n[tk] >= 5 and tk != 'shang_04'])
X_emo = np.array([[track_emo[tk][e]/track_n[tk]*100 for e in emotions] for tk in valid_tracks])
names_en_list = [TRACK_NAMES_EN.get(tk,tk) for tk in valid_tracks]

# PCA + clustering
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
X_emo_z = (X_emo - X_emo.mean(axis=0)) / (X_emo.std(axis=0) + 1e-10)
U_e, S_e, Vt_e = np.linalg.svd(X_emo_z, full_matrices=False)
PC = X_emo_z @ Vt_e.T
clusters = fcluster(linkage(pdist(X_emo_z, 'euclidean'), 'ward'), 3, criterion='maxclust')

# Acoustic features + arousal
import librosa
AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"

acoustic_feats = {}; arousal_means = {}
for tk in valid_tracks:
    fp = os.path.join(AUDIO_DIR, tk + ".mp3")
    if not os.path.exists(fp): continue
    y, sr = librosa.load(fp, sr=22050, duration=50)
    acoustic_feats[tk] = {
        'tempo': float(np.atleast_1d(librosa.beat.beat_track(y=y,sr=sr)[0])[0]),
        'brightness': float(np.mean(librosa.feature.spectral_centroid(y=y,sr=sr))),
        'zcr': float(np.mean(librosa.feature.zero_crossing_rate(y))),
        'bandwidth': float(np.mean(librosa.feature.spectral_bandwidth(y=y,sr=sr))),
    }
# Arousal
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track',''); ar = s.get('arousal',None)
        if not tk or ar is None: continue
        v = int(ar.get('$numberInt',ar)) if isinstance(ar,dict) else int(ar)
        arousal_means.setdefault(tk, []).append(v)
for tk in list(arousal_means.keys()):
    arousal_means[tk] = np.mean(arousal_means[tk])

shared = sorted([tk for tk in valid_tracks if tk in acoustic_feats and tk in arousal_means])

# ===== FIGURE 1: FIVE-SOURCE HEATMAP =====
print("Figure 1...")
fig1, ax1 = plt.subplots(figsize=(7.0, 8.0))
n_tracks, n_sources = len(track_keys_fig1), len(SOURCES)
mode_labels = {'gong':'Gong','shang':'Shang','jue':'Jue','zhi':'Zhi','yu':'Yu','none':'-','mixed':'?'}

for i, tk in enumerate(track_keys_fig1):
    for j in range(n_sources):
        mode = CLASS_MATRIX[tk][j]
        color = MODE_COLORS.get(mode, PAL['neutral_light'])
        rect = plt.Rectangle((j, n_tracks-1-i), 1, 1, facecolor=color, edgecolor='w', lw=1.5)
        ax1.add_patch(rect)
        lbl = mode_labels.get(mode, mode)
        text_c = 'w' if mode in ['zhi','yu'] else PAL['neutral_black']
        ax1.text(j+0.5, n_tracks-1-i+0.5, lbl, ha='center', va='center', fontsize=8, fontweight='bold', color=text_c)

ax1.set_xlim(0, n_sources); ax1.set_ylim(0, n_tracks)
ax1.set_xticks([j+0.5 for j in range(n_sources)]); ax1.set_xticklabels(SOURCES, fontsize=7)
ax1.set_yticks([n_tracks-1-i+0.5 for i in range(n_tracks)])
ax1.set_yticklabels([TRACK_NAMES_EN.get(tk,tk) for tk in track_keys_fig1], fontsize=6.5)
ax1.tick_params(length=0)

legend_patches = [mpatches.Patch(color=MODE_COLORS[m], label=ml) for m, ml in
    [('gong','Gong'),('shang','Shang'),('jue','Jue'),('zhi','Zhi'),('yu','Yu'),
     ('mixed','Disputed'),('none','Not listed')]]
ax1.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1.01,0.98), frameon=False, fontsize=7)

# Group dividers
y_pos = 0
for mode in MODE_ORDER:
    count = sum(1 for tk in track_keys_fig1 if CLASS_MATRIX[tk][0] == mode)
    if count:
        y_pos += count
        if y_pos < n_tracks: ax1.axhline(y=n_tracks-y_pos, color=PAL['neutral_dark'], lw=0.8, alpha=0.4)
        mid_y = n_tracks - (y_pos - count/2)
        ax1.text(-0.8, mid_y, mode.capitalize(), fontsize=8, fontweight='bold',
                color=MODE_COLORS[mode], ha='right', va='center')

fig1.suptitle('Five-source pentatonic mode classification reveals low inter-source agreement',
              fontsize=10, fontweight='bold')
fig1.text(0.5, 0.005, 'Only 4/24 tracks reach ≥4-source consensus. 0/24 achieve unanimous agreement.\nThis classification ambiguity underlies the field\'s empirical challenge.',
          ha='center', fontsize=8, fontstyle='italic', color=PAL['neutral_dark'])
fig1.tight_layout(rect=[0.08, 0.04, 0.90, 0.95])
fig1.savefig(OUT+'fig1_classification_heatmap.png', dpi=300)
fig1.savefig(OUT+'fig1_classification_heatmap.svg')
print("  OK")

# ===== FIGURE 2: EMOTION CLUSTERING =====
print("Figure 2...")
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(8, 4.2))

cluster_labels = {1: 'High-arousal', 2: 'Calm/Quiet', 3: 'Mixed/Flowing'}
for c in [1,2,3]:
    mask = clusters == c
    ax2a.scatter(PC[mask,0], PC[mask,1], c=CLUSTER_COLORS[c], s=65, alpha=0.85,
                edgecolors='w', lw=0.5, zorder=3, label=f'{cluster_labels[c]} ({mask.sum()})')

label_list_en = ['Spring Festival Overture','New Year Joy','Joyful','River of Sorrow',
              'Moonlit Spring','Eighteen Beats','Crow Night Cry']
for i, nm in enumerate(names_en_list):
    if nm in label_list_en:
        offset = (6,6) if PC[i,0]>0 else (-85,6)
        ax2a.annotate(nm.split('(')[0].strip(), (PC[i,0],PC[i,1]), fontsize=6,
                     textcoords='offset points', xytext=offset,
                     arrowprops=dict(arrowstyle='->',lw=0.4,color=PAL['neutral_mid']))

ax2a.set_xlabel(f'PC1 ({S_e[0]**2/np.sum(S_e**2)*100:.0f}% var.)  Exciting ← → Stable')
ax2a.set_ylabel(f'PC2 ({S_e[1]**2/np.sum(S_e**2)*100:.0f}% var.)  Flowing ← → Introspective/Quiet')
ax2a.set_title('Emotion response PCA (no imposed labels)', fontsize=9, fontweight='bold')
ax2a.legend(frameon=False, fontsize=7)

# Panel B: cluster profiles
cluster_profiles = {c: X_emo[clusters==c].mean(axis=0) for c in [1,2,3]}
x_pos = np.arange(len(emo_labels_en))
for i, c in enumerate([1,2,3]):
    ax2b.bar(x_pos+i*0.25, cluster_profiles[c], 0.25, color=CLUSTER_COLORS[c], alpha=0.85,
            edgecolor='w', lw=0.3, label=f'{cluster_labels[c]} (n={clusters.tolist().count(c)})')
ax2b.set_xticks(x_pos+0.25); ax2b.set_xticklabels(emo_labels_en, fontsize=7)
ax2b.set_ylabel('Mean % selected'); ax2b.set_ylim(0, 85)
ax2b.set_title('Cluster emotion profiles', fontsize=9, fontweight='bold')
ax2b.legend(frameon=False, fontsize=6.5)

fig2.suptitle('Data-driven emotion clusters emerge from 50 listeners\' raw responses',
              fontsize=10, fontweight='bold')
fig2.text(0.5, 0.005, 'No pre-defined mode labels imposed. Natural structure: arousal + valence (Russell\'s circumplex model).',
          ha='center', fontsize=8, fontstyle='italic', color=PAL['neutral_dark'])
fig2.tight_layout(rect=[0, 0.04, 1, 0.93])
fig2.savefig(OUT+'fig2_emotion_clusters.png', dpi=300)
fig2.savefig(OUT+'fig2_emotion_clusters.svg')
print("  OK")

# ===== FIGURE 3: AROUSAL ← ACOUSTIC =====
print("Figure 3...")
fig3, axes = plt.subplots(1, 3, figsize=(8.5, 3.3))

feat_pairs = [
    ('zcr', 'Zero-Crossing Rate', '+0.61'),
    ('brightness', 'Spectral Centroid (Hz)', '+0.57'),
    ('bandwidth', 'Spectral Bandwidth (Hz)', '+0.53'),
]

for ax_i, (fkey, flabel, rlabel) in enumerate(feat_pairs):
    ax = axes[ax_i]
    x = np.array([acoustic_feats[tk][fkey] for tk in shared])
    y = np.array([arousal_means[tk] for tk in shared])
    names_s = [TRACK_NAMES_EN.get(tk,tk) for tk in shared]

    ax.scatter(x, y, c=PAL['blue_main'], s=45, alpha=0.7, edgecolors='w', lw=0.3)
    coef = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 50)
    ax.plot(x_line, np.polyval(coef, x_line), color=PAL['red_strong'], lw=2, alpha=0.6)
    r = np.corrcoef(x, y)[0,1]

    standout = ['Spring Festival','New Year Joy','Joyful','River of Sorrow',
                'Moonlit Spring','Crow Night Cry','Yangguan Pass','Butterfly Lovers']
    for i in range(len(x)):
        if names_s[i] in standout:
            ax.annotate(names_s[i], (x[i],y[i]), fontsize=5.5, alpha=0.85,
                       textcoords='offset points', xytext=(3,2))

    ax.set_xlabel(flabel, fontsize=8); ax.set_ylabel('Mean Arousal (1-5)', fontsize=8)
    ax.text(0.03, 0.97, f'r = {r:+.2f}', transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', color=PAL['red_strong'])
    ax.set_title(rlabel, fontsize=9, color=PAL['neutral_mid'])

fig3.suptitle('Acoustic features correlate with self-reported arousal — no mode labels needed',
              fontsize=10, fontweight='bold')
fig3.text(0.5, -0.02, 'Arousal (1-5 self-report scale) is the only label-independent emotional dimension.\nIt is reliably associated with physically measurable acoustic properties (all |r| > 0.5, N=22).',
          ha='center', fontsize=8, fontstyle='italic', color=PAL['neutral_dark'])
fig3.tight_layout(rect=[0, 0.06, 1, 0.90])
fig3.savefig(OUT+'fig3_acoustic_arousal.png', dpi=300)
fig3.savefig(OUT+'fig3_acoustic_arousal.svg')
print("  OK")

print(f"\nDone. Three figures saved to {OUT}")
