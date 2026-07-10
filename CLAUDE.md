# FlipFocus — UbiComp/ISWC 2026 Teenager Show Submission

## Paper Info
- **Title**: FlipFocus: A Browser-Based Multi-Sensor Fusion Tool for Phone Flip Detection and Analysis
- **First Author**: Dengcheng Wang, Shanghai Sanlin High School
- **Status**: ✅ Compiled, ready for submission
- **Final PDF**: `D:\HuaweiMoveData\Users\shirl\Desktop\flipfocus-latex\FlipFocus.pdf` (4 pages, ~596 KB)
- **LaTeX source**: `D:\HuaweiMoveData\Users\shirl\Desktop\flipfocus-latex\FlipFocus.tex`

## Project Source Files
| What | Path |
|------|------|
| LaTeX project | `D:\HuaweiMoveData\Users\shirl\Desktop\flipfocus-latex\` |
| Original DOCX | `D:\HuaweiMoveData\Users\shirl\Desktop\FlipFocus A Browser-Based... .docx` |
| Analysis scripts | `F:\Claude project\ubicomp_teenager\analysis\` |
| Paper figures (vec) | `F:\Claude project\ubicomp_teenager\paper\figures\` |
| Results figures | `F:\Claude project\ubicomp_teenager\results\figures\` |
| BibTeX | `D:\HuaweiMoveData\Users\shirl\Desktop\flipfocus-latex\references.bib` |

## Figures
| Fig | LaTeX label | Source script | PDF file |
|-----|------------|---------------|----------|
| 1: Sensor timeseries | `fig:sensor` | `analysis/fig4_sensor_nature.py` | `figures/fig4_sensor_timeseries.pdf` |
| 2: Boxplot | `fig:boxplot` | `analysis/fig1_nature_boxplot.py` | `figures/fig1_boxplot.pdf` |
| 3: Individual trajectories | `fig:individual` | `analysis/fig2_individual_nature.py` | `figures/fig2_individual.pdf` |
| 4: Validation scatter | `fig:validation` | `analysis/fig3_validation_nature.py` | `figures/fig3_validation.pdf` |

## Tables
| Tab | Label | Content |
|-----|-------|---------|
| 1 | `tab:fusion` | 3-tier fusion modes (Full/Dual/Accel-only) |
| 2 | `tab:accuracy` | Detection accuracy (Accel+Light vs Accel-only) |
| 3 | `tab:compat` | Cross-device compatibility (3 phones) |
| 4 | `tab:sessions` | Session metadata (4 participants) |

## Key References (citation order)
1. Ward et al. 2017 — Brain Drain (JACR)
2. Stothart et al. 2015 — Attentional Cost (JEP:HPP)
3. Duckworth et al. 2011 — Self-Regulation (Ed Psych)
4. Kubiak & Smyth 2015 — PIEL Survey (JMIR)
5. Kuijpers et al. 2022 — Browser Sensors (MobileHCI)
6. Wac et al. 2016 — Mobile Experience (W-MUST)

---

## LaTeX / ACM Formatting — Lessons Learned

### Critical Rules
1. **Document class**: `\documentclass[sigconf]{acmart}`
2. **Conference metadata** (MUST set):
   ```latex
   \acmConference[UbiComp/ISWC '26]{...Full Name...}{October 11--15, 2026}{Shanghai, China}
   \acmYear{2026}
   ```
3. **Affiliation** MUST include city + country:
   ```latex
   \affiliation{%
     \institution{School Name}
     \city{Shanghai}
     \country{China}
   }
   ```
4. **CCS Concepts required**: fill via `\begin{CCSXML}...\end{CCSXML}` + `\ccsdesc`
5. **Bibliography**: USE `\bibliographystyle{unsrt}` for citation-order numbering. `ACM-Reference-Format` sorts ALPHABETICALLY → WRONG for this venue
6. **Fonts**: add `\usepackage{newtxtext}\usepackage{newtxmath}` for uniform Times. Replace `\texttt{}` with `\textit{}` (monospace font doesn't match body text)
7. **Tables in 2-column**: use `\resizebox{\columnwidth}{!}{tabular}` for single-column tables, `table*` for wide ones
8. **Figures**: add `\Description{...}` before `\label{}` for ACM accessibility compliance
9. **Floats**: use `[htbp]` placement (not just `[ht]` or `[tb]`)
10. **Long filenames**: use `\nolinkurl{}` for automatic line breaking

### DOCX → LaTeX Checklist
- Replace full-width Unicode: `：`(U+FF1A)→`:`, `（）`(U+FF08/FF09)→`()`
- Remove template placeholders: Title Note, Author Note, Woodstock'18, dummy ISBN/DOI
- Fix © year from 2018 → 2026
- Ensure all figs/tables are `\ref{}`-ed in body text
- Check citation order: Intro [1]→[N] ascending

### Compilation
```bash
cd flipfocus-latex
rm -f *.aux *.bbl *.blg *.out *.log
pdflatex FlipFocus.tex
bibtex FlipFocus
pdflatex FlipFocus.tex
pdflatex FlipFocus.tex
```

---

## Submission
- **Venue**: UbiComp/ISWC 2026 Teenager Show
- **Website**: https://ubicomp26-teen.top/
- **PCS**: https://new.precisionconference.com/submissions → SIGCHI → UbiComp/ISWC2026 → Teenager Show
- **Contact**: teenager-2026@ubicomp.org
- **Deadline**: June 14, 2026 AoE = **Beijing June 15, 19:59**
- **Notification**: July 4, 2026
- **Camera-ready**: July 23, 2026
- **Format**: PDF, 2-4 pages (excl. refs), English
- **Eligibility**: First author = middle/high school student
- **PCS note**: Requires Google reCAPTCHA (may need VPN in mainland China)
- **Video**: Optional, 2-4 min, encouraged

## Memory References
- `[[ubicomp-teen-show-submission]]` — full submission checklist
- `[[five-tone-aesthetic-analogy]]` — next paper (separate context window)
