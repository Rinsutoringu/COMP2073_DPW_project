import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="宝可梦数据一览", page_icon="⚡", layout="wide")

PKM_COLORS = ["#E63946", "#457B9D", "#2A9D8F", "#F4A261", "#E76F51",
              "#8338EC", "#FF006E", "#3A86FF", "#FB5607", "#06D6A0",
              "#118AB2", "#EF476F", "#FFD166", "#073B4C", "#8AC926",
              "#1982C4", "#6A4C93", "#FF595E"]

@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent.parent.parent / "archive" / "pokemon_cleaned.csv"
    df = pd.read_csv(csv_path)

    num_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_total']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'is_legendary' in df.columns:
        if df['is_legendary'].dtype == object:
            df['is_legendary'] = df['is_legendary'].str.strip().str.title().map({'True': True, 'False': False})
        df['is_legendary'] = df['is_legendary'].astype(bool)

    if 'type2' in df.columns:
        df['type2'] = df['type2'].replace('', np.nan)

    return df

@st.cache_data
def prep_type_counts(df):
    counts = pd.concat([
        df['type1'].value_counts(),
        df['type2'].dropna().value_counts()
    ]).groupby(level=0).sum().sort_values()
    return counts

@st.cache_data
def prep_box_data(df, min_count=5):
    type_counts = df['type1'].value_counts()
    valid = type_counts[type_counts >= min_count].index.tolist()
    subset = df[df['type1'].isin(valid)].copy()
    order = subset.groupby('type1')['base_total'].median().sort_values(ascending=False).index.tolist()
    return subset, order

@st.cache_data
def prep_corr(df):
    stat_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
    return df[stat_cols].corr()

df = load_data()
type_counts = prep_type_counts(df)
df_box, type_order = prep_box_data(df)
corr = prep_corr(df)

st.title("⚡ 宝可梦数据一览")
st.markdown(f"收录 **{len(df)}** 只宝可梦，**{df['type1'].nunique()}** 种属性，其中 **{df['is_legendary'].sum()}** 只为神兽")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 属性数量", "🎻 能力值分布", "🔥 能力相关性", "🗡️ 攻击 vs 防御"
])

with tab1:
    fig = px.bar(
        x=type_counts.values, y=type_counts.index,
        orientation='h',
        text=type_counts.values,
        labels={"x": "数量", "y": ""},
        color=type_counts.index,
        color_discrete_sequence=PKM_COLORS,
        height=500,
    )
    fig.update_traces(textposition='outside', textfont=dict(size=13))
    fig.update_layout(showlegend=False, margin=dict(l=0, r=80, t=10, b=10))
    fig.update_xaxes(range=[0, type_counts.max() * 1.12])
    st.plotly_chart(fig, use_container_width=True)
    st.caption("双属性宝可梦按两个属性分别计算")

with tab2:
    chart_mode = st.radio("展示方式", ["箱线图", "小提琴图", "叠加"], horizontal=True, key="box_violin")

    if chart_mode == "箱线图":
        fig = px.box(
            df_box, x='base_total', y='type1',
            category_orders={"type1": type_order},
            color='type1',
            color_discrete_sequence=PKM_COLORS[:len(type_order)],
            labels={"base_total": "总能力值", "type1": ""},
            height=530,
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=10, t=10, b=10))

    elif chart_mode == "小提琴图":
        fig = px.violin(
            df_box, x='base_total', y='type1',
            category_orders={"type1": type_order},
            color='type1',
            color_discrete_sequence=PKM_COLORS[:len(type_order)],
            labels={"base_total": "总能力值", "type1": ""},
            box=False,
            height=530,
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=10, t=10, b=10))

    else:
        fig = go.Figure()
        for i, t in enumerate(type_order):
            subset = df_box[df_box['type1'] == t]['base_total']
            color = PKM_COLORS[i % len(PKM_COLORS)]
            fig.add_trace(go.Violin(
                x=subset, name=t, side='negative',
                line_color=color, fillcolor=color, opacity=0.35,
                meanline_visible=True, spanmode='hard',
                legendgroup=t, showlegend=False,
            ))
            fig.add_trace(go.Box(
                x=subset, name=t,
                marker_color=color, fillcolor=color, opacity=0.7,
                line_color='black', line_width=1,
                width=0.3, boxpoints='outliers',
                legendgroup=t, showlegend=False,
            ))
        fig.update_layout(
            yaxis=dict(categoryorder='array', categoryarray=type_order[::-1]),
            xaxis_title="总能力值", yaxis_title="",
            margin=dict(l=0, r=10, t=10, b=10),
            height=530,
            violinmode='overlay',
        )

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    stat_labels = ['HP', '攻击', '防御', '特攻', '特防', '速度']
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    masked = corr.where(~mask)

    fig = px.imshow(
        masked,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        range_color=[-1, 1],
        zmin=-1, zmax=1,
        aspect='auto',
        height=480,
    )
    fig.update_xaxes(tickvals=list(range(6)), ticktext=stat_labels, side='top')
    fig.update_yaxes(tickvals=list(range(6)), ticktext=stat_labels)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_colorbar=dict(title="", thickness=15, len=0.7),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    df['legend_label'] = df['is_legendary'].map({True: '神兽', False: '普通'})

    fig = px.scatter(
        df, x='attack', y='defense',
        color='legend_label',
        color_discrete_map={'普通': '#457B9D', '神兽': '#E63946'},
        labels={"attack": "攻击力", "defense": "防御力", "legend_label": ""},
        opacity=0.7,
        height=500,
    )
    fig.update_traces(marker=dict(size=8))
    fig.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"神兽占比 {df['is_legendary'].mean():.1%}")

st.divider()
with st.expander("数据预览"):
    st.dataframe(df.drop(columns=['legend_label']).head(50), use_container_width=True)
