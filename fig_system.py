"""
Figure: FiveTone Explorer System Architecture
Solution Overview — Paradigm B: System Architecture
Client-cloud layout with component boxes and data-flow arrows.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans'],
    'font.size': 8.5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})
# Force matplotlib to find CJK-capable font
import matplotlib.font_manager as fm
for f in fm.fontManager.ttflist:
    if 'YaHei' in f.name or 'SimHei' in f.name:
        plt.rcParams['font.sans-serif'] = [f.name] + plt.rcParams['font.sans-serif']
        break

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.set_xlim(0, 9)
ax.set_ylim(0, 5.5)
ax.axis('off')

# ── Colour palette ──
C_PHONE_BG   = '#F0F4F8'  # light blue-grey for phone zone
C_CLOUD_BG   = '#FFF8F0'  # light warm for cloud zone
C_COMP_PHONE = '#2563EB'  # blue for phone components
C_COMP_CLOUD = '#D97706'  # amber for cloud components
C_BORDER     = '#94A3B8'
C_ARROW      = '#475569'
C_TEXT       = '#1E293B'
C_LABEL_BG   = '#FFFFFF'

# ── Zone backgrounds ──
phone_zone = FancyBboxPatch((0.15, 0.3), 4.0, 4.8, boxstyle="round,pad=0.15",
                             facecolor=C_PHONE_BG, edgecolor=C_BORDER, linewidth=1.2, zorder=0)
cloud_zone = FancyBboxPatch((4.85, 0.3), 4.0, 4.8, boxstyle="round,pad=0.15",
                             facecolor=C_CLOUD_BG, edgecolor=C_BORDER, linewidth=1.2, zorder=0)
ax.add_patch(phone_zone)
ax.add_patch(cloud_zone)

# Zone labels
ax.text(2.15, 5.35, 'Participant Smartphone\n被试智能手机', ha='center', va='top',
        fontsize=9.5, fontweight='bold', color='#1E40AF')
ax.text(6.85, 5.35, 'Cloud Infrastructure\n云端基础设施', ha='center', va='top',
        fontsize=9.5, fontweight='bold', color='#92400E')

# ── Phone components ──
comp_w, comp_h = 3.6, 0.65
phone_y = [4.2, 3.2, 2.2, 1.2]

phone_data = [
    ('Audio Player · 音频播放器', '(CDN-streamed · CDN 推送)'),
    ('Rating UI · 评分界面', '(arousal 1-5 + emotion label)'),
    ('DeviceMotion · 运动传感', '(accelerometer 60Hz · 加速度计采样)'),
    ('localStorage · 本地存储', '(offline fallback cache · 离线容错)'),
]

phone_boxes = []
for idx, (title, subtitle) in enumerate(phone_data):
    y = phone_y[idx]
    box = FancyBboxPatch((0.35, y), comp_w, comp_h, boxstyle="round,pad=0.08",
                          facecolor='white', edgecolor=C_COMP_PHONE, linewidth=1.2, zorder=2)
    ax.add_patch(box)
    phone_boxes.append((0.35, y, comp_w, comp_h))
    ax.text(0.35 + comp_w/2, y + comp_h/2 + 0.08, title, ha='center', va='center',
            fontsize=7.5, fontweight='bold', color=C_COMP_PHONE)
    ax.text(0.35 + comp_w/2, y + comp_h/2 - 0.18, subtitle, ha='center', va='center',
            fontsize=6.2, color='#64748B')

# Phone label
ax.text(0.35 + comp_w/2, 4.2 + comp_h + 0.15, 'Browser · 浏览器', ha='center', va='bottom',
        fontsize=7, fontweight='bold', color='#475569')

# ── Cloud components ──
cloud_data = [
    ('Serverless Function', '无服务器函数', 'HTTPS POST\nendpoint'),
    ('NoSQL Database', 'NoSQL 数据库', 'document store'),
    ('CDN', '内容分发网络', 'audio files · 音频文件'),
]

cloud_y_positions = [4.2, 2.9, 1.5]

for idx, (title_en, title_cn, desc) in enumerate(cloud_data):
    y = cloud_y_positions[idx]
    h = 1.0 if idx < 2 else 1.2
    box = FancyBboxPatch((5.05, y), 3.6, h, boxstyle="round,pad=0.08",
                          facecolor='white', edgecolor=C_COMP_CLOUD, linewidth=1.2, zorder=2)
    ax.add_patch(box)
    ax.text(5.05 + 3.6/2, y + h/2 + 0.15, f'{title_en} · {title_cn}', ha='center', va='center',
            fontsize=7.5, fontweight='bold', color=C_COMP_CLOUD)
    ax.text(5.05 + 3.6/2, y + h/2 - 0.18, desc, ha='center', va='center',
            fontsize=6.2, color='#64748B')

# ── CloudBase wrapper ──
cloudbase = FancyBboxPatch((4.95, 1.2), 3.8, 3.75, boxstyle="round,pad=0.12",
                            facecolor='none', edgecolor='#D97706', linewidth=1.5,
                            linestyle='--', zorder=1)
ax.add_patch(cloudbase)
ax.text(6.85, 1.05, 'Tencent CloudBase · 腾讯云', ha='center', va='top',
        fontsize=6.8, fontweight='bold', color='#B45309', style='italic')

# ── Arrows ──
# HTTPS POST: phone → cloud (from rating UI and localStorage to serverless function)
arrow_style = "simple, tail_width=0.6, head_width=2.5, head_length=3"
ax.annotate('', xy=(5.05, 4.55), xytext=(3.95 + comp_w, 3.55),
            arrowprops=dict(arrowstyle=arrow_style, color=C_ARROW, lw=1.5))
ax.text(4.5, 4.3, 'HTTPS POST', ha='center', va='center', fontsize=6.5,
        fontweight='bold', color=C_ARROW, rotation=0,
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

# Audio CDN → phone (from CDN to Audio Player)
ax.annotate('', xy=(2.15, 4.55), xytext=(4.95, 2.1),
            arrowprops=dict(arrowstyle=arrow_style, color='#059669', lw=1.5))
ax.text(3.55, 3.8, 'audio stream\n音频流', ha='center', va='center', fontsize=6.2,
        fontweight='bold', color='#059669',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

# localStorage → cloud fallback
ax.annotate('', xy=(5.05, 3.15), xytext=(2.15, 1.55),
            arrowprops=dict(arrowstyle=arrow_style, color='#7C3AED', lw=1.0, linestyle='dotted',
                           connectionstyle='arc3,rad=0.3'))
ax.text(3.55, 2.2, 'offline retry\n离线重传', ha='center', va='center', fontsize=6.2,
        color='#7C3AED',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none', alpha=0.85))

# ── Caption ──
caption = (
    'Figure X | FiveTone Explorer system architecture. '
    'The participant smartphone (left) streams audio from a CDN, collects self-report ratings, '
    'and passively samples accelerometer data at 60 Hz via the DeviceMotion API. '
    'Completed ratings are submitted via HTTPS POST to a Tencent CloudBase serverless function '
    'and stored in a NoSQL database. localStorage provides offline resilience: cached responses '
    'are automatically retried on the next successful connection. '
    'Audio files are hosted on the CDN for sub-second initial buffering on 4G mobile networks.'
)

fig.text(0.5, -0.02, caption, ha='center', va='top', fontsize=7.2,
         color='#555555', linespacing=1.3)

fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.06)

out_base = 'F:/Claude project/five_tone_experiment/fig_system'
fig.savefig(f'{out_base}.png', dpi=300)
fig.savefig(f'{out_base}.svg')
print(f'Figure saved: {out_base}.png / .svg')
