# BANGSAFE — The National CyberShield (GitHub-ready)

This repository is a GitHub-ready demo for **BANGSAFE**, a Bangladesh-focused cyber safety site.
It's a lightweight FastAPI backend + dark-mode frontend (Bangla + English mix).

## Quick steps (mobile-friendly)
1. Download this ZIP and upload files to a new GitHub repository (Upload files -> choose files).
2. Deploy backend (FastAPI) on Render / Heroku / any host:
   - Start command (if using Render with working dir backend): `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3. Deploy frontend as static site:
   - Netlify / GitHub Pages / Vercel → set publish directory to `frontend` (or place frontend files at repo root)
4. In the frontend open the site, set the Backend URL (top-right input) to your deployed backend URL (example: https://your-backend.onrender.com) and press Save.
5. Now use SCAN and Report features.

## Notes
- This is a demo. For production add database, authentication, rate-limiting, and moderation.
- Do not publish PII.
