# Affiliate Link Manager (FastAPI)

Simple, beginner-friendly FastAPI project to manage affiliate links for your site **affiliatemath.xyz**.

Features:
- Add / edit / delete affiliate links (admin-protected by an API key).
- Public listing page of links.
- Short redirect route `/r/{slug}` that logs clicks and redirects to the affiliate URL.
- SQLite database stored at `data/affiliate.db`.
- Jinja2 templates for a minimal web UI.
- Dockerfile and requirements.txt for quick deployment.

## Quick start (local)
1. Create a virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Set an admin key (default is `changeme`):
   ```bash
   export ADMIN_KEY="your-secret-key"
   ```
3. Run:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open `http://127.0.0.1:8000/` to see public link listing.
   Admin dashboard: `http://127.0.0.1:8000/admin` (you'll send the ADMIN_KEY via the form).

## Deploy notes
- Use the provided `Dockerfile` to build a container and push to GHCR.
- Ensure environment variable `ADMIN_KEY` is set in your deployment.

## Security notes
- This project uses a simple API-key approach for demonstration. For production, set a strong `ADMIN_KEY` and consider authenticating users with OAuth or username/password and HTTPS.
