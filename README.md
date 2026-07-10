# FiveTone Explorer

**Zero-Install Mobile Sensing for Music Emotion Research in the Wild**

[![UbiComp 2026](https://img.shields.io/badge/UbiComp-2026-blue)](https://www.ubicomp.org/ubicomp2026/)
[![License](https://img.shields.io/badge/License-Academic%20Use%20Only-lightgrey)](#license)

> 🏆 Accepted at **UbiComp 2026 Teenager Show** (55/112, 49.1% acceptance rate)

FiveTone Explorer is a single-URL mobile web tool that turns any smartphone into a music-emotion research platform. It streams music, collects self-reported emotion ratings, and passively logs smartphone accelerometer data via the DeviceMotion API — all without app installation.

---

## 🔬 Research Findings

In a one-day WeChat deployment (N = 56), the tool collected **275 emotion observations** and **835,266 accelerometer samples** from 43 participants in naturalistic conditions:

1. **In-browser motion sensing carries behavioral signal** — directional associations between body movement and music-evoked arousal
2. **Classification crisis documented** — three-source cross-validation of pentatonic mode labels finds pairwise agreement ≤ 46%
3. **Acoustic features predict arousal** — zero-crossing rate, spectral centroid, and bandwidth correlate with self-reported arousal at effect sizes consistent with lab studies
4. **Cross-cultural extensibility** — same URL-based deployment extended to Western classical music with zero code changes

---

## 📂 Repository Contents

| Directory/File | Description |
|---|---|
| `index.html` | Main experiment web application |
| `index_light.html` | Lightweight variant |
| `acoustic_emotion_analysis.py` | Acoustic feature extraction + emotion correlation (librosa) |
| `bottom_up_analysis.py` | Data-driven clustering of emotion responses |
| `mode_detect.py` | Algorithmic pentatonic mode detection (MIR) |
| `detailed_analysis.py` | Multiple regression + PCA + age-group analysis |
| `latest_data.json` | Anonymized participant response data (N = 56) |
| `age_data.json` | Participant demographics |
| `functions/submitData/` | CloudBase serverless function |
| `china_west_comparison/` | Cross-cultural extension (Chinese vs. Western stimuli) |

**Note:** Audio stimulus files (~38 MB) are hosted on CDN and not included in this repository.

---

## 🚀 Quick Start

1. Open `index.html` in a browser, or serve locally:
```bash
python -m http.server 8080
# Visit http://localhost:8080
```

2. The live deployment is accessible at:
```
https://five-tone-cathykang-d4b0676685c9-1409437628.tcloudbaseapp.com
```

---

## 📄 Citation

If you use this work in your research, please cite:

```bibtex
@inproceedings{kang2026fivetone,
  title     = {FiveTone Explorer: Zero-Install Mobile Sensing for Music Emotion Research in the Wild},
  author    = {Kang, Yanan},
  booktitle = {Companion Proceedings of the 2026 ACM International Joint Conference
               on Pervasive and Ubiquitous Computing (UbiComp '26 Companion)},
  year      = {2026},
  publisher = {ACM},
  address   = {New York, NY, USA},
  doi       = {to be assigned}
}
```

---

## ⚖️ License

**This project is for academic research purposes only.** All rights reserved. The code, data, and analysis scripts in this repository are provided to support reproducibility of the accompanying UbiComp 2026 publication. Redistribution or commercial use requires explicit permission from the author.

---

## 👤 Author

**Kang Yanan** — Zhoupu High School Affiliated to East China Normal University, Shanghai, China

- GitHub: [@kang-yanan](https://github.com/kang-yanan)
- ORCID: [0000-0003-1875-4807](https://orcid.org/0000-0003-1875-4807) (Advisor: Juanjuan Jiang)

---

## 📧 Contact

For questions about the paper, code, or data, please open a GitHub issue or contact the author.
