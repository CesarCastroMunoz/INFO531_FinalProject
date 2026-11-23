# Forest Explorer: Final Project Report

**Course:** INFO 531  
**Project option:** Option 1 — UI/Dashboard  
**Student:** [Add your name]  
**Date:** [Add submission date]

## 1. Problem statement

Forest inventory information is collected across many survey plots and can be difficult to explore without querying the underlying data directly. This project addresses the problem by providing an interactive dashboard for exploring U.S. Forest Inventory and Analysis (FIA) observations by state. Users can inspect the recorded distribution of a selected tree species, find plots that report water and trees meeting a height threshold, and review descriptive tree-observation statistics for a state.

The dashboard is intended for educational exploration of historical survey observations, not for estimating current statewide tree populations, identifying exact tree locations, diagnosing forest health, or recommending campsites. FIA surveys can record the same trees or plots across multiple visits, and plot coordinates are approximate for privacy.

## 2. Project requirements and development phases

### 2.1 Update 1 — [add the required Update 1 heading]

**[Complete this section with the actual Update 1 requirements and work.]** The project source currently available for this draft contains the working dashboard and its BigQuery query helpers, but does not include the Update 1 assignment prompt, submitted work, or planning document. Add the specific Update 1 requirements, decisions, and completed work here so that the final report includes the earlier project phase without claiming details that are not in the code.

### 2.2 Update 2 — [add the required Update 2 heading]

**[Complete this section with the actual Update 2 heading and work.]** The Update 2 assignment prompt and submission are also not present in the available project files. Insert the exact Update 2 requirements and summarize what was completed, including any data exploration, analysis, or design work that preceded the dashboard.

### 2.3 Option 1 dashboard implementation

The dashboard is implemented in Python with Streamlit. Its data-access and query functions are in `st_utilities.py`; `streamlit_app.py` creates the user interface and renders query results. The interface contains three tabs: **Species density**, **Water and shade**, and **State forest health**. Each analysis is submitted through a form so that its query is run when the user requests results.

## 3. Data preparation for UI/report development

### 3.1 Data source and access

The dashboard queries the U.S. Forest Service FIA public tables hosted in Google BigQuery. The code refers to these fully qualified tables:

- `bigquery-public-data.usfs_fia.plot` — plot location, state, inventory year, elevation, and water-on-plot information.
- `bigquery-public-data.usfs_fia.tree` — tree status, height, diameter, species identifiers, and species names.

**Data-source links:** [USFS FIA DataMart](https://research.fs.usda.gov/products/dataandtools/fia-datamart) is the Forest Service's FIA data portal, and [Google Cloud BigQuery public datasets](https://cloud.google.com/bigquery/public-data) describes access to BigQuery public datasets. This project queries the BigQuery dataset `bigquery-public-data.usfs_fia`, specifically its `plot` and `tree` tables. No standalone CSV is stored with the project. These source links and table identifiers are provided instead of an uploaded CSV.

The app connects to BigQuery using a Google Cloud service account configured through Streamlit Secrets. Credentials are configuration, not part of the dataset, and should not be included in the report or repository.

### 3.2 Preparation and filtering performed by the application

The dashboard prepares the data at query time rather than loading and cleaning a local CSV:

- A distinct, sorted list of nonblank common species names is queried to populate the species selector.
- The state selector uses state names mapped to FIA state codes.
- The three dashboard analyses filter to inventory years from 2000 onward.
- The species and water/shade queries reject coordinates outside valid latitude and longitude ranges and aggregate observations by plot coordinates.
- Species matching is case-insensitive, and the selected species and state are passed as BigQuery query parameters.
- The water/shade query selects plots where water is reported and includes only living trees (`tree_status_code = 1`) whose recorded height meets the selected minimum.
- The state summary classifies observations as living, dead, or other/unknown; its average height is calculated from available height values.

Query results are converted to pandas DataFrames. The BigQuery client is cached as a Streamlit resource, and query results are cached for ten minutes. Each query has a 2 GB maximum billed-bytes setting. These controls limit repeated work and query cost; they do not produce a downloadable CSV or guarantee that all possible queries will finish within that billing limit.

## 4. Underlying data model

The dashboard uses FIA plot and tree observations as a relational model. A plot is identified by `plot_sequence_number`; tree observations are joined to plots using that identifier. The dashboard analyses use the plot and tree tables:

| Entity/table | Role in the dashboard |
|---|---|
| Plot | Supplies the state code, inventory year, approximate latitude and longitude, and water-on-plot code. |
| Tree | Supplies individual recorded tree observations, including species name, tree status, and total height. |

The model has two useful analytical grains:

1. **Observation-level records** are joined from plot and tree data. These are survey observations and may include repeated measurements over time.
2. **Coordinate-level aggregates** group selected observations by latitude and longitude. Species counts and water/shade results are summarized at this level for mapping.

For the state-health tab, one aggregate row is returned for the selected state. It contains total tree observations, distinct plot surveys, average recorded height, living/dead/other observation counts, and the earliest/latest inventory years in the queried data.

These are descriptive summaries of the records returned by the FIA tables. In particular, the total is not a count of unique trees, the number per plot survey is not a trees-per-acre estimate, and the status proportions are not a formal forest-health assessment.

## 5. Data visualization and analysis

### 5.1 Species density

The user selects a state and a species. The dashboard displays the sum of matching recorded observations and a PyDeck heatmap, weighted by `tree_count`, with a table of the aggregated coordinates and counts. Warmer heatmap areas indicate more recorded observations at nearby mapped locations. Because the input counts are historical records and may include repeat surveys, the visualization represents recorded observations rather than the number of unique trees currently present.

### 5.2 Water and shade exploration

The user selects a state and a minimum tree height, from 5 to 200 feet. The dashboard displays the number of matching mapped locations, a scatterplot map, and a table of results. The underlying query looks for plots reporting water and living trees at or above the selected height; it also returns the count of qualifying trees and their average height for each coordinate.

This view is an exploratory filter, not a campsite recommendation. The water value is reported for the plot and does not provide distance to a lake or stream. Tree height alone does not establish that a location has shade. Users are cautioned to verify current conditions, land access, and camping rules.

### 5.3 State forest-health summary

For a selected state, the dashboard reports the inventory year range, total recorded tree observations, average tree height when available, and observations per distinct plot survey. A bar chart compares living, dead, and other/unknown observations. Separate metrics show living and dead shares; the denominator for both shares is all observations, including other/unknown status.

The labels and explanatory text frame these measures as descriptive statistics. They should not be interpreted as a diagnosis of forest health or as estimates of the current number of living trees in the state.

### 5.4 Interpretation and limitations

The application reports no specific statewide findings in this draft because results depend on the state, species, and query results selected at runtime. The dashboard provides an interface for users to examine those results rather than a fixed analysis of one selected state.

Important limitations include repeat observations across surveys, approximate FIA plot coordinates, missing height or status values, and the difference between plot-level reports and real-world distance or site conditions. The app notes that mapped locations are unsuitable for navigation to individual trees. A result table or screenshot for a selected state can be added here after running the dashboard, with the selected filters and date of access recorded.

## 6. Conclusion

This project turns public FIA data into an interactive state-level dashboard. It supports exploration of species observation patterns, plots reporting water and tall living trees, and descriptive tree-observation summaries. Its query-time preparation, relational joins, parameterized filters, aggregation, and visual encodings connect the underlying survey data to the questions exposed in the interface.

The dashboard is most useful when its results are interpreted as historical survey observations rather than direct measurements of current statewide forest conditions. Repeat surveys, approximate coordinates, and the distinction between reported plot conditions and on-the-ground conditions all limit what can be concluded. The following two paragraphs summarize the project as required.

## Summary

The project developed Forest Explorer, a Streamlit dashboard for exploring U.S. Forest Service FIA observations stored in BigQuery. The dashboard prepares data through SQL filtering and aggregation and provides three views: a species-weighted heatmap, a water-and-height plot map, and state-level summaries of tree observations. State and species filters, a minimum-height control, query-result caching, and a per-query scan limit support interactive use.

The dashboard presents historical observation patterns, not counts of unique current trees, trees per acre, precise tree locations, or a formal forest-health diagnosis. Its results are limited by repeat survey records, approximate coordinates, and the meaning and completeness of reported plot and tree attributes. The source data is publicly available through the Google Cloud BigQuery public dataset `bigquery-public-data.usfs_fia`; no separate CSV is included with the project.
