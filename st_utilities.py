import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

STATES = {
    "Alabama": 1, "Alaska": 2, "Arizona": 4, "Arkansas": 5, "California": 6,
    "Colorado": 8, "Connecticut": 9, "Delaware": 10, "Florida": 12, "Georgia": 13,
    "Hawaii": 15, "Idaho": 16, "Illinois": 17, "Indiana": 18, "Iowa": 19,
    "Kansas": 20, "Kentucky": 21, "Louisiana": 22, "Maine": 23, "Maryland": 24,
    "Massachusetts": 25, "Michigan": 26, "Minnesota": 27, "Mississippi": 28,
    "Missouri": 29, "Montana": 30, "Nebraska": 31, "Nevada": 32,
    "New Hampshire": 33, "New Jersey": 34, "New Mexico": 35, "New York": 36,
    "North Carolina": 37, "North Dakota": 38, "Ohio": 39, "Oklahoma": 40,
    "Oregon": 41, "Pennsylvania": 42, "Rhode Island": 44, "South Carolina": 45,
    "South Dakota": 46, "Tennessee": 47, "Texas": 48, "Utah": 49, "Vermont": 50,
    "Virginia": 51, "Washington": 53, "West Virginia": 54, "Wisconsin": 55,
    "Wyoming": 56,
}


@st.cache_resource
def get_bigquery_client() -> bigquery.Client:
    """Connect to BigQuery using credentials in Streamlit Secrets."""
    credentials = service_account.Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"])
    )
    return bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )


@st.cache_data(ttl=600)
def run_query(
    sql: str, parameters: dict[str, str | int] | None = None
) -> pd.DataFrame:
    """Run SQL and cache the resulting DataFrame for ten minutes."""
    job_config = bigquery.QueryJobConfig(
        maximum_bytes_billed=2_000_000_000,  # Limit each query to 2 GB.
        query_parameters=[
            bigquery.ScalarQueryParameter(
                name, "INT64" if isinstance(value, int) else "STRING", value
            )
            for name, value in (parameters or {}).items()
        ],
    )
    job = get_bigquery_client().query(sql, job_config=job_config)
    return job.result().to_dataframe(create_bqstorage_client=False)


def get_species_names() -> list[str]:
    """Load available common names for the species dropdown."""
    sql = """
    SELECT DISTINCT TRIM(species_common_name) AS species
    FROM `bigquery-public-data.usfs_fia.tree`
    WHERE species_common_name IS NOT NULL
        AND TRIM(species_common_name) != ''
    ORDER BY species
    """
    return run_query(sql)["species"].tolist()


def get_forest_data() -> pd.DataFrame:
    """Load up to 1,000 tree records from plots with water present, 1968-2020."""
    sql = """
    SELECT
        -- Plot location and temporal data
        p.plot_sequence_number AS plot_id,
        p.plot_state_code AS state_code,
        p.latitude,
        p.longitude,
        p.elevation,
        p.plot_inventory_year AS inventory_year,
        p.water_on_plot_code AS water_proximity,

        -- Land condition data
        c.condition_status_code AS land_condition_status,

        -- Individual tree metrics
        t.tree_sequence_number AS tree_id,
        t.tree_status_code AS tree_status_alive_or_dead,
        t.total_height AS tree_height,
        t.current_diameter AS tree_diameter,

        -- Species data
        t.species_code,
        t.species_common_name,
        t.species_scientific_name
    FROM
        `bigquery-public-data.usfs_fia.plot` AS p
    JOIN
        `bigquery-public-data.usfs_fia.condition` AS c
        ON p.plot_sequence_number = c.plot_sequence_number
    JOIN
        `bigquery-public-data.usfs_fia.tree` AS t
        ON p.plot_sequence_number = t.plot_sequence_number
        AND c.condition_class_number = t.condition_class_number
    WHERE
        p.plot_inventory_year BETWEEN 1968 AND 2020
        -- Only include plots where water is present.
        AND p.water_on_plot_code > 0
    LIMIT 1000;
    """
    return run_query(sql)


def get_species_density(state_code: int, species: str) -> pd.DataFrame:
    """Count recorded trees by plot location for a selected species."""
    sql = """
    SELECT p.latitude, p.longitude, COUNT(*) AS tree_count
    FROM `bigquery-public-data.usfs_fia.plot` AS p
    JOIN `bigquery-public-data.usfs_fia.tree` AS t
        ON p.plot_sequence_number = t.plot_sequence_number
    WHERE p.plot_state_code = @state
        AND p.plot_inventory_year >= 2000
        AND LOWER(t.species_common_name) = LOWER(@species)
        AND p.latitude BETWEEN -90 AND 90
        AND p.longitude BETWEEN -180 AND 180
    GROUP BY p.latitude, p.longitude
    """
    return run_query(sql, {"state": state_code, "species": species.strip()})


def get_water_and_shade(state_code: int, minimum_height: int) -> pd.DataFrame:
    """Find plots reporting water and living trees above the requested height."""
    sql = """
    SELECT
        p.latitude, p.longitude,
        COUNT(*) AS tree_count,
        AVG(t.total_height) AS average_height_ft
    FROM `bigquery-public-data.usfs_fia.plot` AS p
    JOIN `bigquery-public-data.usfs_fia.tree` AS t
        ON p.plot_sequence_number = t.plot_sequence_number
    WHERE p.plot_state_code = @state
        AND p.plot_inventory_year >= 2000
        AND p.water_on_plot_code > 0
        AND t.tree_status_code = 1
        AND t.total_height >= @minimum_height
        AND p.latitude BETWEEN -90 AND 90
        AND p.longitude BETWEEN -180 AND 180
    GROUP BY p.latitude, p.longitude
    """
    return run_query(sql, {"state": state_code, "minimum_height": minimum_height})


def get_state_health(state_code: int) -> pd.DataFrame:
    """Summarize historical tree observations, not statewide population estimates."""
    sql = """
    SELECT
        COUNT(*) AS total_trees,
        COUNT(DISTINCT p.plot_sequence_number) AS plot_surveys,
        AVG(t.total_height) AS average_height_ft,
        COUNTIF(t.tree_status_code = 1) AS living_trees,
        COUNTIF(t.tree_status_code = 2) AS dead_trees,
        COUNTIF(t.tree_status_code IS NULL OR t.tree_status_code NOT IN (1, 2))
            AS other_trees,
        MIN(p.plot_inventory_year) AS first_year,
        MAX(p.plot_inventory_year) AS last_year
    FROM `bigquery-public-data.usfs_fia.plot` AS p
    JOIN `bigquery-public-data.usfs_fia.tree` AS t
        ON p.plot_sequence_number = t.plot_sequence_number
    WHERE p.plot_state_code = @state
        AND p.plot_inventory_year >= 2000
    """
    return run_query(sql, {"state": state_code})