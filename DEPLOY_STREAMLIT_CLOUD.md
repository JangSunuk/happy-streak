# Deploy to Streamlit Community Cloud

## 1) Prepare repo (GitHub)

From local project:

```bash
cd /home/sunuk/code/happy-streak
git init
git add .
git commit -m "init happy-streak streamlit"
```

Create a new GitHub repo, then:

```bash
git remote add origin <YOUR_GITHUB_REPO_URL>
git branch -M main
git push -u origin main
```

## 2) Connect Streamlit Cloud

1. Go to `https://share.streamlit.io`
2. Sign in with GitHub.
3. Connect GitHub repository access.

## 3) Create app

1. Click `Create app`.
2. Choose:
   - Repository: your repo
   - Branch: `main`
   - Main file path: `streamlit_app.py`
3. (Optional) Advanced settings:
   - Python version (if needed)
   - Secrets (not needed for current local-only app)
4. Click `Deploy`.

## 4) Result

After build completes, a URL like below is issued:

`https://<generated-subdomain>.streamlit.app`

## 5) Important notes

- `requirements.txt` is included for dependency installation.
- `data.json` is local file storage. On Community Cloud, storage is ephemeral (can reset on restart/redeploy).
- If you need persistent storage later, move data to external DB/object storage.
