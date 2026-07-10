"""
Morandi Color Palette — Shared styling for all figures.
Dusty, muted, low-saturation, high-end visual presentation.
"""
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ── Morandi Palette ──
MORANDI = {
    'dusty_rose':   '#C4A8A0',  # warm muted pink
    'sage_green':   '#A3B5A6',  # muted green
    'muted_blue':   '#8A9BA8',  # dusty blue
    'warm_grey':    '#B8B0A6',  # warm neutral grey
    'dusty_lavender':'#B0A8B8', # muted purple
    'pale_terracotta':'#C9A99A',# earthy clay
    'faded_teal':   '#9AABA0',  # muted teal
    'cream':        '#F5F0EB',  # off-white background
    'charcoal':     '#4A4540',  # dark text
    'warm_dark':    '#6B5E55',  # medium text
    'light_warm':   '#E8E2DA',  # light accent
    'divider':      '#D5CFC7',  # subtle border/grid
}

# ── Color assignments for specific elements ──
CLUSTER_COLORS = {
    1: MORANDI['dusty_rose'],     # High-arousal
    2: MORANDI['muted_blue'],     # Calm/Quiet
    3: MORANDI['sage_green'],     # Mixed/Flowing
}
CHINESE_COLOR = MORANDI['dusty_rose']
WESTERN_COLOR = MORANDI['dusty_lavender']
ACCENT = MORANDI['pale_terracotta']
BG = MORANDI['cream']
TEXT = MORANDI['charcoal']
TEXT_SEC = MORANDI['warm_dark']

# ── Figure defaults ──
def setup_style():
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 9,
        'axes.titlesize': 10,
        'axes.labelsize': 9,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'legend.fontsize': 8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'axes.facecolor': BG,
        'figure.facecolor': BG,
        'axes.edgecolor': MORANDI['divider'],
        'axes.grid': False,
        'xtick.color': TEXT_SEC,
        'ytick.color': TEXT_SEC,
        'text.color': TEXT,
    })
    for f in fm.fontManager.ttflist:
        if 'YaHei' in f.name or 'SimHei' in f.name:
            plt.rcParams['font.sans-serif'] = [f.name, 'Arial', 'DejaVu Sans']
            break

def morandi_cmap(n=5):
    """Return a list of n Morandi colors."""
    palette = list(MORANDI.values())[:8]
    return palette[:n] if n <= len(palette) else palette * (n // len(palette) + 1)[:n]

def set_axes_color(ax):
    """Apply Morandi styling to an axes."""
    ax.set_facecolor(BG)
    ax.tick_params(direction='in', length=3, width=0.6, colors=TEXT_SEC)
    for spine in ax.spines.values():
        spine.set_color(MORANDI['divider'])
        spine.set_linewidth(0.5)

def caption(text, fig, y=-0.06):
    """Add a Morandi-styled caption below the figure."""
    fig.text(0.5, y, text, ha='center', fontsize=7.5, color=TEXT_SEC,
             linespacing=1.3, fontstyle='italic')

def panel_label(ax, label, x=-0.06, y=1.04):
    """Add a bold panel label (a, b, c)."""
    ax.text(x, y, label, transform=ax.transAxes, fontsize=11, fontweight='bold', va='bottom', color=TEXT)
