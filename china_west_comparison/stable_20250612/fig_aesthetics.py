"""Aesthetic figures — Morandi palette with proper spacing."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt; import numpy as np; import librosa,librosa.display,json,os
from plot_utils import MORANDI,setup_style,caption,panel_label,CLUSTER_COLORS

setup_style()
BASE=os.path.dirname(os.path.abspath(__file__))
AUDIO=os.path.join(BASE,'audio'); OUT=BASE; SR=22050

with open(os.path.join(BASE,'..','acoustic_emotion_results.json'),'r',encoding='utf-8')as f:emo=json.load(f)
tracks=emo['track_summary']

# ── A: Spectrograms + Emotion Overlay ──
rep=[('zhi_01','Joyful','High Arousal'),('yu_05','River of Sorrow','Calm/Quiet'),('jue_02','Gusu Journey','Mixed/Flowing')]
emo_labels=['Stable','Introspective','Flowing','Exciting','Quiet']
emo_colors=[MORANDI['muted_blue'],MORANDI['dusty_lavender'],MORANDI['sage_green'],MORANDI['dusty_rose'],MORANDI['muted_blue']]

fig_a,axes=plt.subplots(2,3,figsize=(11,5.5),gridspec_kw={'height_ratios':[3,1]})
for ai,(tk,name,lb)in enumerate(rep):
    # Top: spectrogram
    ax_top=axes[0,ai]; fp=os.path.join(AUDIO,tk+'.mp3')
    y,sr=librosa.load(fp,sr=SR)
    S=librosa.feature.melspectrogram(y=y,sr=sr,n_mels=128)
    S_db=librosa.power_to_db(S,ref=np.max)
    cmaps=['magma','coolwarm','viridis']; librosa.display.specshow(S_db,sr=sr,x_axis='time',y_axis='mel',ax=ax_top,cmap=cmaps[ai])
    ax_top.set_title(f'{name}',fontsize=10,pad=8,fontweight='bold')

    # Bottom: emotion distribution bar
    ax_bot=axes[1,ai]
    tk_data=[t for t in tracks if t['track']==tk]
    if tk_data:
        t=tk_data[0]; vals=[t.get('anding',0),t.get('neixing',0),t.get('shuchang',0),t.get('zhenfen',0),t.get('ningjing',0)]
        bar_colors=[MORANDI['muted_blue'],MORANDI['dusty_lavender'],MORANDI['sage_green'],MORANDI['dusty_rose'],MORANDI['faded_teal']]
        bars=ax_bot.bar(range(5),vals,color=bar_colors,alpha=0.85,edgecolor='white',lw=0.5)
        ax_bot.set_xticks(range(5)); ax_bot.set_xticklabels(emo_labels,fontsize=7.5,rotation=30)
        ax_bot.set_ylabel('%',fontsize=8); ax_bot.set_ylim(0,100)
        dom_idx=np.argmax(vals); dom_pct=vals[dom_idx]
        ax_bot.set_title(f'{emo_labels[dom_idx]}: {dom_pct:.0f}%',fontsize=9,color=MORANDI['dusty_rose'],fontweight='bold')

panel_label(axes[0,0],'a')
caption('Figure 7 | Acoustic fingerprints and their emotional signatures. Top: mel-spectrograms show frequency energy over time. Bottom: emotion distribution from 50 listeners — the visual pattern (bright vs. dark, dense vs. sparse) predicts the dominant felt emotion.',fig_a)
fig_a.subplots_adjust(left=0.05,right=0.98,top=0.92,bottom=0.10,wspace=0.28,hspace=0.35)
fig_a.savefig(os.path.join(OUT,'fig_spectrograms.png')); fig_a.savefig(os.path.join(OUT,'fig_spectrograms.svg'))
print('A: spectrograms+emotion — Morandi.')

# ── B: Correlation Matrix ──
fl=['Tempo','Spectral Centroid','RMS Energy','Zero-Crossing Rate','Onset Rate','Spectral Bandwidth','Harmonic Ratio']
el=['Stable','Introspective','Flowing','Exciting','Quiet']
corrs=np.zeros((7,5))
fm={'速度 BPM':0,'频谱质心 (亮度)':1,'响度 RMS':2,'过零率 (噪音感)':3,'音符密度':4,'频谱宽度':5,'和谐比':6}
em={'安定':0,'内省':1,'舒畅':2,'振奋':3,'宁静':4}
for c in emo['correlations']:
    fi=fm.get(c['feature'],-1); ei=em.get(c['emotion'],-1)
    if fi>=0 and ei>=0: corrs[fi,ei]=c['r']
fig_b,ax_b=plt.subplots(figsize=(6,5.5))
im=ax_b.imshow(corrs,cmap='RdBu_r',vmin=-0.6,vmax=0.6,aspect='auto')
ax_b.set_xticks(range(5)); ax_b.set_xticklabels(el,fontsize=9)
ax_b.set_yticks(range(7)); ax_b.set_yticklabels(fl,fontsize=9)
for i in range(7):
    for j in range(5):
        ax_b.text(j,i,f'{corrs[i,j]:+.2f}',ha='center',va='center',fontsize=7.8,fontweight='bold',
                  color='white'if abs(corrs[i,j])>0.35 else MORANDI['charcoal'])
cbar=fig_b.colorbar(im,ax=ax_b,shrink=0.82); cbar.set_label('Pearson r',fontsize=8.5)
ax_b.set_title('Acoustic-E* × Emotion Correlation Matrix',fontsize=10.5,pad=14)
panel_label(ax_b,'b')
caption('Figure 8 | Zero-crossing rate and spectral bandwidth positively correlate with Exciting (r > 0.5); harmonic ratio negatively correlates — noisier, wider-bandwidth music is perceived as more exciting across both traditions.',fig_b)
fig_b.subplots_adjust(left=0.20,right=0.94,top=0.88,bottom=0.12)
fig_b.savefig(os.path.join(OUT,'fig_corr_matrix.png')); fig_b.savefig(os.path.join(OUT,'fig_corr_matrix.svg'))
print('B: correlation matrix — Morandi.')

# ── C: Emotion-Vector PCA ──
d=np.load(os.path.join(BASE,'..','cluster_data.npz'),allow_pickle=True)
PC=d['PC']; cs=d['clusters']; valid=d['valid']; S0,S1,St=float(d['S0']),float(d['S1']),float(d['Stot'])
ta={t['track']:t.get('zhenfen',0)for t in tracks if t['track']in valid}
fig_c,ax_c=plt.subplots(figsize=(7.5,6.5))
for cl in[1,2,3]:
    m=cs==cl; sz=[ta.get(v,20)*9+35 for v in np.array(valid)[m]]
    ax_c.scatter(PC[m,0],PC[m,1],c=CLUSTER_COLORS[cl],s=sz,alpha=0.82,edgecolors='white',lw=0.5,zorder=3,
                label={1:'High-arousal',2:'Calm/Quiet',3:'Mixed/Flowing'}[cl])
for lb,dx,dy in[('Exciting',1.5,0.5),('Stable',-1.5,-0.5),('Flowing',0.5,1.0),('Quiet',-1.0,-1.0)]:
    ax_c.annotate(lb,xy=(dx*0.8,dy*0.8),xytext=(dx*1.3,dy*1.3),fontsize=9,fontweight='bold',color=MORANDI['charcoal'],
                  arrowprops=dict(arrowstyle='->',lw=1.8,color=MORANDI['warm_dark']))
ax_c.set_xlabel(f'PC1 ({S0**2/St*100:.0f}% var.)  —  Arousal',fontsize=9.5)
ax_c.set_ylabel(f'PC2 ({S1**2/St*100:.0f}% var.)  —  Valence',fontsize=9.5)
ax_c.legend(fontsize=8,loc='upper right',frameon=False)
ax_c.set_title('Emotion Space: Acoustic PCA with Arousal Scaling',fontsize=10.5,pad=12)
panel_label(ax_c,'c')
caption('Figure 9 | Chinese and Western music overlap in acoustic space. Arousal increases along PC1; larger points (higher arousal) cluster upper-right regardless of cultural origin.',fig_c)
fig_c.subplots_adjust(left=0.12,right=0.94,top=0.90,bottom=0.12)
fig_c.savefig(os.path.join(OUT,'fig_emotion_pca.png')); fig_c.savefig(os.path.join(OUT,'fig_emotion_pca.svg'))
print('C: emotion PCA — Morandi.')
print('All done.')
