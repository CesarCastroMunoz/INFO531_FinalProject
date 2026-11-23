# INFO531

Forest Explorer is a Streamlit app for exploring US Forest Inventory and
Analysis (FIA) observations stored in the BigQuery public dataset
`bigquery-public-data.usfs_fia`. This guide covers running it locally on
Windows PowerShell.

## Prerequisites

- Python 3.12
- A Google Cloud project with the **BigQuery API** enabled
- A service account with **BigQuery Job User** on your project and
  **BigQuery Data Viewer** on the datasets you need. Download its JSON key
  somewhere outside this repository.

## 1. Install dependencies

From the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Configure BigQuery credentials

1. Copy the secrets template:

   ```powershell
   Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```

2. Replace the placeholders in `.streamlit\secrets.toml` with values from the
   JSON key. Keep the private key's `\n` escapes. **Never commit the key or the
   populated secrets file.**

## 3. Run the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal (normally http://localhost:8501).
Press Ctrl+C to stop the server. These commands do not require activating the
environment or changing PowerShell's execution policy. Restart the app if you
change credentials.

In VS Code, use **Python: Select Interpreter** and choose
`.venv\Scripts\python.exe` if the environment is not already selected.

## Project structure

- [streamlit_app.py](streamlit_app.py): the user interface.
- [st_utilities.py](st_utilities.py): BigQuery connection and SQL queries.
- [requirements.txt](requirements.txt): Python dependencies.

Each query is limited to **2 GB billed** and its results are cached for ten
minutes. BigQuery can still charge for repeated queries, and `LIMIT` does not
cap bytes scanned.

## Forest Explorer interface

The species dropdown loads distinct, nonblank common names from BigQuery when
the page opens, using the existing ten-minute query cache. The three tabs run
their analysis queries when their form button is clicked:

- **Species density:** choose a state and a species from the database.
  A heatmap weights each plot location by its recorded tree count.
- **Water and shade:** select a state and minimum tree height in feet.
  The map shows plots reporting water and living trees meeting the height filter.
- **State forest health:** select a state to see average height, observation
  counts, observations per plot survey, and living/dead shares. Other/unknown
  tree status is counted separately.

These features include inventory years **2000 onward**, through the latest
available data. They count historical observations, including repeat surveys,
not unique living trees today or estimated trees per acre.

Coordinates are approximate for privacy. Water codes do not measure distance
to a lake or stream, and tall trees do not guarantee shade. These maps are for
education, not navigation or verified campsite recommendations.
