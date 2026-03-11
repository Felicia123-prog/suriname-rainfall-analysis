import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

DATA_DIR = "data"


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


def plot_monthly_totals(df, station):
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
    yearly = df.groupby(["Station", "Year"])["MonthlyTotal"].sum().reset_index()
    monthly_avg = df.groupby("Month")["MonthlyTotal"].mean()

    stats = {
        "avg_annual": yearly["MonthlyTotal"].mean(),
        "monthly_avg": monthly_avg,
        "wettest": monthly_avg.idxmax(),
        "driest": monthly_avg.idxmin(),
    }
    return stats


# ---------------- STREAMLIT UI ---------------- #

st.title("🌧️ Suriname Rainfall & Climate Analysis")
st.write("Analyseer maandelijkse neerslagdata van Surinaamse weerstations.")

df = load_all_stations()

# Station kiezen
stations = sorted(df["Station"].unique())
station = st.selectbox("Kies een station:", stations)

# Aantal jaren kiezen
max_years = df["Year"].nunique()
years = st.slider("Aantal jaren om te analyseren:", 1, max_years, 10)

# Filter data
df_station = df[df["Station"] == station]
df_filtered = filter_last_years(df_station, years)

# Grafiek tonen
st.subheader("📊 Maandtotalen per jaar")
plot_monthly_totals(df_filtered, station)

# Statistieken tonen
st.subheader("📈 Statistieken")
stats = compute_statistics(df_filtered)

st.write(f"**Gemiddelde jaarlijkse neerslag:** {stats['avg_annual']:.1f} mm")
st.write(f"**Natste maand:** {stats['wettest']}")
st.write(f"**Droogste maand:** {stats['driest']}")

st.write("**Gemiddelde maandelijkse neerslag:**")
st.line_chart(stats["monthly_avg"])
