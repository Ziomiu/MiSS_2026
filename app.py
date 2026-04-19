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

with st.sidebar:
    st.header("Model")
    model_name = st.selectbox(
        "Variant",
        list(MODEL_CLASSES.keys()),
        help="Wybierz wariant modelu epidemicznego."
    )

    st.divider()
    st.header("Common parameters")
    population = st.slider("Population", 50, 500, 200)
    grid_size = st.slider("Grid size", 10, 50, 25)
    infection_prob = st.slider("Infection probability", 0.0, 1.0, 0.2, step=0.01)
    recovery_time = st.slider("Recovery time", 1, 20, 5)
    steps = st.slider("Steps", 10, 200, 100)
    step_delay = st.slider("Delay per step (s)", 0.0, 1.0, 0.3, step=0.05)

    # Parametry specyficzne dla modelu
    extra_kwargs = {}

    if model_name == "Vaccine":
        st.divider()
        st.header("Vaccine parameters")
        extra_kwargs["vaccination_start"] = st.slider(
            "Vaccination start (step)", 1, 50, 10,
            help="Po ilu krokach od pierwszego zarażenia rusza kampania."
        )
        extra_kwargs["vaccination_rate"] = st.slider(
            "Vaccination rate (agents/step)", 1, 20, 3,
            help="Ile agentów S szczepimy na każdy krok po starcie kampanii."
        )

    elif model_name == "Hospital":
        st.divider()
        st.header("Hospital parameters")
        extra_kwargs["hospital_capacity"] = st.slider(
            "Hospital capacity", 1, 100, 15,
            help="Maksymalna liczba jednoczesnych łóżek szpitalnych."
        )
        extra_kwargs["hospitalization_prob"] = st.slider(
            "Hospitalization probability", 0.0, 1.0, 0.1, step=0.01,
            help="Prawdopodobieństwo trafienia zarażonego do szpitala na krok."
        )

    elif model_name == "SEIR":
        st.divider()
        st.header("SEIR parameters")
        extra_kwargs["exposure_time"] = st.slider(
            "Exposure time (steps)", 1, 20, 3,
            help="Liczba kroków w fazie E zanim agent stanie się zakaźny."
        )

col_grid, col_chart = st.columns([1, 1], gap="large")

with col_grid:
    st.subheader("Grid")
    grid_placeholder = st.empty()

with col_chart:
    st.subheader("Population over time")
    chart_placeholder = st.empty()
    metrics_placeholder = st.empty()

if st.button("Start Simulation", type="primary"):
    ModelClass = MODEL_CLASSES[model_name]
    active_states = MODEL_STATES[model_name]

    model = ModelClass(
        population,
        grid_size,
        grid_size,
        infection_prob,
        recovery_time,
        **extra_kwargs,
    )

    history = {state: [] for state in active_states}

    for step_num in range(steps):
        model.step()

        grid_rgb = np.ones((grid_size, grid_size, 3)) * 0.12  # ciemne tło
        for agent in model.scheduler.agents:
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
            labelcolor="white",
        )
        ax_grid.set_title(
            f"Step {step_num + 1} / {steps}",
            color="white", fontsize=9, pad=4
        )
        fig_grid.tight_layout(pad=0.3)
        grid_placeholder.pyplot(fig_grid)
        plt.close(fig_grid)

        # ── 2. Wykres liniowy ──────────────────────────────────
        data = model.datacollector.get_model_vars_dataframe()
        for state in active_states:
            col_name = STATE_COLORS[state][2]  # "Susceptible", "Infected" …
            if col_name in data.columns:
                history[state] = data[col_name].tolist()

        fig_chart, ax_chart = plt.subplots(figsize=(5, 3.5))
        fig_chart.patch.set_facecolor("#0e1117")
        ax_chart.set_facecolor("#161b22")

        for state in active_states:
            if history[state]:
                ax_chart.plot(
                    history[state],
                    color=STATE_COLORS[state][1],
                    linewidth=1.8,
                    label=STATE_COLORS[state][2],
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

        # ── 3. Metryki liczbowe ────────────────────────────────
        with metrics_placeholder.container():
            cols = st.columns(len(active_states))
            for i, state in enumerate(active_states):
                current_val = history[state][-1] if history[state] else 0
                cols[i].metric(
                    label=STATE_COLORS[state][2],
                    value=int(current_val),
                )

        time.sleep(step_delay)

    st.success(f"Simulation complete after {steps} steps.")
