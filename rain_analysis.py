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
tab1, tab2, tab3 = st.tabs(["📊 Lijngrafiek", "🌈 Regenval Matrix", "📈 Statistieken"])

# -----------------------------
# TAB 1 — LIJNGRAFIEK
# -----------------------------
with tab1:
    st.subheader("Maandtotalen per jaar")
    plot_monthly_totals(df_filtered, station)

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
