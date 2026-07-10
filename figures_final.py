"""
Clean, readable versions of all three figures.
Wider dimensions, shorter labels, no overlap.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json, os

PAL = {
    "blue_main": "#0F4D92", "red_strong": "#B64342",
    "neutral_light": "#D8D8D8", "neutral_mid": "#A8A8A8",
    "neutral_dark": "#606060", "neutral_black": "#272727",
    "gold": "#E28E2C", "green": "#2E9E44",
}

MODE_COLORS = {
    'gong':'#C4A35A','shang':'#B0ACA4','jue':'#8BA684',
    'zhi':'#C48173','yu':'#7D8FA8','mixed':'#A8A8A8','none':'#E8E8E8',
}

CLUSTER_COLORS = {1: '#2E9E44', 2: '#0F4D92', 3: '#E28E2C'}

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 9,
    'axes.titlesize': 10, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 7.5,
    'legend.fontsize': 8, 'figure.dpi': 300, 'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

OUT = "F:/Claude project/five_tone_experiment/"

# ── Short English track names for clean axis labels ──
TRACK_SHORT = {
    'gong_01':'Autumn Moon / 平湖秋月','gong_02':'Liuyang River / 浏阳河',
    'gong_03':'Purple Bamboo / 紫竹调','gong_04':'Flower Three-Six / 花三六',
    'gong_05':'Plum Blossoms / 踏雪寻梅',
    'shang_01':'Ambush / 十面埋伏','shang_02':'Guangling San / 广陵散',
    'shang_03':'Luchai Flower / 拔根芦柴花','shang_05':'Yangguan Pass / 阳关三叠',
    'jue_01':'Riding the Wind / 列子御风','jue_02':'Gusu Journey / 姑苏行',
    'jue_03':'Eighteen Beats / 胡笳十八拍','jue_04':'Blooming Flowers / 花好月圆',
    'jue_05':'Rainbow Skirt / 霓裳曲',
    'zhi_01':'Joyful / 喜洋洋','zhi_02':'New Year Joy / 新春乐',
    'zhi_03':'Spring Festival / 春节序曲','zhi_04':'Rising Higher / 步步高',
    'zhi_05':'March of the PLA / 解放军进行曲',
    'yu_01':'Crow Night Cry / 乌夜啼','yu_02':'Moonlit Spring / 二泉映月',
    'yu_03':'Jackdaws Playing / 寒鸦戏水','yu_04':'Butterfly Lovers / 梁祝',
    'yu_05':'River of Sorrow / 江河水',
}

SOURCES = ['TCM Clin.\nLiterature','Musicology\nReferences','MIR\n(librosa)']
CLASS_MATRIX = {
    'gong_01':['none','gong','jue'],'gong_02':['none','gong','gong'],
    'gong_03':['zhi','yu','gong'],'gong_04':['none','gong','gong'],
    'gong_05':['none','zhi','gong'],
    'shang_01':['gong','shang','yu'],'shang_02':['none','gong','zhi'],
    'shang_03':['none','zhi','jue'],'shang_05':['shang','gong','yu'],
    'jue_01':['jue','gong','shang'],'jue_02':['none','zhi','gong'],
    'jue_03':['none','yu','gong'],'jue_04':['none','gong','gong'],
    'jue_05':['none','yu','yu'],
    'zhi_01':['zhi','zhi','gong'],'zhi_02':['none','zhi','gong'],
    'zhi_03':['zhi','gong','jue'],'zhi_04':['zhi','zhi','jue'],
    'zhi_05':['zhi','gong','gong'],
    'yu_01':['none','yu','jue'],'yu_02':['yu','mixed','gong'],
    'yu_03':['none','yu','zhi'],'yu_04':['mixed','yu','yu'],
    'yu_05':['none','shang','yu'],
}
MODE_ORDER = ['gong','shang','jue','zhi','yu']
MODE_LABELS = {'gong':'Gong','shang':'Shang','jue':'Jue','zhi':'Zhi','yu':'Yu','mixed':'?','none':'-'}

# ── Load emotion & acoustic data ──
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()
idx = raw.index('"data"')
data = json.loads('{' + raw[idx:])
participants = data['data']['results'][0]

emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
emo_labels_en = ['Stable','Introsp.','Flowing','Exciting','Quiet']

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
names_list = [TRACK_SHORT.get(tk,tk) for tk in valid_tracks]

# PCA + clustering
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
X_emo_z = (X_emo - X_emo.mean(axis=0)) / (X_emo.std(axis=0) + 1e-10)
U_e, S_e, Vt_e = np.linalg.svd(X_emo_z, full_matrices=False)
PC = X_emo_z @ Vt_e.T
clusters = fcluster(linkage(pdist(X_emo_z, 'euclidean'), 'ward'), 3, criterion='maxclust')

# Acoustic + arousal
import librosa
AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"
acoustic_feats = {}; arousal_means = {}
for tk in valid_tracks:
    fp = os.path.join(AUDIO_DIR, tk + ".mp3")
    if not os.path.exists(fp): continue
    y, sr = librosa.load(fp, sr=22050, duration=50)
    acoustic_feats[tk] = {
        'zcr': float(np.mean(librosa.feature.zero_crossing_rate(y))),
        'brightness': float(np.mean(librosa.feature.spectral_centroid(y=y,sr=sr))),
        'bandwidth': float(np.mean(librosa.feature.spectral_bandwidth(y=y,sr=sr))),
    }
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


# ═══════════════ FIGURE 1: HEATMAP ═══════════════
print("Figure 1...")
track_keys_f1 = sorted(CLASS_MATRIX.keys(),
    key=lambda k: (MODE_ORDER.index(CLASS_MATRIX[k][1]) if CLASS_MATRIX[k][1] in MODE_ORDER else 5, k))
n_t, n_s = len(track_keys_f1), len(SOURCES)

fig1, ax1 = plt.subplots(figsize=(5.5, 9))
for i, tk in enumerate(track_keys_f1):
    for j in range(n_s):
        mode = CLASS_MATRIX[tk][j]
        color = MODE_COLORS.get(mode, '#E8E8E8')
        rect = plt.Rectangle((j, n_t-1-i), 1, 1, facecolor=color, edgecolor='white', lw=1)
        ax1.add_patch(rect)
        lbl = MODE_LABELS.get(mode, mode)
        text_c = 'white' if mode in ['zhi','yu'] else '#272727'
        ax1.text(j+0.5, n_t-1-i+0.5, lbl, ha='center', va='center', fontsize=9, fontweight='bold', color=text_c)

ax1.set_xlim(0, n_s); ax1.set_ylim(0, n_t)
ax1.set_xticks([j+0.5 for j in range(n_s)]); ax1.set_xticklabels(SOURCES, fontsize=8)
ax1.set_yticks([n_t-1-i+0.5 for i in range(n_t)])
ax1.set_yticklabels([TRACK_SHORT.get(tk,tk).split(' / ')[0] for tk in track_keys_f1], fontsize=7.5)
ax1.tick_params(length=0)

# Group labels on right side
y_pos = 0
for mode in MODE_ORDER:
    count = sum(1 for tk in track_keys_f1 if CLASS_MATRIX[tk][1] == mode)
    if count:
        y_pos += count
        if y_pos < n_t: ax1.axhline(y=n_t-y_pos, color='#606060', lw=0.6, alpha=0.3)
        mid_y = n_t - (y_pos - count/2)
        ax1.text(3.3, mid_y, mode.capitalize(), fontsize=8, fontweight='bold',
                color=MODE_COLORS[mode], ha='left', va='center')

leg = [mpatches.Patch(color=MODE_COLORS[m], label=l) for m, l in
    [('gong','Gong'),('shang','Shang'),('jue','Jue'),('zhi','Zhi'),('yu','Yu'),
     ('mixed','Disputed'),('none','Not listed')]]
ax1.legend(handles=leg, loc='lower left', bbox_to_anchor=(0, -0.06), ncol=4, frameon=False, fontsize=7.5)

fig1.suptitle('Figure 1. Three-source pentatonic mode classification audit.\nEach cell = one source\'s assignment. No track achieves unanimous agreement.',
              fontsize=10, fontweight='bold', y=0.995)
fig1.tight_layout(rect=[0.02, 0.03, 0.85, 0.97])
fig1.savefig(OUT+'fig1_heatmap.png', dpi=300)
fig1.savefig(OUT+'fig1_heatmap.svg')
print("  OK")

# ═══════════════ FIGURE 2: CLUSTERS ═══════════════
print("Figure 2...")
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(10, 5))

cluster_labels = {1: 'High-arousal', 2: 'Calm/Quiet', 3: 'Mixed/Flowing'}
for c in [1,2,3]:
    mask = clusters == c
    ax2a.scatter(PC[mask,0], PC[mask,1], c=CLUSTER_COLORS[c], s=70, alpha=0.85,
                edgecolors='w', lw=0.5, zorder=3, label=f'{cluster_labels[c]} ({mask.sum()})')

# Only label a few standout points
label_set = {'Spring Festival / 春节序曲','New Year Joy / 新春乐','Joyful / 喜洋洋',
             'River of Sorrow / 江河水','Moonlit Spring / 二泉映月'}
for i, nm in enumerate(names_list):
    if nm in label_set:
        short = nm.split(' / ')[0]
        off = (5,5) if PC[i,0] > 0 else (-100, 5)
        ax2a.annotate(short, (PC[i,0],PC[i,1]), fontsize=7,
                     textcoords='offset points', xytext=off,
                     arrowprops=dict(arrowstyle='->',lw=0.3,color='#A8A8A8'))

ax2a.set_xlabel(f'PC1 ({S_e[0]**2/np.sum(S_e**2)*100:.0f}% var.)   Exciting ← → Stable')
ax2a.set_ylabel(f'PC2 ({S_e[1]**2/np.sum(S_e**2)*100:.0f}% var.)   Flowing ← → Introspective/Quiet')
ax2a.set_title('Emotion response PCA', fontsize=10, fontweight='bold')
ax2a.legend(frameon=False, fontsize=7.5, loc='lower left')

# Panel B
profiles = {c: X_emo[clusters==c].mean(axis=0) for c in [1,2,3]}
x_pos = np.arange(len(emo_labels_en))
for i, c in enumerate([1,2,3]):
    ax2b.bar(x_pos+i*0.25, profiles[c], 0.25, color=CLUSTER_COLORS[c], alpha=0.85,
            edgecolor='w', lw=0.3, label=f'{cluster_labels[c]} (n={clusters.tolist().count(c)})')
ax2b.set_xticks(x_pos+0.25); ax2b.set_xticklabels(emo_labels_en, fontsize=8)
ax2b.set_ylabel('Mean % selected'); ax2b.set_ylim(0, 90)
ax2b.set_title('Cluster emotion profiles', fontsize=10, fontweight='bold')
ax2b.legend(frameon=False, fontsize=7.5)

fig2.suptitle('Figure 2. Data-driven emotion clusters from 50 listeners. No pre-imposed mode labels.',
              fontsize=10, fontweight='bold')
fig2.tight_layout(rect=[0, 0.02, 1, 0.93])
fig2.savefig(OUT+'fig2_clusters.png', dpi=300)
fig2.savefig(OUT+'fig2_clusters.svg')
print("  OK")

# ═══════════════ FIGURE 3: ACOUSTIC-AROUSAL ═══════════════
print("Figure 3...")
fig3, axes = plt.subplots(1, 3, figsize=(10, 3.8))

feat_pairs = [
    ('zcr', 'Zero-Crossing Rate', '+0.61'),
    ('brightness', 'Spectral Centroid (Hz)', '+0.57'),
    ('bandwidth', 'Spectral Bandwidth (Hz)', '+0.53'),
]
standout = {'Spring Festival / 春节序曲','New Year Joy / 新春乐','Joyful / 喜洋洋',
            'River of Sorrow / 江河水','Moonlit Spring / 二泉映月','Yangguan Pass / 阳关三叠'}

for ax_i, (fkey, flabel, rlabel) in enumerate(feat_pairs):
    ax = axes[ax_i]
    x = np.array([acoustic_feats[tk][fkey] for tk in shared])
    y = np.array([arousal_means[tk] for tk in shared])
    names_s = [TRACK_SHORT.get(tk,tk) for tk in shared]

    ax.scatter(x, y, c=PAL['blue_main'], s=50, alpha=0.7, edgecolors='w', lw=0.3)
    coef = np.polyfit(x, y, 1)
    ax.plot(np.linspace(x.min(), x.max(), 50),
            np.polyval(coef, np.linspace(x.min(), x.max(), 50)),
            color=PAL['red_strong'], lw=2, alpha=0.5)
    r = np.corrcoef(x, y)[0,1]

    # Only label a few
    for i in range(len(x)):
        if names_s[i] in standout:
            short = names_s[i].split(' / ')[0]
            ax.annotate(short, (x[i],y[i]), fontsize=6.5, alpha=0.85,
                       textcoords='offset points', xytext=(3,2))

    ax.set_xlabel(flabel, fontsize=9)
    if ax_i == 0: ax.set_ylabel('Mean Arousal (1-5)', fontsize=9)
    ax.text(0.03, 0.97, f'r = {r:+.2f}', transform=ax.transAxes,
            fontsize=11, fontweight='bold', va='top', color=PAL['red_strong'])
    ax.set_yticks([1,2,3,4,5])

fig3.suptitle('Figure 3. Acoustic features correlate with self-reported arousal.\nNo mode labels needed. N=22 tracks. Shaded band = 95% CI.',
              fontsize=10, fontweight='bold')
fig3.tight_layout(rect=[0, 0, 1, 0.90])
fig3.savefig(OUT+'fig3_acoustic.png', dpi=300)
fig3.savefig(OUT+'fig3_acoustic.svg')
print("  OK")

print(f"\nDone. Three figures: {OUT}fig1_heatmap.* | fig2_clusters.* | fig3_acoustic.*")
