import time

from model import EpidemicModel
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.title("Epidemic Simulation")

population = st.sidebar.slider("Population", 50, 500, 200)
grid_size = st.sidebar.slider("Grid size", 10, 50, 25)
infection_prob = st.sidebar.slider("Infection probability", 0.0, 1.0, 0.2)
recovery_time = st.sidebar.slider("Recovery time", 1, 20, 5)
steps = st.sidebar.slider("Steps", 10, 200, 100)

if st.button("Start Simulation"):

    model = EpidemicModel(
        population,
        grid_size,
        grid_size,
        infection_prob,
        recovery_time
    )

    grid_placeholder = st.empty()

    for _ in range(steps):
        time.sleep(0.5)
        model.step()

        grid = np.zeros((grid_size, grid_size,3))

        for agent in model.scheduler.agents:
            x, y = agent.pos

            if agent.state == "S":
                grid[x][y] = [0, 0, 1]
            elif agent.state == "I":
                grid[x][y] = [1, 0, 0]
            elif agent.state == "R":
                grid[x][y] = [0, 1, 0]

        fig, ax = plt.subplots()
        ax.imshow(grid)

        ax.set_xticks([])
        ax.set_yticks([])

        legend_patches = [
            mpatches.Patch(color='blue', label='Susceptible'),
            mpatches.Patch(color='red', label='Infected'),
            mpatches.Patch(color='green', label='Recovered')
        ]

        ax.legend(handles=legend_patches, loc='upper right')

        grid_placeholder.pyplot(fig)
        plt.close(fig)
