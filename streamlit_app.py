import pandas as pd
import pydeck as pdk
import streamlit as st
from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import GoogleAuthError
from streamlit.errors import StreamlitSecretNotFoundError

from st_utilities import (
    STATES,
    get_species_density,
    get_species_names,
    get_state_health,
    get_water_and_shade,
)

st.set_page_config(page_title="Forest Explorer", page_icon=":deciduous_tree:")
st.title("Forest Explorer")
st.write("Explore US forest inventory observations from 2000 onward.")
st.caption(
    "Historical surveys can record the same trees more than once. "
    "Counts describe sampled observations, not trees per acre or statewide totals."
)

species_tab, water_tab, health_tab = st.tabs(
    ["Species density", "Water and shade", "State forest health"]
)

try:
    with species_tab:
        species_names = get_species_names()
        if not species_names:
            st.warning("No species names are available in the database.")
        with st.form("species"):
            state = st.selectbox("State", STATES, index=2, key="species_state")
            species = st.selectbox(
                "Tree species",
                species_names,
            )
            submitted = st.form_submit_button(
                "Show species density", disabled=not species_names
            )

        if submitted:
            data = get_species_density(STATES[state], species)
            if data.empty:
                st.info("No matching observations. Try another state or species name.")
            else:
                st.metric("Mapped tree observations", f"{data.tree_count.sum():,}")
                st.pydeck_chart(pdk.Deck(
                    map_style="light",
                    layers=[pdk.Layer(
                        "HeatmapLayer",
                        data=data,
                        get_position="[longitude, latitude]",
                        get_weight="tree_count",
                        radius_pixels=40,
                    )],
                    initial_view_state=pdk.ViewState(
                        latitude=float(data.latitude.mean()),
                        longitude=float(data.longitude.mean()),
                        zoom=5,
                    ),
                ))
                st.caption("Warmer colors indicate more recorded trees nearby.")
                st.dataframe(data, hide_index=True)

    with water_tab:
        st.write("Explore plots reporting water and tall, living trees.")
        with st.form("water"):
            state = st.selectbox("State", STATES, index=2, key="water_state")
            height = st.slider("Minimum tree height (feet)", 5, 200, 30)
            submitted = st.form_submit_button("Find water and shade")

        if submitted:
            data = get_water_and_shade(STATES[state], height)
            if data.empty:
                st.info("No matching plots. Try a lower height or another state.")
            else:
                st.metric("Matching mapped locations", f"{len(data):,}")
                st.pydeck_chart(pdk.Deck(
                    map_style="light",
                    layers=[pdk.Layer(
                        "ScatterplotLayer",
                        data=data,
                        get_position="[longitude, latitude]",
                        get_fill_color=[0, 100, 200],
                        get_radius=500,
                        radius_min_pixels=4,
                    )],
                    initial_view_state=pdk.ViewState(
                        latitude=float(data.latitude.mean()),
                        longitude=float(data.longitude.mean()),
                        zoom=5,
                    ),
                ))
                st.dataframe(data, hide_index=True)
        st.warning(
            "Exploration only, not campsite recommendations. Water is reported on "
            "the plot, not a measured distance. Height does not guarantee shade. "
            "Verify current conditions, land access, and camping rules."
        )

    with health_tab:
        with st.form("health"):
            state = st.selectbox("State", STATES, index=2, key="health_state")
            submitted = st.form_submit_button("Show forest statistics")

        if submitted:
            data = get_state_health(STATES[state])
            row = data.iloc[0]
            if row.total_trees == 0:
                st.info("No tree observations found for this state since 2000.")
            else:
                st.caption(f"Inventory years: {int(row.first_year)}-{int(row.last_year)}")
                counts, heights = st.columns(2)
                counts.metric("Recorded tree observations", f"{int(row.total_trees):,}")
                heights.metric(
                    "Average tree height",
                    "Not available" if pd.isna(row.average_height_ft)
                    else f"{row.average_height_ft:.1f} ft",
                )
                st.metric(
                    "Tree observations per plot survey",
                    f"{row.total_trees / row.plot_surveys:.1f}",
                )
                status = pd.DataFrame({
                    "Status": ["Living", "Dead", "Other / unknown"],
                    "Observations": [
                        int(row.living_trees), int(row.dead_trees), int(row.other_trees)
                    ],
                }).set_index("Status")
                st.bar_chart(status)
                living, dead = st.columns(2)
                living.metric("Living share", f"{row.living_trees / row.total_trees:.1%}")
                dead.metric("Dead share", f"{row.dead_trees / row.total_trees:.1%}")
                st.caption(
                    "Shares use all observations, including other/unknown status. "
                    "These are descriptive statistics, not a forest health diagnosis."
                )
except (GoogleAPICallError, GoogleAuthError, StreamlitSecretNotFoundError) as error:
    st.error(f"Could not load BigQuery data: {error}")

st.caption(
    "FIA plot coordinates are approximate and sometimes swapped for privacy. "
    "Maps are not suitable for navigating to individual trees. "
    "Results are cached for ten minutes; each query has a 2 GB scan limit."
)
