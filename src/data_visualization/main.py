import streamlit as st

from charts import (
    make_attack_defense_chart,
    make_correlation_chart,
    make_stat_distribution_chart,
    make_type_counts_chart,
)
from data_utils import (
    get_eda_metrics,
    get_legendary_comparison,
    load_data,
    prep_box_data,
    prep_correlation,
    prep_type_counts,
)


st.set_page_config(page_title="Pokémon data at a glance", page_icon="⚡", layout="wide")

df = load_data()
type_counts = prep_type_counts(df)
df_box, type_order = prep_box_data(df)
corr = prep_correlation(df)
eda_metrics = get_eda_metrics(df)

st.title("Pokémon data at a glance")
st.markdown(
    f"include **{len(df)}** pokémon in this csv, **{df['type1'].nunique()}** types, "
    f"where **{df['is_legendary'].sum()}** are legendary pokémon."
)

col1, col2, col3 = st.columns(3)
col1.metric("Most Common Type", eda_metrics["most_common_type"])
col2.metric("Highest Avg Attack", f"{eda_metrics['highest_attack_type']} ({eda_metrics['highest_attack_value']:.1f})")
col3.metric("Atk-Speed Correlation", f"{eda_metrics['attack_speed_corr']:.3f}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Type Counts",
    "Stat Distributions",
    "Stat Correlations",
    "Attack vs Defense",
    "EDA Insights",
])

with tab1:
    st.caption("Pokémon count by type — dual-type counted in both")
    st.plotly_chart(make_type_counts_chart(type_counts), use_container_width=True)

with tab2:
    st.caption("Base stat total distribution by type")
    st.plotly_chart(make_stat_distribution_chart(df_box, type_order), use_container_width=True)

with tab3:
    st.caption("Pearson correlation among HP, Attack, Defense, Sp. Atk, Sp. Def, Speed")
    st.plotly_chart(make_correlation_chart(corr), use_container_width=True)

with tab4:
    st.caption("Attack vs Defense — colored by legendary status")
    st.plotly_chart(make_attack_defense_chart(df), use_container_width=True)

with tab5:
    st.subheader("Deep EDA Insights")

    st.write("### 1. Most Common Type")
    st.write(f"The most common primary type is **{eda_metrics['most_common_type']}**.")

    st.write("### 2. Highest Average Attack")
    st.write(f"The **{eda_metrics['highest_attack_type']}** type has the highest average attack power at **{eda_metrics['highest_attack_value']:.2f}**.")

    st.write("### 3. Attack & Speed Correlation")
    correlation = eda_metrics['attack_speed_corr']
    relation = "positive" if correlation > 0 else "negative"
    st.write(f"The Pearson correlation between Attack and Speed is **{correlation:.4f}**, indicating a **{relation}** relationship.")

    st.write("### 4. Legendary vs Non-Legendary Comparison")
    st.dataframe(get_legendary_comparison(df), hide_index=True, use_container_width=True)
    st.caption("Values show the mean stats and the absolute difference (diff > 0 means Legendary is higher).")
