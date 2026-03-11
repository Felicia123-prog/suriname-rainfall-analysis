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
    max_year = df["Year"].max()
    min_year = max_year - years + 1
    return df[df["Year"].between(min_year, max_year)]


def compute_statistics(df):
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

# Maandnamen toevoegen
month_names = {
    1: "Jan", 2: "Feb", 3: "Mrt", 4: "Apr",
    5: "Mei", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Okt", 11: "Nov", 12: "Dec"
}
df["MonthName"] = df["Month"].map(month_names)

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
tab1, tab2, tab3 = st.tabs(["📊 Staafdiagram", "🌈 Regenval Matrix", "📈 Statistieken"])

# -----------------------------
# TAB 1 — STAAFDIAGRAM
# -----------------------------
with tab1:
    st.subheader("Maandtotalen per jaar (Staafdiagram)")

    pivot = df_filtered.pivot_table(
        index="Month",
        columns="Year",
        values="MonthlyTotal"
    )

    # Maandnamen op de x-as
    pivot.index = [month_names[m] for m in pivot.index]

    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.1
    months = range(len(pivot.index))

    for i, year in enumerate(pivot.columns):
        ax.bar(
            [m + i * bar_width for m in months],
            pivot[year],
            width=bar_width,
            label=str(year)
        )

    ax.set_xticks([m + bar_width for m in months])
    ax.set_xticklabels(pivot.index)

    ax.set_xlabel("Maand")
    ax.set_ylabel("Neerslag (mm)")
    ax.set_title(f"Maandtotalen per jaar – {station}")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    st.pyplot(fig)

# -----------------------------
# TAB 2 — REGENVAL MATRIX
# -----------------------------
with tab2:
    st.subheader("Regenval Matrix per maand/jaar")

    pivot = df_filtered.pivot_table(
        index="Year",
        columns="Month",
        values="MonthlyTotal"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    cax = ax.imshow(pivot, cmap="Blues", aspect="auto")

    ax.set_xticks(range(12))
    ax.set_xticklabels([month_names[m] for m in range(1, 13)])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    ax.set_xlabel("Maand")
    ax.set_ylabel("Jaar")
    ax.set_title(f"Regenval Matrix – {station}")

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
