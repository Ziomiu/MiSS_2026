import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

from models import VaccineModel, HospitalModel, SEIRModel, BaseEpidemicModel

STATE_COLORS = {
    "S": ([0.22, 0.48, 0.85], "blue", "Susceptible"),
    "E": ([0.95, 0.60, 0.10], "orange", "Exposed"),
    "I": ([0.85, 0.20, 0.20], "red", "Infected"),
    "H": ([0.70, 0.10, 0.70], "purple", "Hospitalized"),
    "R": ([0.20, 0.72, 0.35], "green", "Recovered"),
    "V": ([0.20, 0.75, 0.85], "cyan", "Vaccinated"),
}

MODEL_STATES = {
    "Base SIR": ["S", "I", "R"],
    "Vaccine": ["S", "I", "R", "V"],
    "Hospital": ["S", "I", "H", "R"],
    "SEIR": ["S", "E", "I", "R"],
}

MODEL_CLASSES = {
    "Base SIR": BaseEpidemicModel,
    "Vaccine": VaccineModel,
    "Hospital": HospitalModel,
    "SEIR": SEIRModel,
}

st.set_page_config(page_title="Epidemic Simulation", layout="wide")
st.title("Epidemic Simulation")

# Initializing session state
if 'run' not in st.session_state:
    st.session_state.run = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'model' not in st.session_state:
    st.session_state.model = None
if 'history' not in st.session_state:
    st.session_state.history = {}
if 'params' not in st.session_state:
    st.session_state.params = {}

with st.sidebar:
    st.header("Model")
    model_name = st.selectbox(
        "Variant",
        list(MODEL_CLASSES.keys()),
        help="Wybierz wariant modelu epidemicznego."
    )

    st.divider()
    st.header("Common parameters")
    population = st.slider(
        "Population", 50, 500, 200,
        help="Całkowita liczba agentów w symulacji."
    )
    grid_size = st.slider(
        "Grid size", 10, 50, 25,
        help="Rozmiar kwadratowej siatki (N x N)."
    )
    infection_prob = st.slider(
        "Infection probability", 0.1, 1.0, 0.4, step=0.01,
        help="Prawdopobieństwo zakażenia agenta podatnego (w stanie S) przez agenta zakaźnego (w stanie I)."
    )
    recovery_time = st.slider(
        "Recovery time", 3, 20, 10,
        help="Liczba kroków, po których agent zdrowieje (przechodzi do stanu R)."
    )
    steps = st.slider(
        "Steps", 50, 200, 100,
        help="Liczba kroków symulacji."
    )
    step_delay = st.slider(
        "Delay per step (s)", 0.3, 1.0, 0.5, step=0.1,
        help="Czas trwania jednego kroku symulacji."
    )

    extra_kwargs = {}

    if model_name == "Vaccine":
        st.divider()
        st.header("Vaccine parameters")
        extra_kwargs["vaccination_start"] = st.slider(
            "Vaccination start (steps)", 5, 20, 10,
            help="Liczba kroków od pierwszego zakażenia, po których rusza kampania."
        )
        extra_kwargs["vaccination_rate"] = st.slider(
            "Vaccination rate (agents/step)", 1, 20, 3,
            help="Liczba agentów podatnych (w stanie S), którzy są szczepieni w każdym kroku po starcie kampanii."
        )
    elif model_name == "Hospital":
        st.divider()
        st.header("Hospital parameters")
        extra_kwargs["hospital_capacity"] = st.slider(
            "Hospital capacity", 10, 50, 20,
            help="Maksymalna liczba jednocześnie zajętych łóżek szpitalnych."
        )
        extra_kwargs["hospitalization_prob"] = st.slider(
            "Hospitalization probability", 0.1, 1.0, 0.2, step=0.01,
            help="Prawdopodobieństwo trafienia zakażonego do szpitala w każdym kroku."
        )
    elif model_name == "SEIR":
        st.divider()
        st.header("SEIR parameters")
        extra_kwargs["exposure_time"] = st.slider(
            "Exposure time (steps)", 3, 20, 7,
            help="Liczba kroków, po których agent narażony (w stanie E) stanie się zakaźny (stan I)."
        )

current_params = {
    "model": model_name,
    "pop": population,
    "grid": grid_size,
    "inf": infection_prob,
    "rec": recovery_time,
    **extra_kwargs
}

# Detect parameters change
if st.session_state.model is not None:
    if current_params != st.session_state.params:
        st.session_state.model = None
        st.session_state.history = {}
        st.session_state.params = {}
        st.session_state.current_step = 0
        st.session_state.run = False
        st.rerun()

col_b1, col_b2, _ = st.columns([1, 1, 4])

# Start / Reset button depending on the state
if st.session_state.current_step == 0 and not st.session_state.run:
    if col_b1.button("Start Simulation", type="primary"):
        ModelClass = MODEL_CLASSES[model_name]
        st.session_state.model = ModelClass(
            population,
            grid_size,
            grid_size,
            infection_prob,
            recovery_time,
            **extra_kwargs
        )
        st.session_state.history = {state: [] for state in MODEL_STATES[model_name]}
        st.session_state.params = current_params
        st.session_state.run = True
        st.rerun()
    
if st.session_state.run or st.session_state.current_step > 0:
    if col_b1.button("Reset Simulation"):
        st.session_state.model = None
        st.session_state.history = {}
        st.session_state.params = {}
        st.session_state.current_step = 0
        st.session_state.run = False
        st.rerun()

# Pause / Resume button depending on the state
if st.session_state.current_step < steps:
    if st.session_state.run:
        if col_b2.button("Pause Simulation"):
            st.session_state.run = False
            st.rerun()
    elif st.session_state.current_step > 0:
        if col_b2.button("Resume Simulation", type="primary"):
            st.session_state.run = True
            st.rerun()

col_grid, col_chart = st.columns([1, 1], gap="large")

with col_grid:
    st.subheader("Grid")
    grid_placeholder = st.empty()

with col_chart:
    st.subheader("Population over time")
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()

# -----------------------------------------------

# Function to plot population chart - separated to not repeat code 
def plot_population():
    grid_rgb = np.ones((grid_size, grid_size, 3)) * 0.12
    for agent in st.session_state.model.scheduler.agents:
        x, y = agent.pos
        color, _, _ = STATE_COLORS.get(agent.state, ([1, 1, 1], "", ""))
        grid_rgb[y][x] = color

    fig_grid, ax_grid = plt.subplots(figsize=(4, 4))
    fig_grid.patch.set_facecolor("#0e1117")
    ax_grid.set_facecolor("#0e1117")
    ax_grid.imshow(grid_rgb, interpolation="nearest")
    ax_grid.set_xticks([])
    ax_grid.set_yticks([])

    patches = [
        mpatches.Patch(color=STATE_COLORS[s][1], label=STATE_COLORS[s][2])
        for s in active_states
    ]
    ax_grid.legend(
        handles=patches,
        loc="upper right",
        fontsize=7,
        framealpha=0.6,
        facecolor="#1e2128",
        edgecolor="none",
        labelcolor="white"
    )
    status_label = "" if st.session_state.run else " (Paused)"
    ax_grid.set_title(
        f"Step {st.session_state.current_step} / {steps}{status_label}",
        color="white", fontsize=9, pad=4
    )
    fig_grid.tight_layout(pad=0.3)
    grid_placeholder.pyplot(fig_grid)
    plt.close(fig_grid)

    data = st.session_state.model.datacollector.get_model_vars_dataframe()
    for state in active_states:
        col_name = STATE_COLORS[state][2]
        if col_name in data.columns:
            st.session_state.history[state] = data[col_name].tolist()

    fig_chart, ax_chart = plt.subplots(figsize=(4, 3.5))
    fig_chart.patch.set_facecolor("#0e1117")
    ax_chart.set_facecolor("#161b22")

    for state in active_states:
        if st.session_state.history[state]:
            ax_chart.plot(
                st.session_state.history[state],
                color=STATE_COLORS[state][1],
                linewidth=1.8,
                label=STATE_COLORS[state][2]
            )

    ax_chart.set_xlim(0, steps)
    ax_chart.set_ylim(0, population)
    ax_chart.set_xlabel("Step", color="#8b949e", fontsize=8)
    ax_chart.set_ylabel("Agents", color="#8b949e", fontsize=8)
    ax_chart.tick_params(colors="#8b949e", labelsize=7)
    for spine in ax_chart.spines.values():
        spine.set_edgecolor("#30363d")
    ax_chart.legend(
        fontsize=7, framealpha=0.5,
        facecolor="#1e2128", edgecolor="none", labelcolor="white"
    )
    fig_chart.tight_layout(pad=0.5)
    chart_placeholder.pyplot(fig_chart)
    plt.close(fig_chart)

    with metrics_placeholder.container():
        cols = st.columns(len(active_states))
        for i, state in enumerate(active_states):
            current_val = st.session_state.history[state][-1] if st.session_state.history[state] else 0
            cols[i].metric(
                label=STATE_COLORS[state][2],
                value=int(current_val)
            )

# -----------------------------------------------

# Return to the main script part 
if st.session_state.model is not None:
    active_states = MODEL_STATES[model_name]

    if st.session_state.run:
        while st.session_state.current_step < steps:
            start_time = time.perf_counter()

            st.session_state.model.step()
            st.session_state.current_step += 1

            plot_population()

            elapsed_time = time.perf_counter() - start_time

            if not st.session_state.run: break
            if st.session_state.current_step >= steps:
                st.rerun()
            else:
                # it usually is around 0.3 seconds
                # print(elapsed)

                # sleep appropriate time to make the step last possibly closest to step_delay
                # some minimal time is required for gui to react
                time.sleep(max(0.01, step_delay - elapsed_time))

        plot_population()
        st.success(f"Simulation complete after {steps} steps.")
        
    else:
        plot_population()
