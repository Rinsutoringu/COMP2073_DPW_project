import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Pokémon data at a glance", page_icon="⚡", layout="wide")

COLORS = ["#E63946", "#457B9D", "#2A9D8F", "#F4A261", "#E76F51",
          "#8338EC", "#FF006E", "#3A86FF", "#FB5607", "#06D6A0",
          "#118AB2", "#EF476F", "#FFD166", "#073B4C", "#8AC926",
          "#1982C4", "#6A4C93", "#FF595E"]

@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent.parent.parent / "archive" / "pokemon_cleaned.csv"
    df = pd.read_csv(csv_path)
    for col in ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_total']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if df['is_legendary'].dtype == object:
        df['is_legendary'] = df['is_legendary'].str.strip().str.title().map({'True': True, 'False': False})
    df['is_legendary'] = df['is_legendary'].astype(bool)
    df['type2'] = df['type2'].replace('', np.nan)
    return df

@st.cache_data
def prep_type_counts(df):
    return pd.concat([
        df['type1'].value_counts(),
        df['type2'].dropna().value_counts()
    ]).groupby(level=0).sum().sort_values()

@st.cache_data
def prep_box_order(df):
    counts = df['type1'].value_counts()
    subset = df[df['type1'].isin(counts[counts >= 5].index)]
    return subset.groupby('type1')['base_total'].median().sort_values(ascending=False).index.tolist()

df = load_data()
type_counts = prep_type_counts(df)
type_order = prep_box_order(df)
df_box = df[df['type1'].isin(type_order)]

st.title("Pokémon data at a glance")
st.markdown(f"include **{len(df)}** pokémon in this csv, **{df['type1'].nunique()}** types, where **{df['is_legendary'].sum()}** are legendary pokémon.")

tab1, tab2, tab3, tab4 = st.tabs([
    "Type Counts", "Stat Distributions", "Stat Correlations", "Attack vs Defense"
])

with tab1:
    st.caption("Pokémon count by type — dual-type counted in both")
    fig = px.bar(
        x=type_counts.values, y=type_counts.index, orientation='h',
        text=type_counts.values, color=type_counts.index,
        color_discrete_sequence=COLORS, height=500,
    )
    fig.update_traces(textposition='outside', textfont_size=13)
    fig.update_layout(showlegend=False, margin=dict(l=0, r=60, t=0, b=0))
    fig.update_xaxes(range=[0, type_counts.max() * 1.1])
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.caption("Base stat total distribution by type")
    fig = px.box(
        df_box, x='base_total', y='type1',
        category_orders={"type1": type_order},
        color='type1', color_discrete_sequence=COLORS[:len(type_order)],
        labels={"base_total": "Base Stat Total", "type1": ""},
        height=530,
    )
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.caption("Pearson correlation among HP, Attack, Defense, Sp. Atk, Sp. Def, Speed")
    stat_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
    labels = stat_cols
    corr = df[stat_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)

    fig = px.imshow(
        corr.where(~mask), text_auto='.2f',
        color_continuous_scale='RdBu_r', zmin=-1, zmax=1,
        aspect='auto', height=460,
    )
    fig.update_xaxes(tickvals=list(range(6)), ticktext=labels, side='top')
    fig.update_yaxes(tickvals=list(range(6)), ticktext=labels)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), coloraxis_colorbar_len=0.7)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.caption("Attack vs Defense — colored by legendary status")
    df_scatter = df.assign(label=df['is_legendary'].map({True: 'Divine Beast', False: 'Normal'}))
    fig = px.scatter(
        df_scatter, x='attack', y='defense',
        color='label',
        color_discrete_map={'Normal': '#457B9D', 'Divine Beast': '#E63946'},
        labels={"attack": "Attack", "defense": "Defense"},
        opacity=0.6, height=500,
    )
    for trace in fig.data:
        trace.hovertemplate = 'Attack %{x}<br>Defense %{y}<br>%{fullData.name}<extra></extra>'
    fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
