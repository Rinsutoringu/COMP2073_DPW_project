import numpy as np
import plotly.express as px


COLORS = [
    "#E63946",
    "#457B9D",
    "#2A9D8F",
    "#F4A261",
    "#E76F51",
    "#8338EC",
    "#FF006E",
    "#3A86FF",
    "#FB5607",
    "#06D6A0",
    "#118AB2",
    "#EF476F",
    "#FFD166",
    "#073B4C",
    "#8AC926",
    "#1982C4",
    "#6A4C93",
    "#FF595E",
]


def make_type_counts_chart(type_counts):
    fig = px.bar(
        x=type_counts.values,
        y=type_counts.index,
        orientation="h",
        text=type_counts.values,
        color=type_counts.index,
        color_discrete_sequence=COLORS,
        height=500,
    )
    fig.update_traces(textposition="outside", textfont_size=13)
    fig.update_layout(showlegend=False, margin=dict(l=0, r=60, t=0, b=0))
    fig.update_xaxes(range=[0, type_counts.max() * 1.1])
    return fig


def make_stat_distribution_chart(df_box, type_order):
    fig = px.box(
        df_box,
        x="base_total",
        y="type1",
        category_orders={"type1": type_order},
        color="type1",
        color_discrete_sequence=COLORS[: len(type_order)],
        labels={"base_total": "Base Stat Total", "type1": ""},
        height=530,
    )
    fig.update_traces(hovertemplate="Base Stat Total %{x}<extra>%{fullData.name}</extra>")
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    return fig


def make_correlation_chart(corr):
    labels = corr.columns.tolist()
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    fig = px.imshow(
        corr.where(~mask),
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        height=460,
    )
    fig.update_xaxes(tickvals=list(range(len(labels))), ticktext=labels, side="top")
    fig.update_yaxes(tickvals=list(range(len(labels))), ticktext=labels)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), coloraxis_colorbar_len=0.7)
    return fig


def make_attack_defense_chart(df):
    df_scatter = df.assign(label=df["is_legendary"].map({True: "Legendary", False: "Normal"}))
    fig = px.scatter(
        df_scatter,
        x="attack",
        y="defense",
        color="label",
        color_discrete_map={"Normal": "#457B9D", "Legendary": "#E63946"},
        labels={"attack": "Attack", "defense": "Defense"},
        opacity=0.6,
        height=500,
    )
    for trace in fig.data:
        trace.hovertemplate = "Attack %{x}<br>Defense %{y}<br>%{fullData.name}<extra></extra>"
    fig.update_layout(showlegend=True, margin=dict(l=0, r=0, t=0, b=0))
    return fig
