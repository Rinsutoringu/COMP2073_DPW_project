import streamlit as st

from charts import (
    make_attack_defense_chart,
    make_correlation_chart,
    make_stat_distribution_chart,
    make_type_counts_chart,
)
from data_utils import load_data, prep_box_data, prep_correlation, prep_type_counts


st.set_page_config(page_title="Pokémon data at a glance", page_icon="⚡", layout="wide")

df = load_data()
type_counts = prep_type_counts(df)
df_box, type_order = prep_box_data(df)
corr = prep_correlation(df)

st.title("Pokémon data at a glance")
st.markdown(
    f"include **{len(df)}** pokémon in this csv, **{df['type1'].nunique()}** types, "
    f"where **{df['is_legendary'].sum()}** are legendary pokémon."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Type Counts",
    "Stat Distributions",
    "Stat Correlations",
    "Attack vs Defense",
])

with tab1:
    st.caption("Pokémon count by type — dual-type counted in both")
    st.plotly_chart(make_type_counts_chart(type_counts), width="stretch")

with tab2:
    st.caption("Base stat total distribution by type")
    st.plotly_chart(make_stat_distribution_chart(df_box, type_order), width="stretch")

with tab3:
    st.caption("Pearson correlation among HP, Attack, Defense, Sp. Atk, Sp. Def, Speed")
    st.plotly_chart(make_correlation_chart(corr), width="stretch")

with tab4:
    st.caption("Attack vs Defense — colored by legendary status")
    st.plotly_chart(make_attack_defense_chart(df), width="stretch")
