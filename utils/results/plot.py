import plotly.express as px
import streamlit as st

# Validated categorical palette (first three slots, light/dark variants).
# Series colors follow the entity: Method 1 = blue, Method 2 = orange, Method 3 = aqua.
LIGHT_SLOTS = ["#2a78d6", "#eb6834", "#1baf7a"]
DARK_SLOTS = ["#3987e5", "#d95926", "#199e70"]

METHOD_LABELS = {
    "distance_method_1": "Method 1 — No clustering",
    "distance_method_2": "Method 2 — Clustering on single-line orders",
    "distance_method_3": "Method 3 — Clustering + centroids for multi-line",
}

AXIS_LABELS = {
    "order_per_wave": "Wave size (orders/wave)",
    "orders_number": "Wave size (orders/wave)",
    "distance": "Total picking walking distance (m)",
    "method": "Batching method",
}


def _series_colors():
    '''Palette steps for the active Streamlit theme (light or dark).'''
    try:
        dark = st.context.theme.type == "dark"
    except Exception:
        dark = False
    return DARK_SLOTS if dark else LIGHT_SLOTS


def plot_simulation1(df_results, lines_number):
    '''Simulation 1 — total walking distance per wave size (single series).'''
    colors = _series_colors()
    fig = px.bar(
        data_frame=df_results,
        x='order_per_wave',
        y='distance',
        labels=AXIS_LABELS,
        color_discrete_sequence=[colors[0]],
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='Wave size: %{x} orders/wave<br>Walking distance: %{y:,.0f} m<extra></extra>',
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        height=480,
        barcornerradius=4,
        bargap=0.3,
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig, width='stretch')


def plot_simulation2(df_reswave, lines_number, distance_threshold):
    '''Simulation 2 — three batching methods compared (grouped bars).'''
    colors = _series_colors()
    color_map = dict(zip(METHOD_LABELS.values(), colors, strict=True))
    # Long format with readable method names for the legend
    df_plot = df_reswave.reset_index().melt(
        id_vars='orders_number', var_name='method', value_name='distance')
    df_plot['method'] = df_plot['method'].map(METHOD_LABELS)
    fig = px.bar(
        data_frame=df_plot,
        x='orders_number',
        y='distance',
        color='method',
        barmode='group',
        category_orders={'method': list(METHOD_LABELS.values())},
        color_discrete_map=color_map,
        labels=AXIS_LABELS,
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate='%{fullData.name}<br>Wave size: %{x} orders/wave<br>Walking distance: %{y:,.0f} m<extra></extra>',
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        height=480,
        barcornerradius=2,
        bargap=0.25,
        legend=dict(title=None, orientation='h', yanchor='bottom', y=1.02, x=0),
        margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig, width='stretch')
