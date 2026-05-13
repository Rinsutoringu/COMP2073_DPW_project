from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent.parent.parent / "archive" / "pokemon_cleaned.csv"
    df = pd.read_csv(csv_path)

    for col in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "base_total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if df["is_legendary"].dtype == object:
        df["is_legendary"] = df["is_legendary"].str.strip().str.title().map({"True": True, "False": False})

    df["is_legendary"] = df["is_legendary"].astype(bool)
    df["type2"] = df["type2"].replace("", np.nan)
    return df


@st.cache_data
def prep_type_counts(df):
    return pd.concat([
        df["type1"].value_counts(),
        df["type2"].dropna().value_counts(),
    ]).groupby(level=0).sum().sort_values()


@st.cache_data
def prep_box_order(df):
    counts = df["type1"].value_counts()
    subset = df[df["type1"].isin(counts[counts >= 5].index)]
    return subset.groupby("type1")["base_total"].median().sort_values(ascending=False).index.tolist()


@st.cache_data
def prep_box_data(df):
    type_order = prep_box_order(df)
    return df[df["type1"].isin(type_order)], type_order


@st.cache_data
def prep_correlation(df):
    stat_cols = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
    return df[stat_cols].corr()


@st.cache_data
def get_eda_metrics(df):
    from data_analysis.pokemon_stats import (
        attack_speed_correlation,
        highest_avg_attack_type1,
        most_common_type1,
    )

    top_type, _ = most_common_type1(df)
    best_atk_type, best_atk_val = highest_avg_attack_type1(df)
    atk_spd_corr = attack_speed_correlation(df)

    return {
        "most_common_type": top_type,
        "highest_attack_type": best_atk_type,
        "highest_attack_value": best_atk_val,
        "attack_speed_corr": atk_spd_corr
    }


@st.cache_data
def get_legendary_comparison(df):
    from data_analysis.pokemon_stats import legendary_vs_nonlegendary
    return legendary_vs_nonlegendary(df)
