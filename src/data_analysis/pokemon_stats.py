from pathlib import Path

import numpy as np
import pandas as pd


def load_data() -> pd.DataFrame:
    csv_path = (
        Path(__file__).resolve().parent.parent.parent
        / "archive"
        / "pokemon_cleaned.csv"
    )
    df = pd.read_csv(csv_path)

    num_cols = [
        "hp", "attack", "defense", "sp_attack", "sp_defense",
        "speed", "base_total",
    ]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["is_legendary"].dtype == object:
        df["is_legendary"] = (
            df["is_legendary"]
            .str.strip()
            .str.title()
            .map({"True": True, "False": False})
        )
    df["is_legendary"] = df["is_legendary"].astype(bool)

    df["type2"] = df["type2"].replace("", np.nan)

    return df


def most_common_type1(df: pd.DataFrame) -> tuple[str, int]:
    counts = df["type1"].value_counts()
    top_type = counts.idxmax()
    top_count = counts.max()
    return top_type, top_count


def highest_avg_attack_type1(df: pd.DataFrame) -> tuple[str, float]:
    avg_attack = df.groupby("type1")["attack"].mean()
    top_type = avg_attack.idxmax()
    top_value = avg_attack.max()
    return top_type, top_value


def attack_speed_correlation(df: pd.DataFrame) -> float:
    return df["attack"].corr(df["speed"])


def legendary_vs_nonlegendary(df: pd.DataFrame) -> pd.DataFrame:
    core_stats = ["attack", "defense", "speed", "hp", "sp_attack", "sp_defense"]

    legend = df[df["is_legendary"]]
    non_legend = df[~df["is_legendary"]]

    rows = []
    for col in core_stats:
        lm = legend[col].mean()
        nm = non_legend[col].mean()
        rows.append({
            "stat": col,
            "legendary_mean": round(lm, 2),
            "non_legendary_mean": round(nm, 2),
            "diff": round(lm - nm, 2),
        })

    return pd.DataFrame(rows)


def main() -> None:
    df = load_data()

    top_type, top_count = most_common_type1(df)
    print(f"most common type1: {top_type} ({top_count})")

    best_type, best_avg = highest_avg_attack_type1(df)
    print(f"highest avg attack type1: {best_type} ({best_avg:.2f})")

    corr = attack_speed_correlation(df)
    print(f"attack-speed pearson r: {corr:.4f}")

    print("\nlegendary vs non-legendary (mean stats):")
    print(legendary_vs_nonlegendary(df).to_string(index=False))


if __name__ == "__main__":
    main()
