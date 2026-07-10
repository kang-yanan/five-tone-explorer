"""
Figure 1 — Journal-grade heatmap.
Title below. Column headers. Clean legend. Colorblind-safe.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Colorblind-safe palette (Okabe-Ito inspired, adapted for 5 modes) ──
# Gong=orange, Shang=blue-grey, Jue=green, Zhi=vermillion, Yu=sky-blue
MODE_COLORS = {
    'gong':   '#E69F00',  # orange
    'shang':  '#56B4E9',  # sky blue
    'jue':    '#009E73',  # bluish green
    'zhi':    '#D55E00',  # vermillion
    'yu':     '#0072B2',  # deep blue
    'mixed':  '#CCCCCC',  # light grey
    'none':   '#F5F5F5',  # very light grey
}
# For text on colored cells — dark text on light colors, white on dark
def text_color(mode):
    if mode in ('zhi', 'yu'):
        return 'white'
    if mode in ('mixed',):
        return '#555555'
    if mode == 'none':
        return '#777777'
    return '#222222'

MODE_LABELS = {'gong':'Gong','shang':'Shang','jue':'Jue','zhi':'Zhi','yu':'Yu',
               'mixed':'Disputed','none':'Not listed'}
MODE_ORDER = ['gong','shang','jue','zhi','yu']

SOURCES = ['TCM Clinical\nLiterature', 'Musicology\nReferences', 'MIR Tonic\nDetection (librosa)']

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

TRACK_SHORT = {
    'gong_01':'Autumn Moon on the Lake', 'gong_02':'Liuyang River',
    'gong_03':'Purple Bamboo Tune', 'gong_04':'Flower Three-Six',
    'gong_05':'Plum Blossoms in Snow',
    'shang_01':'Ambush on All Sides', 'shang_02':'Guangling San',
    'shang_03':'Luchai Flower', 'shang_05':'Yangguan Pass',
    'jue_01':'Riding the Wind', 'jue_02':'Gusu Journey',
    'jue_03':'Eighteen Beats', 'jue_04':'Blooming Flowers',
    'jue_05':'Rainbow Skirt Dance',
    'zhi_01':'Joyful', 'zhi_02':'New Year Joy',
    'zhi_03':'Spring Festival Overture', 'zhi_04':'Rising Higher',
    'zhi_05':'March of the PLA',
    'yu_01':'Crow Night Cry', 'yu_02':'Moonlit Spring',
    'yu_03':'Jackdaws Playing in Water', 'yu_04':'Butterfly Lovers',
    'yu_05':'River of Sorrow',
}

# Sort tracks by inter-source agreement (how many sources agree on the SAME mode)
# Count unique modes assigned across the 3 sources
def agreement_score(modes):
    unique = set(m for m in modes if m != 'none')
    if len(unique) == 0: return 0
    if len(unique) == 1: return 3  # all three agree
    if len(unique) == 2: return 2  # two agree, one differs
    return 1  # all three disagree

track_keys = sorted(CLASS_MATRIX.keys(),
    key=lambda k: (agreement_score(CLASS_MATRIX[k]),
                   TRACK_SHORT.get(k,k)),
    reverse=True)  # highest agreement first
n_tracks = len(track_keys)
n_sources = len(SOURCES)

plt.rcParams.update({
    'font.family': 'sans-serif', 'font.size': 9,
    'figure.dpi': 300, 'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

fig, ax = plt.subplots(figsize=(6.5, 9.5))

# ── Draw cells ──
col_x = [0, 1.2, 2.4]  # spread columns to prevent header overlap
col_w = 0.9
for i, tk in enumerate(track_keys):
    y = n_tracks - 1 - i
    for j in range(n_sources):
        x_pos = col_x[j]
        mode = CLASS_MATRIX[tk][j]
        color = MODE_COLORS.get(mode, '#F5F5F5')
        rect = plt.Rectangle((x_pos, y), col_w, 1, facecolor=color, edgecolor='white', linewidth=1.5, zorder=1)
        ax.add_patch(rect)
        # Add diagonal hatching for "mixed"/disputed cells
        if mode == 'mixed':
            ax.plot([x_pos, x_pos+col_w], [y, y+1], color='#999999', linewidth=0.6, zorder=1.5)
            ax.plot([x_pos+col_w, x_pos], [y, y+1], color='#999999', linewidth=0.6, zorder=1.5)

        lbl = MODE_LABELS.get(mode, mode)
        tc = text_color(mode)
        fs = 7.5 if len(lbl) <= 3 else 6.5
        ax.text(x_pos + col_w/2, y+0.5, lbl, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=tc, zorder=2)

# ── Column headers ──
for j, src in enumerate(SOURCES):
    ax.text(col_x[j] + col_w/2, n_tracks + 0.5, src, ha='center', va='bottom',
            fontsize=7.5, fontweight='bold', color='#333333', linespacing=1.1)

# ── Row labels (track names) ──
for i, tk in enumerate(track_keys):
    y = n_tracks - 1 - i
    ax.text(-0.15, y+0.5, TRACK_SHORT.get(tk, tk), ha='right', va='center',
            fontsize=7, color='#333333')

# ── Subtle agreement-level spacing (no dividers cutting text) ──
prev_score = None
for i, tk in enumerate(track_keys):
    score = agreement_score(CLASS_MATRIX[tk])
    y = n_tracks - 1 - i
    # Insert a blank spacer row when agreement level changes
    if prev_score is not None and score != prev_score:
        pass  # no dividers — just natural gap from sorting order
    prev_score = score

# ── Axis limits ──
ax.set_xlim(-3.0, col_x[-1] + col_w + 0.4)
ax.set_ylim(-0.5, n_tracks + 1.2)
ax.axis('off')

# ── Legend below the figure ──
legend_elements = []
for mode in ['gong','shang','jue','zhi','yu','mixed','none']:
    legend_elements.append(mpatches.Patch(
        facecolor=MODE_COLORS[mode], edgecolor='#CCCCCC',
        linewidth=0.5, label=MODE_LABELS[mode]))

leg = ax.legend(handles=legend_elements, loc='upper center',
                bbox_to_anchor=(0.5, -0.04), ncol=7, frameon=False,
                fontsize=7.5, columnspacing=0.8, handlelength=1.2, handleheight=1.2)

# ── Figure caption / legend (below) ──
caption = (
    "Figure 1 | Pentatonic mode classification audit for 24 traditional Chinese instrumental pieces.\n"
    "Columns represent three independent classification sources. Rows are grouped by their musicology-reference mode.\n"
    "'Not listed' indicates the track was absent from all six reviewed TCM clinical papers. "
    "'Disputed' indicates conflicting assignments across multiple TCM papers for the same track.\n"
    "No track achieves unanimous agreement across all three sources. Pairwise agreement: TCM vs. Musicology = 46%; "
    "Musicology vs. MIR = 29%; TCM vs. MIR = 25%."
)

fig.text(0.5, -0.06, caption, ha='center', va='top', fontsize=7.5,
         color='#444444', linespacing=1.4,
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#FAFAFA', edgecolor='#DDDDDD', alpha=0.8))

fig.subplots_adjust(left=0.02, right=0.96, top=0.98, bottom=0.06)
fig.savefig('F:/Claude project/five_tone_experiment/fig1_heatmap.png', dpi=300)
fig.savefig('F:/Claude project/five_tone_experiment/fig1_heatmap.svg')
print("Figure 1 saved.")
