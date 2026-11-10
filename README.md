# INFO531

A Python 3.12 app ready for Streamlit Community Cloud.

## Local setup (Windows PowerShell)

The initial environment is already installed in `.venv`. On a fresh clone,
run these commands from the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Open the local URL printed in the terminal (normally http://localhost:8501).
Press Ctrl+C to stop the server. These commands do not require activating the
environment or changing PowerShell's execution policy.

In VS Code, use **Python: Select Interpreter** and choose
`.venv\Scripts\python.exe` if the environment is not already selected.

Edit [streamlit_app.py](streamlit_app.py) to build your page. Add any additional
third-party packages your app imports to [requirements.txt](requirements.txt),
then rerun the install command.

## Push to GitHub

This project is connected to
https://github.com/CesarCastroMunoz/INFO531_FinalProject.
From this project folder, commit and push changes with:

```powershell
git add .
git commit -m "Describe your changes"
git push -u origin main
```

The local Git repository has already been initialized on `main` with the
GitHub repository configured as `origin`.
Review `git status` before committing. Do not upload `.venv` or secrets.

## Deploy for free on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ and connect your GitHub account.
2. Click **Create app**, then **Yup, I have an app**.
3. Select `CesarCastroMunoz/INFO531_FinalProject` and the `main` branch.
4. Set the main file path to `streamlit_app.py`.
5. In **Advanced settings**, choose **Python 3.12** to match local development.
6. Click **Deploy**.

Community Cloud installs packages from `requirements.txt`; it does not use your
local `.venv`. Push future changes to the same GitHub branch to update the app.

For API keys or credentials, use `.streamlit/secrets.toml` locally and paste its
contents into the app's Community Cloud **Secrets** settings. The local secrets
file is ignored by Git. Never put secrets in your Python code.

Official deployment guide:
https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## BigQuery connection and SQL extraction

1. Enable the **BigQuery API** in your Google Cloud project.
2. Create a service account with **BigQuery Job User** on your project and
   **BigQuery Data Viewer** on the datasets you need. Download its JSON key
   somewhere outside this repository.
3. Copy the secrets template:

   ```powershell
   Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```

4. Replace the placeholders with values from the JSON key. Keep the private
   key's `\n` escapes. **Never commit the key or populated secrets file.**
5. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

6. For deployment, paste the populated TOML into your Streamlit app's
   **Secrets** settings. Restart the app if you change credentials.

SQL and data loading live in [st_utilities.py](st_utilities.py).
[streamlit_app.py](streamlit_app.py) calls the helper and displays the results:

```python
from st_utilities import get_forest_data

data = get_forest_data()
st.dataframe(data, hide_index=True)
```

`get_bigquery_client()` connects; `run_query(sql)` returns a pandas DataFrame.
Results are cached for ten minutes and shared across viewers, so use only data
all viewers may see. Keep SQL in your code; do not insert user input into SQL.
Errors are raised normally.

Each query has a **2 GB billing limit**. BigQuery can still charge for repeated
queries even though Streamlit hosting is free. `LIMIT` does not cap bytes scanned.
The forest query returns up to 1,000 records with all 15 original columns,
joining the plot, condition, and tree tables with the original year and water
filters.

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
not unique living trees today or estimated trees per acre. The original
`get_forest_data()` test query remains available separately.

Coordinates are approximate for privacy. Water codes do not measure distance
to a lake or stream, and tall trees do not guarantee shade. These maps are for
education, not navigation or verified campsite recommendations.
