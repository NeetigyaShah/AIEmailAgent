# Deployment Guide & Security Overview

## 🔒 Security Audit

We have performed a security review of the application and implemented the following safeguards:

1.  **HTML Sanitization**:
    *   Email bodies are rendered using `streamlit.components.v1.html`, which uses a sandboxed iframe. This prevents malicious emails (XSS attacks) from executing scripts in your browser.
    *   Where manual HTML is used (e.g., for styling cards), all dynamic content is strictly escaped using `html.escape()`.

2.  **Secret Management**:
    *   **API Keys**: The app does NOT hardcode API keys. It uses `os.environ` or prompts the user in the UI.
    *   **OAuth Credentials**: `client_secret.json` is required for Gmail OAuth but is listed in `.gitignore` to prevent accidental leaks to GitHub.
    *   **Recommendation**: Never commit `.env` or `client_secret.json` files.

3.  **Dependencies**:
    *   All necessary libraries are pinned in `requirements.txt`.

## 🚀 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended for Demos)
This is the easiest and free way to host, but **data will be reset** when the app restarts because SQLite is file-based.

1.  **Push to GitHub**: Ensure your code is in a GitHub repository (we just did this!).
2.  **Sign Up**: Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3.  **Deploy**:
    *   Click "New app".
    *   Select your repository (`AIEmailAgent`) and branch (`main`).
    *   Main file path: `app.py`.
    *   Click **Deploy**.
4.  **Secrets**:
    *   Go to your App Settings -> Secrets.
    *   Add your `GOOGLE_API_KEY` there if you want it pre-loaded:
        ```toml
        GOOGLE_API_KEY = "your-key-here"
        ```

### Option 2: Render / Railway (Recommended for Persistence)
If you want your database to survive restarts, you need a platform that supports persistent disks or a separate database service.

**Deploying on Render:**
1.  Create a new **Web Service** connected to your GitHub repo.
2.  **Build Command**: `pip install -r requirements.txt`
3.  **Start Command**: `streamlit run app.py --server.port $PORT`
4.  **Environment Variables**: Add `PYTHON_VERSION` = `3.9` (or newer).
5.  **Persistent Disk (Paid)**: To keep `email_agent.db`, you must add a "Disk" in Render settings and mount it to `/data`. You would then need to update `db_utils.py` to save the DB in `/data/email_agent.db`.

### ⚠️ Important Note on Database
This app currently uses **SQLite** (`email_agent.db`), which is a file stored on the disk.
*   **Streamlit Cloud**: The disk is ephemeral. If the app goes to sleep, **your emails and settings will be deleted**.
*   **Production Fix**: For a real production app, you should switch from SQLite to a cloud database like **Supabase (PostgreSQL)** or **Neon**. This would require changing `src/db_utils.py` to use `psycopg2` or `sqlalchemy` instead of `sqlite3`.
