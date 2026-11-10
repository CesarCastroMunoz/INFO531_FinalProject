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
