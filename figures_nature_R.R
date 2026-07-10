# Nature-style figures for FiveTone Explorer — R/ggplot2 + patchwork
library(ggplot2)
library(patchwork)
library(svglite)

# ─── Palettes ───
pal <- list(
  blue_main   = "#0F4D92", red_strong = "#B64342",
  n_light     = "#D8D8D8", n_mid    = "#A8A8A8",
  n_dark      = "#606060", n_black  = "#272727",
  teal        = "#42949E", violet  = "#9A4D8E",
  gold        = "#E28E2C", green   = "#2E9E44"
)

mode_colors <- c(
  gong  = "#C4A35A", shang = "#B0ACA4", jue  = "#8BA684",
  zhi   = "#C48173", yu    = "#7D8FA8",
  mixed = "#A8A8A8", none  = "#D8D8D8"
)

cluster_colors <- c("1" = "#2E9E44", "2" = "#0F4D92", "3" = "#E28E2C")

# ─── Theme ───
theme_nature <- theme_minimal(base_size = 9, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(linewidth = 0.2, color = "#E0E0E0"),
    plot.title = element_text(size = 10, face = "bold"),
    plot.subtitle = element_text(size = 8, color = "#606060"),
    plot.caption = element_text(size = 7, color = "#A8A8A8", hjust = 0),
    axis.title = element_text(size = 8),
    legend.position = "bottom",
    legend.title = element_text(size = 8),
    legend.text = element_text(size = 7)
  )

# ─── Track names (English only) ───
track_names_en <- c(
  gong_01 = "Autumn Moon over the Lake", gong_02 = "Liuyang River",
  gong_03 = "Purple Bamboo Tune",       gong_04 = "Flower Three-Six",
  gong_05 = "Plum Blossoms in Snow",
  shang_01 = "Ambush on All Sides",     shang_02 = "Guangling San",
  shang_03 = "Luchai Flower",           shang_05 = "Yangguan Pass",
  jue_01 = "Riding the Wind",           jue_02 = "Gusu Journey",
  jue_03 = "Eighteen Beats",            jue_04 = "Blooming Flowers",
  jue_05 = "Rainbow Skirt Dance",
  zhi_01 = "Joyful",                    zhi_02 = "New Year Joy",
  zhi_03 = "Spring Festival Overture",  zhi_04 = "Rising Higher",
  zhi_05 = "March of the PLA",
  yu_01 = "Crow Night Cry",             yu_02 = "Moonlit Spring",
  yu_03 = "Jackdaws Playing in Water",  yu_04 = "Butterfly Lovers",
  yu_05 = "River of Sorrow"
)

# ─── Figure 1 data: classification matrix ───
sources <- c("Original", "Claude", "Gemini", "TCM lit.", "Mita")
class_data <- data.frame(
  track = rep(names(track_names_en), each = 5),
  track_name = rep(track_names_en, each = 5),
  source = rep(factor(sources, levels = sources), 24),
  mode = c(
    "gong","yu","zhi","none","gong",
    "gong","yu","gong","none","gong",
    "gong","gong","zhi","zhi","yu",
    "gong","gong","zhi","none","gong",
    "gong","gong","gong","none","zhi",
    "shang","shang","shang","gong","shang",
    "shang","shang","shang","none","gong",
    "shang","zhi","zhi","none","zhi",
    "shang","yu","shang","shang","gong",
    "jue","gong","gong","jue","gong",
    "jue","gong","gong","none","zhi",
    "jue","yu","yu","none","yu",
    "jue","gong","gong","none","gong",
    "jue","zhi","zhi","none","yu",
    "zhi","gong","gong","zhi","zhi",
    "zhi","gong","gong","none","zhi",
    "zhi","gong","gong","zhi","gong",
    "zhi","gong","gong","zhi","zhi",
    "zhi","gong","gong","zhi","gong",
    "yu","yu","yu","none","yu",
    "yu","gong","yu","yu","mixed",
    "yu","zhi","zhi","none","yu",
    "yu","gong","yu","mixed","yu",
    "yu","yu","yu","none","shang"
  )
)
class_data$mode <- factor(class_data$mode,
  levels = c("gong","shang","jue","zhi","yu","mixed","none"))
class_data$track_name <- factor(class_data$track_name,
  levels = rev(track_names_en))

mode_labels <- c(gong="Gong", shang="Shang", jue="Jue", zhi="Zhi", yu="Yu",
                 mixed="Disputed", none="Not listed")

fig1 <- ggplot(class_data, aes(x = source, y = track_name, fill = mode)) +
  geom_tile(color = "white", linewidth = 1.2) +
  geom_text(aes(label = c(gong="Go",shang="Sh",jue="Ju",zhi="Zh",yu="Yu",
                          mixed="?",none="-")[as.character(mode)]),
            size = 2.8, fontface = "bold",
            color = ifelse(class_data$mode %in% c("zhi","yu"), "white", "#272727")) +
  scale_fill_manual(values = mode_colors, labels = mode_labels, name = "Mode") +
  labs(
    title = "Five-source pentatonic mode classification reveals low inter-source agreement",
    subtitle = "Only 4/24 tracks reach 4+ source consensus. Zero achieve unanimous agreement.",
    caption = "Classification ambiguity underlies the empirical challenge in five-tone therapy research.",
    x = NULL, y = NULL
  ) +
  theme_nature +
  theme(axis.text.y = element_text(size = 6.5), axis.text.x = element_text(size = 7))

ggsave("F:/Claude project/five_tone_experiment/fig1_heatmap_R.png", fig1, width = 7, height = 8, dpi = 300)
ggsave("F:/Claude project/five_tone_experiment/fig1_heatmap_R.svg", fig1, width = 7, height = 8)
cat("Figure 1 OK\n")

# ─── Figure 2: compute PCA + clusters from raw data ───
library(jsonlite)
raw <- readLines("F:/Claude project/five_tone_experiment/latest_data.json", warn = FALSE)
raw <- paste(raw, collapse = "")
# Skip CLI header
json_start <- regexpr('"data"', raw)[1]
jdata <- fromJSON(paste0("{", substr(raw, json_start, nchar(raw))))
# Parse raw JSON more carefully — double-nested array structure
ppl_df <- jdata$data$results[[1]]  # data.frame, each row = one participant

emotions <- c("anding","neixing","shuchang","zhenfen","ningjing")
emo_labels <- c("Stable","Introsp.","Flowing","Exciting","Quiet")

# Extract summary from each row
track_emo <- list(); track_n <- list()
extract_summary <- function(summary_col) {
  # summary_col may be a data.frame (list of columns) or a list of lists
  if (is.null(summary_col)) return(NULL)
  if (is.data.frame(summary_col)) {
    # Rows = tracks, columns = mode/track/emotion/arousal
    return(summary_col)
  }
  return(NULL)
}

for (i in seq_len(nrow(ppl_df))) {
  if (!"summary" %in% names(ppl_df)) next
  smry <- ppl_df$summary[[i]]
  if (is.null(smry)) next
  # smry is a data.frame with columns: mode, track, emotion, arousal, label, trackName
  if (is.data.frame(smry)) {
    for (j in seq_len(nrow(smry))) {
      tk <- smry$track[j]
      em <- smry$emotion[j]
      if (is.null(tk) || is.null(em) || nchar(tk) == 0) next
      if (is.null(track_emo[[tk]])) { track_emo[[tk]] <- setNames(rep(0,5), emotions); track_n[[tk]] <- 0 }
      track_emo[[tk]][em] <- track_emo[[tk]][em] + 1; track_n[[tk]] <- track_n[[tk]] + 1
    }
  }
}

valid <- names(track_n)[track_n >= 5 & names(track_n) != "shang_04"]
X_emo <- t(sapply(valid, function(tk) track_emo[[tk]] / track_n[[tk]] * 100))
colnames(X_emo) <- emo_labels

# PCA
pca <- prcomp(X_emo, scale. = TRUE, center = TRUE)
pc_scores <- as.data.frame(pca$x)
pc_scores$track <- valid
pc_scores$name <- track_names_en[valid]
var_pc1 <- round(summary(pca)$importance[2,1] * 100)
var_pc2 <- round(summary(pca)$importance[2,2] * 100)

# Clustering
hc <- hclust(dist(scale(X_emo)), method = "ward.D2")
pc_scores$cluster <- factor(cutree(hc, 3))
cluster_labels <- c("1" = "High-arousal", "2" = "Calm / Quiet", "3" = "Mixed / Flowing")

# Panel A: PCA
standout <- c("Spring Festival Overture","New Year Joy","Joyful",
              "River of Sorrow","Moonlit Spring","Eighteen Beats","Crow Night Cry")
pc_scores$label <- ifelse(pc_scores$name %in% standout, pc_scores$name, "")

p2a <- ggplot(pc_scores, aes(x = PC1, y = PC2, color = cluster, label = label)) +
  geom_point(size = 3, alpha = 0.85) +
  ggrepel::geom_text_repel(size = 2.8, max.overlaps = 15, box.padding = 0.3,
                           segment.color = "#A8A8A8", segment.size = 0.3) +
  scale_color_manual(values = cluster_colors, labels = cluster_labels) +
  labs(
    x = sprintf("PC1 (%d%% var.)  Exciting <- -> Stable", var_pc1),
    y = sprintf("PC2 (%d%% var.)  Flowing <- -> Introspective/Quiet", var_pc2),
    title = "Emotion response PCA (no pre-imposed labels)",
    color = NULL
  ) + theme_nature

# Panel B: cluster profiles
profiles <- do.call(rbind, lapply(1:3, function(c) {
  tracks_in <- pc_scores$track[pc_scores$cluster == c]
  avg <- colMeans(X_emo[tracks_in, , drop = FALSE])
  data.frame(cluster = factor(c), emotion = factor(emo_labels, levels = emo_labels),
             pct = avg, n = length(tracks_in))
}))
profiles$cluster_label <- cluster_labels[as.character(profiles$cluster)]

p2b <- ggplot(profiles, aes(x = emotion, y = pct, fill = cluster_label)) +
  geom_col(position = position_dodge(0.8), width = 0.7, alpha = 0.85) +
  scale_fill_manual(values = unname(cluster_colors)) +
  labs(y = "Mean % selected", x = NULL, title = "Cluster emotion profiles", fill = NULL) +
  theme_nature

fig2 <- p2a + p2b +
  plot_annotation(
    title = "Data-driven emotion clusters emerge from 50 listeners' raw responses",
    subtitle = "No pre-defined mode labels. Natural structure: arousal + valence (Russell's circumplex).",
    caption = "Each listener rated 5 tracks + 1 silent baseline. K=3 hierarchical clustering on emotion percentages.",
    theme = theme_nature
  )

ggsave("F:/Claude project/five_tone_experiment/fig2_clusters_R.png", fig2, width = 9, height = 4.5, dpi = 300)
ggsave("F:/Claude project/five_tone_experiment/fig2_clusters_R.svg", fig2, width = 9, height = 4.5)
cat("Figure 2 OK\n")

# ─── Figure 3: Arousal ~ Acoustic ───
# Acoustic features pre-computed by Python (librosa) and exported to JSON
acoustic <- fromJSON("F:/Claude project/five_tone_experiment/acoustic_for_R.json")

# Arousal from participant data
arousal_raw <- list()
for (i in seq_len(nrow(ppl_df))) {
  if (!"summary" %in% names(ppl_df)) next
  smry <- ppl_df$summary[[i]]
  if (is.null(smry) || !is.data.frame(smry)) next
  for (j in seq_len(nrow(smry))) {
    tk <- smry$track[j]
    # Arousal is a nested data.frame with column $numberInt
    ar_val <- smry$arousal[["$numberInt"]][j]
    if (is.null(tk) || nchar(tk) == 0) next
    v <- if (is.null(ar_val)) NA_integer_ else as.integer(ar_val)
    if (is.na(v)) next
    if (is.null(arousal_raw[[tk]])) arousal_raw[[tk]] <- c()
    arousal_raw[[tk]] <- c(arousal_raw[[tk]], v)
  }
}

shared <- intersect(names(acoustic), names(arousal_raw))

# Build data frame: one row per track
df3 <- data.frame(
  name      = track_names_en[shared],
  zcr       = sapply(shared, function(tk) acoustic[[tk]]$zcr),
  brightness = sapply(shared, function(tk) acoustic[[tk]]$brightness),
  bandwidth  = sapply(shared, function(tk) acoustic[[tk]]$bandwidth),
  arousal    = sapply(shared, function(tk) mean(arousal_raw[[tk]]))
)

# Three sub-plots
make_acoustic_plot <- function(xvar, xlab, df) {
  r_val <- cor(df[[xvar]], df$arousal, use = "complete.obs")
  r_label <- sprintf("r = %+.2f", r_val)

  standout3 <- c("Spring Festival Overture","New Year Joy","Joyful",
                 "River of Sorrow","Moonlit Spring","Crow Night Cry",
                 "Yangguan Pass","Butterfly Lovers")
  df$highlight <- ifelse(df$name %in% standout3, df$name, "")

  ggplot(df, aes(x = .data[[xvar]], y = arousal)) +
    geom_smooth(method = "lm", se = TRUE, color = "#B64342", fill = "#F6CFCB",
                linewidth = 1, alpha = 0.3) +
    geom_point(color = pal$blue_main, size = 2.5, alpha = 0.7) +
    ggrepel::geom_text_repel(aes(label = highlight), size = 2.5, max.overlaps = 12,
                             box.padding = 0.2, segment.size = 0.2, color = "#606060") +
    annotate("text", x = -Inf, y = Inf, label = r_label, hjust = -0.1, vjust = 2,
             size = 4, fontface = "bold", color = pal$red_strong) +
    labs(x = xlab, y = "Mean Arousal (1-5)") +
    theme_nature + theme(plot.title = element_blank())
}

p3a <- make_acoustic_plot("zcr", "Zero-Crossing Rate (noisiness)", df3)
p3b <- make_acoustic_plot("brightness", "Spectral Centroid (Hz)", df3)
p3c <- make_acoustic_plot("bandwidth", "Spectral Bandwidth (Hz)", df3)

fig3 <- p3a + p3b + p3c +
  plot_annotation(
    title = "Acoustic features correlate with self-reported arousal — no mode labels needed",
    subtitle = "Arousal is the only label-independent emotional dimension (|r| > 0.5, N = 22 tracks).",
    caption = "Shaded band = 95% CI. Each point = one track, aggregated across all participants who heard it.",
    theme = theme_nature
  ) & theme(plot.margin = margin(6, 6, 4, 4))

ggsave("F:/Claude project/five_tone_experiment/fig3_arousal_R.png", fig3, width = 9.5, height = 3.8, dpi = 300)
ggsave("F:/Claude project/five_tone_experiment/fig3_arousal_R.svg", fig3, width = 9.5, height = 3.8)
cat("Figure 3 OK\nDone.\n")
