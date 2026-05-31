import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon="🌫",
    layout="wide",
)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "main_data.csv")
    df = pd.read_csv(path)
    return df

df = load_data()

SEASON_ORDER  = ["Winter", "Spring", "Summer", "Autumn"]
SEASON_COLORS = {"Winter": "#2c3e50", "Spring": "#27ae60",
                 "Summer": "#e74c3c", "Autumn": "#e67e22"}

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("Filter Data")

all_stations = sorted(df["station"].unique())
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun", all_stations, default=all_stations
)

year_min, year_max = int(df["year"].min()), int(df["year"].max())
selected_years = st.sidebar.slider(
    "Rentang Tahun", year_min, year_max, (year_min, year_max)
)

selected_seasons = st.sidebar.multiselect(
    "Pilih Musim", SEASON_ORDER, default=SEASON_ORDER
)

# ── Filter ───────────────────────────────────────────────────────────────────
mask = (
    df["station"].isin(selected_stations) &
    df["year"].between(selected_years[0], selected_years[1]) &
    df["season"].isin(selected_seasons)
)
dff = df[mask].copy()

if dff.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Beijing Air Quality Dashboard")
st.markdown(
    "Analisis konsentrasi PM2.5 dan faktor meteorologi dari **12 stasiun pemantauan** "
    "di Beijing, periode **2013-2017**. Dataset: PRSA Multi-Site Air Quality Data."
)
st.markdown("---")

# ── KPI Metrics ──────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Rata-rata PM2.5 (ug/m3)",  f"{dff['PM2.5'].mean():.1f}")
col2.metric("Median PM2.5 (ug/m3)",     f"{dff['PM2.5'].median():.1f}")
col3.metric("Stasiun Terburuk",
            dff.groupby("station")["PM2.5"].mean().idxmax())
col4.metric("Total Observasi",
            f"{len(dff):,}")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1 : Pola PM2.5 berdasarkan musim, jam, dan stasiun
# ════════════════════════════════════════════════════════════════════════════
st.header("Pertanyaan 1: Pola PM2.5 Berdasarkan Musim, Jam, dan Stasiun")
st.markdown(
    "Bagaimana pola konsentrasi PM2.5 berubah berdasarkan musim dan jam dalam sehari "
    "di seluruh stasiun pemantauan Beijing, dan stasiun mana yang secara konsisten "
    "mencatat tingkat polusi tertinggi?"
)

tab1a, tab1b, tab1c = st.tabs(["Per Stasiun", "Per Musim & Jam", "Heatmap Bulanan"])

# Tab: Per Stasiun
with tab1a:
    fig, ax = plt.subplots(figsize=(10, 5))
    station_avg = dff.groupby("station")["PM2.5"].mean().sort_values(ascending=True)
    median_val  = station_avg.median()
    colors = ["#c0392b" if v > median_val else "#2980b9" for v in station_avg.values]
    bars = ax.barh(station_avg.index, station_avg.values, color=colors, edgecolor="white")
    ax.axvline(median_val, color="gray", linestyle="--", linewidth=1.2,
               label=f"Median: {median_val:.1f} ug/m3")
    for bar, val in zip(bars, station_avg.values):
        ax.text(val + 0.4, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=8)
    ax.set_xlabel("Rata-rata PM2.5 (ug/m3)")
    ax.set_title("Rata-rata PM2.5 per Stasiun", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info(
        "Stasiun di pusat kota Beijing (Dongsi, Wanshouxigong, Nongzhanguan) secara "
        "konsisten berada di atas median konsentrasi PM2.5, mencerminkan dampak "
        "kepadatan lalu lintas dan aktivitas industri urban yang lebih tinggi."
    )

# Tab: Per Musim & Jam
with tab1b:
    col_a, col_b = st.columns(2)

    with col_a:
        fig, ax = plt.subplots(figsize=(5, 4))
        avail_seasons = [s for s in SEASON_ORDER if s in dff["season"].unique()]
        season_avg = dff.groupby("season")["PM2.5"].mean()[avail_seasons]
        bars2 = ax.bar(avail_seasons, season_avg.values,
                       color=[SEASON_COLORS[s] for s in avail_seasons],
                       edgecolor="white", width=0.6)
        for bar, val in zip(bars2, season_avg.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.1f}", ha="center", fontsize=9, fontweight="bold")
        ax.set_ylabel("Rata-rata PM2.5 (ug/m3)")
        ax.set_title("PM2.5 per Musim", fontweight="bold")
        ax.set_ylim(0, season_avg.max() * 1.2)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        fig, ax = plt.subplots(figsize=(5, 4))
        hourly_season = dff.groupby(["hour", "season"])["PM2.5"].mean().reset_index()
        for season in avail_seasons:
            ds = hourly_season[hourly_season["season"] == season]
            ax.plot(ds["hour"], ds["PM2.5"], color=SEASON_COLORS[season],
                    linewidth=2, marker="o", markersize=3, label=season)
        ax.set_xlabel("Jam dalam Sehari")
        ax.set_ylabel("Rata-rata PM2.5 (ug/m3)")
        ax.set_title("Pola Jam berdasarkan Musim", fontweight="bold")
        ax.set_xticks(range(0, 24, 3))
        ax.legend(title="Musim", fontsize=8)
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.info(
        "Musim Winter memiliki rata-rata PM2.5 tertinggi. Pola harian menunjukkan "
        "konsentrasi puncak terjadi malam hari (pukul 21-23), bukan jam sibuk pagi, "
        "karena melemahnya planetary boundary layer yang menekan dispersi vertikal polutan."
    )

# Tab: Heatmap Bulanan
with tab1c:
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot = dff.groupby(["month", "hour"])["PM2.5"].mean().unstack()
    month_labels = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    avail_months = [month_labels[i-1] for i in sorted(pivot.index)]
    sns.heatmap(pivot, ax=ax, cmap="YlOrRd", linewidths=0,
                xticklabels=range(0, 24, 3),
                yticklabels=avail_months,
                cbar_kws={"label": "PM2.5 (ug/m3)", "shrink": 0.8})
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_ylabel("Bulan")
    ax.set_title("Heatmap PM2.5: Bulan vs Jam dalam Sehari", fontweight="bold")
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info(
        "Area merah gelap terkonsentrasi di Desember-Maret pada jam malam, "
        "mengonfirmasi interaksi musim dingin dan jam malam sebagai periode risiko polusi tertinggi."
    )

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 2 : Korelasi faktor meteorologi
# ════════════════════════════════════════════════════════════════════════════
st.header("Pertanyaan 2: Korelasi Faktor Meteorologi terhadap PM2.5")
st.markdown(
    "Faktor meteorologi mana (suhu, tekanan udara, kecepatan angin, curah hujan) "
    "yang memiliki korelasi paling signifikan terhadap konsentrasi PM2.5?"
)

tab2a, tab2b, tab2c = st.tabs(["Matriks Korelasi", "Kecepatan Angin vs PM2.5", "Korelasi per Stasiun"])

METEO_VARS = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]

# Tab: Matriks Korelasi
with tab2a:
    fig, ax = plt.subplots(figsize=(7, 5))
    corr_cols = ["PM2.5"] + METEO_VARS
    corr_matrix = dff[corr_cols].corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, ax=ax, mask=mask, annot=True, fmt=".2f",
                cmap="coolwarm", center=0, square=True,
                linewidths=0.5, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 10})
    ax.set_title("Matriks Korelasi: PM2.5 vs Variabel Meteorologi", fontweight="bold")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Show correlation table
    corr_pm25 = dff[corr_cols].corr()["PM2.5"].drop("PM2.5").sort_values()
    corr_df = pd.DataFrame({
        "Variabel": corr_pm25.index,
        "Korelasi dengan PM2.5": corr_pm25.values.round(3),
        "Interpretasi": [
            "Kuat negatif" if v < -0.2 else
            "Lemah negatif" if v < 0 else
            "Lemah positif" if v < 0.2 else "Kuat positif"
            for v in corr_pm25.values
        ]
    })
    st.dataframe(corr_df, use_container_width=True, hide_index=True)

# Tab: Kecepatan Angin vs PM2.5
with tab2b:
    col_c, col_d = st.columns(2)

    with col_c:
        fig, ax = plt.subplots(figsize=(5, 4))
        sample = dff[["PM2.5", "WSPM", "season"]].dropna().sample(
            min(8000, len(dff)), random_state=42
        )
        for season in avail_seasons:
            s = sample[sample["season"] == season]
            ax.scatter(s["WSPM"], s["PM2.5"], alpha=0.3, s=8,
                       color=SEASON_COLORS[season], label=season)
        ax.set_xlabel("Kecepatan Angin - WSPM (m/s)")
        ax.set_ylabel("PM2.5 (ug/m3)")
        ax.set_title("Kecepatan Angin vs PM2.5", fontweight="bold")
        ax.legend(title="Musim", fontsize=8, markerscale=2)
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_d:
        fig, ax = plt.subplots(figsize=(5, 4))
        dff_copy = dff.copy()
        dff_copy["wspm_cat"] = pd.cut(
            dff_copy["WSPM"],
            bins=[0, 1, 2, 3, 5, 14],
            labels=["0-1", "1-2", "2-3", "3-5", ">5"]
        )
        wspm_pm25 = dff_copy.groupby("wspm_cat", observed=True)["PM2.5"].median()
        colors_bar = ["#c0392b", "#e67e22", "#f1c40f", "#27ae60", "#2980b9"]
        bars4 = ax.bar(wspm_pm25.index.astype(str), wspm_pm25.values,
                       color=colors_bar, edgecolor="white", width=0.6)
        for bar, val in zip(bars4, wspm_pm25.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{val:.0f}", ha="center", fontsize=9, fontweight="bold")
        ax.set_xlabel("Kategori Kecepatan Angin (m/s)")
        ax.set_ylabel("Median PM2.5 (ug/m3)")
        ax.set_title("Median PM2.5 per Kategori Angin", fontweight="bold")
        ax.set_ylim(0, wspm_pm25.max() * 1.25)
        ax.grid(axis="y", alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.info(
        "Kecepatan angin adalah faktor meteorologi paling konsisten. "
        "Pada kondisi angin lemah (0-1 m/s), median PM2.5 bisa mencapai 83 ug/m3. "
        "Pada kondisi angin kencang (di atas 5 m/s), median turun ke sekitar 33 ug/m3, "
        "penurunan lebih dari 60%."
    )

# Tab: Korelasi per Stasiun
with tab2c:
    fig, ax = plt.subplots(figsize=(10, 5))
    corr_per_station = dff.groupby("station").apply(
        lambda x: x[["PM2.5"] + METEO_VARS].corr()["PM2.5"].drop("PM2.5")
    ).reset_index()
    corr_per_station.columns = ["station"] + METEO_VARS
    pivot_corr = corr_per_station.set_index("station")
    sns.heatmap(pivot_corr, ax=ax, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, linewidths=0.5, cbar_kws={"shrink": 0.8},
                annot_kws={"size": 9})
    ax.set_title("Korelasi PM2.5 vs Meteorologi per Stasiun", fontweight="bold")
    ax.tick_params(axis="x", rotation=15)
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info(
        "Pola korelasi WSPM terhadap PM2.5 konsisten negatif di semua stasiun, "
        "membuktikan bahwa kecepatan angin adalah faktor dispersi universal terlepas dari lokasi."
    )

st.markdown("---")

# ── Footer ───────────────────────────────────────────────────────────────────
st.caption(
    "Dashboard ini dibuat menggunakan Streamlit sebagai bagian dari Proyek Analisis Data Dicoding. "
    "Dataset: Beijing Multi-Site Air Quality Data (PRSA) 2013-2017."
)
