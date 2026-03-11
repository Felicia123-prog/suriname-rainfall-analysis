import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = "data"
OUTPUT_FIG_DIR = os.path.join("output", "figures")
OUTPUT_REPORT_DIR = os.path.join("output", "reports")

os.makedirs(OUTPUT_FIG_DIR, exist_ok=True)
os.makedirs(OUTPUT_REPORT_DIR, exist_ok=True)


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
    if years is None:
        return df
    max_year = df["Year"].max()
    min_year = max_year - years + 1
    return df[df["Year"].between(min_year, max_year)]


def plot_monthly_totals(df, station, years):
    df_station = df[df["Station"] == station]
    df_station = filter_last_years(df_station, years)

    pivot = df_station.pivot_table(index="Month", columns="Year", values="MonthlyTotal")

    plt.figure(figsize=(10, 6))
    for year in pivot.columns:
        plt.plot(pivot.index, pivot[year], marker="o", label=str(year))

    plt.title(f"Maandtotalen per jaar – {station} ({years or 'alle'} jaar)")
    plt.xlabel("Maand")
    plt.ylabel("Neerslag (mm)")
    plt.xticks(range(1, 13))
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()

    out = os.path.join(OUTPUT_FIG_DIR, f"{station}_{years or 'all'}years.png")
    plt.savefig(out, dpi=150)
    plt.close()


def compute_statistics(df):
    report = []

    yearly = df.groupby(["Station", "Year"])["MonthlyTotal"].sum().reset_index()

    avg_annual = yearly["MonthlyTotal"].mean()
    report.append(f"Gemiddelde jaarlijkse neerslag (alle stations): {avg_annual:.1f} mm")

    monthly_avg = df.groupby("Month")["MonthlyTotal"].mean()
    report.append("\nGemiddelde maandelijkse neerslag:")
    for m, v in monthly_avg.items():
        report.append(f"  Maand {m}: {v:.1f} mm")

    wettest = monthly_avg.idxmax()
    driest = monthly_avg.idxmin()
    report.append(f"\nNatste maand: {wettest}")
    report.append(f"Droogste maand: {driest}")

    report.append("\nTrend per station (eerste 10 jaar vs laatste 10 jaar):")
    for station, g in yearly.groupby("Station"):
        g = g.sort_values("Year")
        if len(g) >= 20:
            first10 = g.head(10)["MonthlyTotal"].mean()
            last10 = g.tail(10)["MonthlyTotal"].mean()
            diff = last10 - first10
            report.append(f"  {station}: {diff:+.1f} mm verschil")

    return "\n".join(report)


def save_report(text):
    path = os.path.join(OUTPUT_REPORT_DIR, "rainfall_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    df = load_all_stations()

    try:
        years = int(input("Hoeveel jaren analyseren? (bijv. 5, 10, 30, of leeg voor alle): ") or 0)
        years = years if years > 0 else None
    except:
        years = None

    for station in df["Station"].unique():
        plot_monthly_totals(df, station, years)

    stats = compute_statistics(df)
    save_report(stats)

    print("\nAnalyse voltooid. Grafieken en rapport staan in de map 'output'.")


if __name__ == "__main__":
    main()
