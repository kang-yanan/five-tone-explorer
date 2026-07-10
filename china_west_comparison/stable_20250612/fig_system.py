"""System architecture — Morandi palette."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from plot_utils import MORANDI, setup_style, caption

setup_style()
fig, ax = plt.subplots(figsize=(8.8, 5.2))
ax.set_xlim(0,8.8); ax.set_ylim(0,5.2); ax.axis('off')

# Morandi tones
PZ=MORANDI['light_warm']; CZ='#EEEAE4'; PB='#D5CBC4'; CB='#D9CFC6'
PT='#4A4540'; CT='#5C4F48'; AG=MORANDI['sage_green']; AD='#6B5E55'; AO=MORANDI['dusty_lavender']

# Zone backgrounds
p=FancyBboxPatch((0.30,0.35),3.60,4.55,boxstyle="round,pad=0.12",facecolor=PZ,edgecolor=MORANDI['divider'],lw=0.6,zorder=0)
c=FancyBboxPatch((4.90,0.35),3.60,4.55,boxstyle="round,pad=0.12",facecolor=CZ,edgecolor=MORANDI['divider'],lw=0.6,zorder=0)
ax.add_patch(p); ax.add_patch(c)
ax.text(2.10,5.10,'Participant Smartphone  ·  Browser',ha='center',va='bottom',fontsize=9.5,fontweight='bold',color=PT)
ax.text(6.70,5.10,'Cloud Infrastructure  ·  Tencent CloudBase',ha='center',va='bottom',fontsize=9.5,fontweight='bold',color=CT)

# Phone modules
pw,ph=3.20,0.80; px=0.50; py=[4.28,3.18,2.08,0.98]
pm=[('Audio Player','CDN-streamed audio playback'),('Rating UI','arousal 1–5 + emotion label forced choice'),
    ('DeviceMotion','60 Hz accelerometer sampling via API'),('localStorage','offline fallback cache')]
for i,(t,s) in enumerate(pm):
    b=FancyBboxPatch((px,py[i]),pw,ph,boxstyle="round,pad=0.06",facecolor=PB,edgecolor='white',lw=1.2,zorder=2)
    ax.add_patch(b)
    ax.text(px+pw/2,py[i]+ph/2+0.10,t,ha='center',va='center',fontsize=8.5,fontweight='bold',color='#3D3833')
    ax.text(px+pw/2,py[i]+ph/2-0.20,s,ha='center',va='center',fontsize=7.2,color='#6B5E55')

# Cloud modules
cw,ch=3.20,0.95; cx=5.10; cy=[4.15,2.80,1.35]
cm=[('Serverless Function','HTTPS POST endpoint'),('NoSQL Database','document store for user data'),('CDN','hosts audio files')]
for i,(t,s) in enumerate(cm):
    b=FancyBboxPatch((cx,cy[i]),cw,ch,boxstyle="round,pad=0.06",facecolor=CB,edgecolor='white',lw=1.2,zorder=2)
    ax.add_patch(b)
    ax.text(cx+cw/2,cy[i]+ch/2+0.12,t,ha='center',va='center',fontsize=8.5,fontweight='bold',color='#4A3E35')
    ax.text(cx+cw/2,cy[i]+ch/2-0.22,s,ha='center',va='center',fontsize=7.2,color='#7A6A5F')

# Arrows
ast="simple,tail_width=0.5,head_width=2.2,head_length=2.5"
bb=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor='none',alpha=0.92)
ax.annotate('',xy=(px+pw/2,py[0]+ph/2),xytext=(cx+cw/2,cy[2]+ch),
            arrowprops=dict(arrowstyle=ast,color=AG,lw=2,connectionstyle='arc3,rad=0.25'))
ax.text(2.7,3.65,'audio stream',ha='center',va='center',fontsize=7.5,fontweight='bold',color=AG,bbox=bb)
ax.annotate('',xy=(cx+cw/2,cy[0]+ch/2),xytext=(px+pw,py[1]+ph/2),
            arrowprops=dict(arrowstyle=ast,color=AD,lw=1.5))
ax.annotate('',xy=(cx+cw/2,cy[1]+ch/2),xytext=(cx+cw/2,cy[0]),
            arrowprops=dict(arrowstyle=ast,color=AD,lw=1.5))
ax.text(4.40,3.88,'HTTPS POST\nratings & sensor data',ha='center',va='center',fontsize=7.5,fontweight='bold',color=AD,bbox=bb)
ax.annotate('',xy=(cx+cw/2,cy[1]),xytext=(px+pw,py[3]+ph/2),
            arrowprops=dict(arrowstyle=ast,color=AO,lw=1.2,linestyle='dotted',connectionstyle='arc3,rad=0.35'))
ax.text(4.40,0.95,'offline retry\ncached data upload',ha='center',va='center',fontsize=7.5,fontweight='bold',color=AO,bbox=bb)

caption('Figure 1 | FiveTone Explorer system architecture.', fig)
fig.subplots_adjust(left=0.01,right=0.99,top=0.96,bottom=0.04)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_system.png',dpi=300)
fig.savefig('F:/Claude project/five_tone_experiment/china_west_comparison/fig_system.svg')
print('fig_system saved — Morandi.')
