from pathlib import Path

import pandas as pd
import streamlit as st

from utils.batch.simulation_batch import simulate_batch
from utils.cluster.simulation_cluster import simulation_cluster
from utils.results.plot import plot_simulation1, plot_simulation2

# --- Page configuration -------------------------------------------------------
st.set_page_config(page_title="Improve Warehouse Productivity using Order Batching",
                   initial_sidebar_state="expanded",
                   layout="wide",
                   page_icon="🛒")

# --- Warehouse layout constants -----------------------------------------------
Y_LOW, Y_HIGH = 5.5, 50        # alley low/high coordinates on the y-axis (m)
ORIGIN_LOC = [0, Y_LOW]        # picking route start/end point (depot)
DISTANCE_THRESHOLD = 35        # clustering: max walking distance between two locations (m)
DATA_FILE = Path("static/in/df_lines.csv")


# --- Cached data & simulations ------------------------------------------------
@st.cache_data(show_spinner=False)
def dataset_size():
    return len(pd.read_csv(DATA_FILE))


@st.cache_data(show_spinner=False)
def load(n):
    '''Load the first n order lines of the dataset'''
    return pd.read_csv(DATA_FILE).head(n)


@st.cache_data(show_spinner=False)
def run_simulation_1(lines_number, n1, n2):
    '''Simulation 1: total walking distance for each wave size in [n1, n2]'''
    df_orderlines = load(lines_number)
    _, df_results = simulate_batch(n1, n2, Y_LOW, Y_HIGH, ORIGIN_LOC, lines_number, df_orderlines)
    return df_results


@st.cache_data(show_spinner=False)
def run_simulation_2(lines_number, n1, n2, distance_threshold):
    '''Simulation 2: three wave-creation methods (no clustering / mono-line clustering / + centroids)'''
    df_orderlines = load(lines_number)
    list_results = [[], [], [], [], [], [], []]
    df_reswave, _ = simulation_cluster(Y_LOW, Y_HIGH, df_orderlines, list_results, n1, n2, distance_threshold)
    return df_reswave


# --- Sidebar: simulation parameters -------------------------------------------
max_scope = max(1, dataset_size() // 1000)
with st.sidebar:
    st.title("🛒 Picking Route Optimisation")
    st.caption("Simulate the impact of order batching strategies on the walking distance of warehouse pickers.")

    st.header("⚙️ Parameters")
    scope = st.slider("Scope (thousand order lines)", 1, max_scope, min(5, max_scope),
                      help="Number of order lines included in the simulations — "
                           f"the loaded dataset has {dataset_size():,} lines.")
    n1 = st.slider("N_MIN (orders/wave)", 1, 20, 1,
                   help="Smallest wave size to simulate.")
    n2 = st.slider("N_MAX (orders/wave)", n1 + 1, 20, max(n1 + 1, 10),
                   help="Largest wave size to simulate.")

    st.header("🥈 Simulation 2")
    run_2 = st.toggle("Compare batching methods",
                      help="Runs the three wave-creation methods: no clustering, clustering on single-line orders, "
                           "clustering + centroids for multi-line orders. Roughly 3× slower than Simulation 1.")

    st.divider()
    st.markdown("Made by [Samir Saci](https://samirsaci.com/about) · "
                "[Theory behind the model 📜](https://www.samirsaci.com/improve-warehouse-productivity-using-order-batching-with-python/)")

lines_number = scope * 1000

# --- Main page -----------------------------------------------------------------
st.title("📦 Improve Warehouse Productivity using Order Batching")
st.markdown(f"Simulating **{lines_number:,} order lines** with wave sizes from **{n1}** to **{n2} orders/wave** — "
            "tune the parameters in the sidebar, results update automatically.")

tab1, tab2 = st.tabs(["🥇 Impact of wave size", "🥈 Impact of batching method"])

# Simulation 1: runs by default on arrival (cached across reruns)
with tab1:
    st.subheader("How does the number of orders per wave impact the total walking distance?")
    with st.spinner(f"Simulating {lines_number:,} order lines for wave sizes {n1} to {n2}…"):
        df_results = run_simulation_1(lines_number, n1, n2)

    base = df_results.iloc[0]
    best = df_results.loc[df_results["distance"].idxmin()]
    saving = 1 - best["distance"] / base["distance"]

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Baseline — {int(base['order_per_wave'])} order(s)/wave", f"{base['distance']:,.0f} m")
    col2.metric(f"Best — {int(best['order_per_wave'])} orders/wave", f"{best['distance']:,.0f} m",
                delta=f"-{saving:.0%} walking distance", delta_color="inverse")
    col3.metric("Order lines simulated", f"{lines_number:,}")

    plot_simulation1(df_results, lines_number)

    with st.expander("📄 Results table"):
        st.dataframe(df_results.rename(columns={"order_per_wave": "Wave size (orders/wave)",
                                                "distance": "Walking distance (m)"}),
                     hide_index=True, width="stretch")

# Simulation 2: opt-in from the sidebar (3× heavier)
with tab2:
    st.subheader("Does spatial clustering of picking locations reduce the walking distance further?")
    st.markdown(f"Three wave-creation methods compared — **Method 1**: chronological batching (no clustering) · "
                f"**Method 2**: clustering on single-line orders · **Method 3**: clustering + centroids for "
                f"multi-line orders _(distance threshold: {DISTANCE_THRESHOLD} m)_.")
    if run_2:
        with st.spinner(f"Running the three methods on {lines_number:,} order lines — about 3× Simulation 1…"):
            df_reswave = run_simulation_2(lines_number, n1, n2, DISTANCE_THRESHOLD)

        best_n = df_reswave["distance_method_3"].idxmin()
        m1_val = df_reswave.loc[best_n, "distance_method_1"]
        m3_val = df_reswave.loc[best_n, "distance_method_3"]
        saving_2 = 1 - m3_val / m1_val

        col1, col2, col3 = st.columns(3)
        col1.metric(f"Method 1 — {int(best_n)} orders/wave", f"{m1_val:,.0f} m")
        col2.metric(f"Method 3 — {int(best_n)} orders/wave", f"{m3_val:,.0f} m",
                    delta=f"-{saving_2:.0%} vs Method 1", delta_color="inverse")
        col3.metric("Distance threshold", f"{DISTANCE_THRESHOLD} m")

        plot_simulation2(df_reswave, lines_number, DISTANCE_THRESHOLD)

        with st.expander("📄 Results table"):
            st.dataframe(df_reswave.reset_index().rename(
                columns={"orders_number": "Wave size (orders/wave)",
                         "distance_method_1": "Method 1 — No clustering (m)",
                         "distance_method_2": "Method 2 — Clustering single-line (m)",
                         "distance_method_3": "Method 3 — Clustering + centroids (m)"}),
                hide_index=True, width="stretch")
    else:
        st.info("👈 Turn on **Compare batching methods** in the sidebar to run this simulation.")
