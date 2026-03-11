import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

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

# Filter data voor gekozen station
df_station = df[df["Station"] == station]

# -----------------------------
# JAARSELECTIE (BEGIN + EINDE)
# -----------------------------
available_years = sorted(df_station["Year"].unique())

colA, colB = st.columns(2)

with colA:
    start_year = st.selectbox("Beginjaar:", available_years, index=0)

with colB:
    end_year = st.selectbox("Eindjaar:", available_years, index=len(available_years)-1)

# Validatie
if start_year > end_year:
    st.error("Beginjaar mag niet groter zijn dan eindjaar.")
    st.stop()

# Filteren op jaarbereik
df_filtered = df_station[df_station["Year"].between(start_year, end_year)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Staafdiagram", "🌈 Regenval Matrix", "📈 Statistieken"])

# -----------------------------
# TAB 1 — INTERACTIEVE STAAFDIAGRAM (PLOTLY)
# -----------------------------
with tab1:
    st.subheader("Maandtotalen per jaar (Interactieve Staafdiagram)")

    pivot = df_filtered.pivot_table(
        index="Month",
        columns="Year",
        values="MonthlyTotal"
    )

    month_labels = [month_names[m] for m in pivot.index]

    fig = go.Figure()

    for year in pivot.columns:
        fig.add_trace(go.Bar(
            x=month_labels,
            y=pivot[year],
            name=str(year),
            hovertemplate="<b>%{x}</b><br>Jaar: " + str(year) +
                          "<br>Neerslag: %{y} mm<extra></extra>"
        ))

    fig.update_layout(
        barmode='group',
        xaxis_title="Maand",
        yaxis_title="Neerslag (mm)",
        title=f"Maandtotalen per jaar – {station}",
        legend_title="Jaar",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

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
