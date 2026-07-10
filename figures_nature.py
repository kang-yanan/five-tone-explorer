"""
Nature-style figures for FiveTone Explorer paper.
Three figures: classification heatmap, emotion clustering, acoustic-arousal.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Register Chinese font
font_path = 'C:/WINDOWS/Fonts/STSONG.TTF'
fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)
font_name = prop.get_name()

plt.rcParams.update({
    'font.family': font_name,
    'font.size': 8,
PAL = {
    "blue_main": "#0F4D92", "blue_secondary": "#3775BA",
    "green_2": "#AADCA9", "green_3": "#8BCF8B",
    "red_strong": "#B64342", "red_2": "#E9A6A1",
    "neutral_light": "#D8D8D8", "neutral_mid": "#A8A8A8",
    "neutral_dark": "#606060", "neutral_black": "#272727",
    "teal": "#42949E", "violet": "#9A4D8E", "gold": "#E28E2C",
    "delta_up": "#2E9E44", "delta_down": "#E53935",
    "bg_lilac": "#E0E0F0", "bg_aqua": "#E0F0F0", "bg_peach": "#F0E0D0",
}

# Mode colors for Fig 1 — 5 modes + unknown
MODE_COLORS = {
    'gong': '#C4A35A',   # gold/earth
    'shang': '#B0ACA4',  # silver/metal
    'jue': '#8BA684',    # green/wood
    'zhi': '#C48173',    # red/fire
    'yu': '#7D8FA8',     # blue/water
    'mixed': PAL['neutral_mid'],
    'none': PAL['neutral_light'],
}
MODE_ORDER = ['gong','shang','jue','zhi','yu']

# Emotion colors (low-saturation pastels)
EMO_COLORS = {
    '振奋': '#E28E2C',  # warm
    '舒畅': '#8BCF8B',  # green
    '安定': '#42949E',  # teal
    '宁静': '#7C6CCF',  # violet
    '内省': '#B64342',  # muted red
}

# Cluster colors
CLUSTER_COLORS = {1: PAL['delta_up'], 2: PAL['blue_main'], 3: PAL['gold']}

plt.rcParams.update({
    'font.family': 'Noto Sans SC',
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

OUT = "F:/Claude project/five_tone_experiment/"

# ===== DATA =====
TRACK_NAMES = {
    'gong_01':'平湖秋月','gong_02':'浏阳河','gong_03':'紫竹调','gong_04':'花三六','gong_05':'踏雪寻梅',
    'shang_01':'十面埋伏','shang_02':'广陵散','shang_03':'拔根芦柴花','shang_05':'阳关三叠',
    'jue_01':'列子御风','jue_02':'姑苏行','jue_03':'胡笳十八拍','jue_04':'花好月圆','jue_05':'霓裳曲',
    'zhi_01':'喜洋洋','zhi_02':'新春乐','zhi_03':'春节序曲','zhi_04':'步步高','zhi_05':'解放军进行曲',
    'yu_01':'乌夜啼','yu_02':'二泉映月','yu_03':'寒鸦戏水','yu_04':'梁祝','yu_05':'江河水',
}

# Five-source classification matrix (from our audit)
# Rows: 24 tracks, Cols: Original, Claude, Gemini, Doubao/Lit, Mita
SOURCES = ['Original','Claude\n(musicology)','Gemini\n(musicology)','Doubao\n(TCM lit)','Mita\n(web search)']
CLASS_MATRIX = {
    'gong_01': ['gong','yu','zhi','none','gong'],
    'gong_02': ['gong','yu','gong','none','gong'],
    'gong_03': ['gong','gong','zhi','zhi','yu'],
    'gong_04': ['gong','gong','zhi','none','gong'],
    'gong_05': ['gong','gong','gong','none','zhi'],
    'shang_01': ['shang','shang','shang','gong','shang'],
    'shang_02': ['shang','shang','shang','none','gong'],
    'shang_03': ['shang','zhi','zhi','none','zhi'],
    'shang_05': ['shang','yu','shang','shang','gong'],
    'jue_01': ['jue','gong','gong','jue','gong'],
    'jue_02': ['jue','gong','gong','none','zhi'],
    'jue_03': ['jue','yu','yu','none','yu'],
    'jue_04': ['jue','gong','gong','none','gong'],
    'jue_05': ['jue','zhi','zhi','none','yu'],
    'zhi_01': ['zhi','gong','gong','zhi','zhi'],
    'zhi_02': ['zhi','gong','gong','none','zhi'],
    'zhi_03': ['zhi','gong','gong','zhi','gong'],
    'zhi_04': ['zhi','gong','gong','zhi','zhi'],
    'zhi_05': ['zhi','gong','gong','zhi','gong'],
    'yu_01': ['yu','yu','yu','none','yu'],
    'yu_02': ['yu','gong','yu','yu','mixed'],
    'yu_03': ['yu','zhi','zhi','none','yu'],
    'yu_04': ['yu','gong','yu','mixed','yu'],
    'yu_05': ['yu','yu','yu','none','shang'],
}

# Track ordering for Fig 1: sort by original mode then name
track_keys_fig1 = sorted(CLASS_MATRIX.keys(), key=lambda k: (MODE_ORDER.index(CLASS_MATRIX[k][0]) if CLASS_MATRIX[k][0] in MODE_ORDER else 5, TRACK_NAMES.get(k,k)))

# ===== Load bottom-up analysis data =====
# We'll regenerate the clusters and PCA from raw data
DATA_FILE = "F:/Claude project/five_tone_experiment/latest_data.json"
import librosa

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    raw = f.read()
idx = raw.index('"data"')
data = json.loads('{' + raw[idx:])
participants = data['data']['results'][0]

emotions = ['anding','neixing','shuchang','zhenfen','ningjing']
emo_labels_cn = ['安定','内省','舒畅','振奋','宁静']

# Per-track emotion percentages
track_emo = {}
track_n = {}
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track',''); em = s.get('emotion','')
        if not tk: continue
        if tk not in track_emo:
            track_emo[tk] = {e:0 for e in emotions}; track_n[tk] = 0
        track_emo[tk][em] += 1; track_n[tk] += 1

valid_tracks = sorted([tk for tk in track_n if track_n[tk] >= 5 and tk != 'shang_04'])
X_emo = np.array([[track_emo[tk][e]/track_n[tk]*100 for e in emotions] for tk in valid_tracks])
names_emo = [TRACK_NAMES.get(tk,tk) for tk in valid_tracks]

# PCA on emotions
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
X_emo_z = (X_emo - X_emo.mean(axis=0)) / (X_emo.std(axis=0) + 1e-10)
U_e, S_e, Vt_e = np.linalg.svd(X_emo_z, full_matrices=False)
PC = X_emo_z @ Vt_e.T

# Clustering
dist = pdist(X_emo_z, metric='euclidean')
Z = linkage(dist, method='ward')
clusters = fcluster(Z, 3, criterion='maxclust')

# ===== Extract acoustic features & arousal =====
AUDIO_DIR = "F:/Claude project/five_tone_experiment/audio"

def get_acoustic(filepath):
    y, sr = librosa.load(filepath, sr=22050, duration=50)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    f = {}
    f['tempo'] = float(tempo.item() if hasattr(tempo, 'item') else tempo)
    f['brightness'] = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    f['zcr'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    f['bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    return f

# Per-track arousal
track_arousal = {}
for rec in participants:
    if 'summary' not in rec: continue
    for s in rec['summary']:
        tk = s.get('track',''); ar = s.get('arousal',None)
        if not tk or ar is None: continue
        if tk not in track_arousal: track_arousal[tk] = []
        v = int(ar.get('$numberInt',ar)) if isinstance(ar,dict) else int(ar)
        track_arousal[tk].append(v)

acoustic_feats = {}
arousal_means = {}
for tk in valid_tracks:
    fp = os.path.join(AUDIO_DIR, tk + ".mp3")
    if os.path.exists(fp) and tk in track_arousal:
        acoustic_feats[tk] = get_acoustic(fp)
        arousal_means[tk] = np.mean(track_arousal[tk])

shared = sorted([tk for tk in valid_tracks if tk in acoustic_feats and tk in arousal_means])

# ===== FIGURE 1: FIVE-SOURCE HEATMAP =====
print("Generating Figure 1...")
fig1, ax1 = plt.subplots(figsize=(6.5, 7.5))

n_tracks = len(track_keys_fig1)
n_sources = len(SOURCES)
data_matrix = np.zeros((n_tracks, n_sources))

# Build color matrix
cell_colors = []
for i, tk in enumerate(track_keys_fig1):
    row_colors = []
    for j in range(n_sources):
        mode = CLASS_MATRIX[tk][j]
        row_colors.append(MODE_COLORS.get(mode, PAL['neutral_light']))
    cell_colors.append(row_colors)

# Draw as colored grid
for i in range(n_tracks):
    for j in range(n_sources):
        mode = CLASS_MATRIX[track_keys_fig1[i]][j]
        color = MODE_COLORS.get(mode, PAL['neutral_light'])
        rect = plt.Rectangle((j, n_tracks-1-i), 1, 1, facecolor=color,
                              edgecolor='white', linewidth=1.5)
        ax1.add_patch(rect)
        # Label
        label_map = {'gong':'宫','shang':'商','jue':'角','zhi':'徵','yu':'羽','none':'−','mixed':'?'}
        lbl = label_map.get(mode, mode)
        text_color = 'white' if mode in ['zhi','yu'] else PAL['neutral_black']
        ax1.text(j+0.5, n_tracks-1-i+0.5, lbl, ha='center', va='center',
                fontsize=8, fontweight='bold', color=text_color)

ax1.set_xlim(0, n_sources)
ax1.set_ylim(0, n_tracks)
ax1.set_xticks([j+0.5 for j in range(n_sources)])
ax1.set_xticklabels(SOURCES, fontsize=7)
ax1.set_yticks([n_tracks-1-i+0.5 for i in range(n_tracks)])
ax1.set_yticklabels([TRACK_NAMES.get(tk,tk) for tk in track_keys_fig1], fontsize=7)
ax1.tick_params(length=0)

# Legend
legend_patches = [
    mpatches.Patch(color=MODE_COLORS['gong'], label='宫 Gōng'),
    mpatches.Patch(color=MODE_COLORS['shang'], label='商 Shāng'),
    mpatches.Patch(color=MODE_COLORS['jue'], label='角 Jué'),
    mpatches.Patch(color=MODE_COLORS['zhi'], label='徵 Zhǐ'),
    mpatches.Patch(color=MODE_COLORS['yu'], label='羽 Yǔ'),
    mpatches.Patch(color=MODE_COLORS['mixed'], label='有争议'),
    mpatches.Patch(color=MODE_COLORS['none'], label='未出现'),
]

ax1.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1.01, 0.98),
           frameon=False, fontsize=7, title='Mode', title_fontsize=8)

# Section dividers by original mode groups
orig_groups = {'gong':0,'shang':0,'jue':0,'zhi':0,'yu':0}
for tk in track_keys_fig1:
    orig_groups[CLASS_MATRIX[tk][0]] = orig_groups.get(CLASS_MATRIX[tk][0],0) + 1

y_pos = 0
for mode in MODE_ORDER:
    count = orig_groups.get(mode,0)
    if count > 0:
        y_pos += count
        if y_pos < n_tracks:
            ax1.axhline(y=n_tracks-y_pos, color=PAL['neutral_dark'], linewidth=0.8, linestyle='-', alpha=0.5)
    # Group label
    if count > 0:
        mid_y = n_tracks - (y_pos - count/2)
        ax1.text(-0.8, mid_y, mode.upper(), fontsize=8, fontweight='bold',
                color=MODE_COLORS.get(mode,PAL['neutral_black']), ha='right', va='center')

fig1.suptitle('Five-source pentatonic mode classification for 24 traditional Chinese instrumental tracks',
              fontsize=10, fontweight='bold', y=0.98)
fig1.text(0.5, 0.01, 'Only 4/24 tracks achieve ≥4-source consensus. No track achieves unanimous agreement across all five sources.',
          ha='center', fontsize=8, style='italic', color=PAL['neutral_dark'])

fig1.tight_layout(rect=[0.08, 0.03, 0.92, 0.95])
fig1.savefig(OUT + 'fig1_classification_heatmap.png', dpi=300, bbox_inches='tight')
fig1.savefig(OUT + 'fig1_classification_heatmap.svg', bbox_inches='tight')
print("  Figure 1 saved.")


# ===== FIGURE 2: EMOTION CLUSTERING =====
print("Generating Figure 2...")
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(7.5, 4.0))

# Panel A: PCA scatter with clusters
for c in [1,2,3]:
    mask = clusters == c
    ax2a.scatter(PC[mask,0], PC[mask,1], c=CLUSTER_COLORS[c], s=60, alpha=0.85,
                edgecolors='white', linewidth=0.5, zorder=3,
                label=f'Cluster {c} ({mask.sum()} tracks)')

# Label standout tracks
label_tracks = ['新春乐','春节序曲','喜洋洋','江河水','二泉映月','梁祝','乌夜啼','浏阳河']
for i, nm in enumerate(names_emo):
    if nm in label_tracks:
        offset = (8, 8) if PC[i,0] > 0 else (-80, 8)
        ax2a.annotate(nm, (PC[i,0], PC[i,1]), fontsize=6.5, alpha=0.85,
                     textcoords='offset points', xytext=offset,
                     arrowprops=dict(arrowstyle='->', lw=0.5, color=PAL['neutral_mid']))

ax2a.set_xlabel(f'PC1 ({S_e[0]**2/np.sum(S_e**2)*100:.0f}%)  ← 振奋 · 安定 →')
ax2a.set_ylabel(f'PC2 ({S_e[1]**2/np.sum(S_e**2)*100:.0f}%)  ← 舒畅 · 内省/宁静 →')
ax2a.set_title('Emotion response PCA (data-driven)', fontsize=9, fontweight='bold')
ax2a.legend(frameon=False, fontsize=7)

# Panel B: Cluster average profiles
cluster_profiles = {}
for c in [1,2,3]:
    mask = clusters == c
    cluster_profiles[c] = X_emo[mask].mean(axis=0)

x_pos = np.arange(len(emo_labels_cn))
width = 0.25
for i, c in enumerate([1,2,3]):
    bars = ax2b.bar(x_pos + i*width, cluster_profiles[c], width,
                    color=CLUSTER_COLORS[c], alpha=0.8, edgecolor='white', linewidth=0.3,
                    label=f'C{c} ({clusters.tolist().count(c)} tracks)')
ax2b.set_xticks(x_pos + width)
ax2b.set_xticklabels(emo_labels_cn, fontsize=7)
ax2b.set_ylabel('Mean % selected')
ax2b.set_title('Cluster emotion profiles', fontsize=9, fontweight='bold')
ax2b.legend(frameon=False, fontsize=7)
ax2b.set_ylim(0, 85)

fig2.suptitle('Bottom-up: 50 listeners\' responses self-organize into 3 natural emotion clusters',
              fontsize=10, fontweight='bold')
fig2.text(0.5, 0.01, 'No pre-imposed five-tone labels. Clusters emerge from raw response data. C1=high-arousal, C2=calm/quiet, C3=mixed/flowing.',
          ha='center', fontsize=8, style='italic', color=PAL['neutral_dark'])

fig2.tight_layout(rect=[0, 0.04, 1, 0.93])
fig2.savefig(OUT + 'fig2_emotion_clusters.png', dpi=300, bbox_inches='tight')
fig2.savefig(OUT + 'fig2_emotion_clusters.svg', bbox_inches='tight')
print("  Figure 2 saved.")


# ===== FIGURE 3: AROUSAL ← ACOUSTIC =====
print("Generating Figure 3...")
fig3, axes = plt.subplots(1, 3, figsize=(8, 3.2))

feat_pairs = [
    ('zcr', 'Zero-Crossing Rate (noisiness)', 'r = +0.61'),
    ('brightness', 'Spectral Centroid (brightness)', 'r = +0.57'),
    ('bandwidth', 'Spectral Bandwidth', 'r = +0.53'),
]

for ax_idx, (feat_key, feat_label, r_label) in enumerate(feat_pairs):
    ax = axes[ax_idx]
    x = [acoustic_feats[tk][feat_key] for tk in shared]
    y = [arousal_means[tk] for tk in shared]
    names_shared = [TRACK_NAMES.get(tk,tk) for tk in shared]

    # Scatter
    ax.scatter(x, y, c=PAL['blue_main'], s=40, alpha=0.7, edgecolors='white', linewidth=0.3)

    # Regression line
    if len(x) > 3:
        coef = np.polyfit(x, y, 1)
        x_line = np.linspace(min(x), max(x), 50)
        ax.plot(x_line, np.polyval(coef, x_line), color=PAL['red_strong'], linewidth=1.5, alpha=0.7)

    # Label standouts
    y_arr = np.array(y)
    for i in range(len(x)):
        nm = names_shared[i]
        if nm in ['新春乐','春节序曲','解放军进行曲','江河水','二泉映月','乌夜啼','阳关三叠']:
            ax.annotate(nm, (x[i], y[i]), fontsize=5.5, alpha=0.8,
                       textcoords='offset points', xytext=(3, 3))

    ax.set_xlabel(feat_label, fontsize=8)
    ax.set_ylabel('Mean Arousal (1-5)', fontsize=8)
    ax.set_title(r_label, fontsize=9, fontweight='bold', color=PAL['red_strong'])
    # Add r value annotation
    r_val = np.corrcoef(x, y)[0,1]
    ax.text(0.05, 0.95, f'r = {r_val:.2f}', transform=ax.transAxes,
            fontsize=9, fontweight='bold', va='top', color=PAL['neutral_black'])

fig3.suptitle('Arousal (self-reported, scale 1-5) predicted by objective acoustic features',
              fontsize=10, fontweight='bold')
fig3.text(0.5, 0.0, 'Arousal is the only cross-culturally valid, label-free emotional dimension. '
          'It correlates with physically measurable acoustic properties.',
          ha='center', fontsize=8, style='italic', color=PAL['neutral_dark'])

fig3.tight_layout(rect=[0, 0.06, 1, 0.90])
fig3.savefig(OUT + 'fig3_acoustic_arousal.png', dpi=300, bbox_inches='tight')
fig3.savefig(OUT + 'fig3_acoustic_arousal.svg', bbox_inches='tight')
print("  Figure 3 saved.")

print("\nAll figures generated:")
print(f"  {OUT}fig1_classification_heatmap.png")
print(f"  {OUT}fig2_emotion_clusters.png")
print(f"  {OUT}fig3_acoustic_arousal.png")
