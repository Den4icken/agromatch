# Deploy the FULL AgroMatch application for free on Render

Netlify Drop serves static HTML, CSS and JavaScript. The original AgroMatch also
requires Python FastAPI endpoints, a SQLite database and WebSocket connections;
therefore a ZIP alone cannot make the full app run on Netlify Drop.

## Publish on Render (full app, one URL)

1. Unzip `AgroMatch_Render_Full_NoSecrets.zip`.
2. Create a GitHub repository. Upload **the content of this folder to the repository root**
   (so `render.yaml`, `backend/`, `frontend/` are at root), not the parent ZIP folder.
   Do not commit your private `.env`, database or keys.
3. Visit https://dashboard.render.com/ and sign in; connect GitHub.
4. Choose **New > Blueprint**, then select the repository. The included
   `render.yaml` specifies a free Python Web Service, install and start commands.
   Alternatively, create **New > Web Service**, choose **Free** and use:
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn main:app --app-dir backend --host 0.0.0.0 --port $PORT`
   - Environment: `DATABASE_PATH=storage/agromatch.db`
5. Deploy. When ready, open your `https://<chosen-name>.onrender.com` URL.
   AgroMatch's FastAPI server serves both frontend and backend on the same origin.
6. In the public application, create a demonstration account and farm/field. Only
   enter synthetic/demo personal information for now.

## Configuring optional AI / NASA credentials

In Render > Web Service > Environment, set keys such as `AI_PRIMARY_API_KEY`
and (optional) `AI_BACKUP_API_KEY`. Add other variables from `.env.example` as
needed. Never put secrets in JavaScript, public GitHub repos or deployment ZIPs.
Previously supplied `backend/.env` **was deliberately excluded** from this ZIP.
Because the provided ZIP contained a populated credential, rotate/revoke that
credential if it has been exposed to an untrusted party or public repository.

## IMPORTANT: Render Free is not persistent

Render Free services spin down after about 15 minutes of inactivity. Files on the
free instance are EPHEMERAL, including local SQLite DB and generated audio. User
accounts, farms, matches, conversations and exported local data may be lost on
restart / redeploy / spin-down. This is only suitable for short-lived
presentations and demos, NOT a production site or permanent multi-user community.
A production deployment needs a persistent database (e.g. PostgreSQL), persistent
file storage, stronger privacy/security controls and backups. The supplied
application is currently written for SQLite and cannot be switched to Postgres
just by changing an environment variable.

Security note: The prototype is not hardened for public deployment; add rate
limiting, abuse controls, account management, better sessions and privacy notice
before collecting real farmer information. The sample database from the original
upload was excluded because it contained a user and session data.

## Local test

    python -m venv .venv
    pip install -r backend/requirements.txt
    uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000

Open http://127.0.0.1:8000 (not the Netlify site).

## Sources
- https://render.com/docs/free
- https://render.com/docs/your-first-deploy
- https://docs.netlify.com/start/quickstarts/netlify-drop-quickstart/
