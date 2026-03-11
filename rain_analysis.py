import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------
# DATA MAP
# -----------------------------
DATA_DIR = "data"

# -----------------------------
# FUNCTIES
# -----------------------------

def load_all_stations():
    """Lees alle Excel-bestanden (.xlsx) in de data-map."""
    frames = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".xlsx"):
            station = fname.replace(".xlsx", "")
            path = os.path.join(DATA_DIR, fname)
            df = pd.read_excel(path)
            df["Station"] = station
            frames.append(df)
    return pd.concat(frames, ignore_index=True)


def filter_last_years(df, years):
    """Filter op de laatste X jaren."""
    max_year = df["Year"].max()
    min_year = max_year - years + 1
    return df[df["Year"].between(min_year, max_year)]


def plot_monthly_totals(df, station):
    """Maak een grafiek van maandtotalen per jaar."""
    pivot = df.pivot_table(index="Month", columns="Year", values="MonthlyTotal")

    fig, ax = plt.subplots(figsize=(10, 5))
    for year in pivot.columns:
        ax.plot(pivot.index, pivot[year], marker="o", label=str(year))

    ax.set_title(f"Maandtotalen per jaar – {station}")
    ax.set_xlabel("Maand")
    ax.set_ylabel("Neerslag (mm)")
    ax.set_xticks(range(1, 13))
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    st.pyplot(fig)


def compute_statistics(df):
    """Bereken statistieken voor de geselecteerde data."""
    yearly = df.groupby(["Station", "Year"])["MonthlyTotal"].sum().reset_index()
    monthly_avg = df.groupby("Month")["MonthlyTotal"].mean()

    stats = {
        "avg_annual": yearly["MonthlyTotal"].mean(),
        "monthly_avg": monthly_avg,
        "wettest": monthly_avg.idxmax(),
        "driest": monthly_avg.idxmin(),
    }
    return stats


# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("🌧️ Suriname Rainfall & Climate Analysis")
st.write("Interactieve analyse van maandelijkse neerslagdata van Surinaamse weerstations.")

# Data laden
df = load_all_stations()

# Station kiezen
stations = sorted(df["Station"].unique())
station = st.selectbox("Kies een station:", stations)

# Aantal jaren kiezen
max_years = df["Year"].nunique()
years = st.slider("Aantal jaren om te analyseren:", 1, max_years, 10)

# Filteren
df_station = df[df["Station"] == station]
df_filtered = filter_last_years(df_station, years)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Lijngrafiek", "🔥 Heatmap", "📈 Statistieken"])

# -----------------------------
# TAB 1 — LIJNGRAFIEK
# -----------------------------
with tab1:
    st.subheader("Maandtotalen per jaar")
    plot_monthly_totals(df_filtered, station)

# -----------------------------
# TAB 2 — HEATMAP
# -----------------------------
with tab2:
    st.subheader("Heatmap van neerslag per maand/jaar")

    pivot = df_filtered.pivot_table(
        index="Year",
        columns="Month",
        values="MonthlyTotal"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    cax = ax.imshow(pivot, cmap="Blues", aspect="auto")

    ax.set_xticks(range(12))
    ax.set_xticklabels(range(1, 13))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    ax.set_xlabel("Maand")
    ax.set_ylabel("Jaar")
    ax.set_title(f"Heatmap – {station}")

    fig.colorbar(cax, label="Neerslag (mm)")
    st.pyplot(fig)

# -----------------------------
# TAB 3 — STATISTIEKEN
# -----------------------------
with tab3:
    st.subheader("Statistieken")
    stats = compute_statistics(df_filtered)

    col1, col2, col3 = st.columns(3)
    col1.metric("Gem. jaarlijkse neerslag", f"{stats['avg_annual']:.1f} mm")
    col2.metric("Natste maand", stats["wettest"])
    col3.metric("Droogste maand", stats["driest"])

    st.write("Gemiddelde maandelijkse neerslag:")
    st.line_chart(stats["monthly_avg"])
