from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import string, random, os

# Import internal modules
from .db import get_db, init_db, Link, Click, DB_PATH

# --------------------------------
# App Initialization
# --------------------------------
app = FastAPI(title="Affiliate Link Manager 🚀")

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static directory if available
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Setup Jinja templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# --------------------------------
# Utility: Generate Random Slug
# --------------------------------
def generate_slug(length: int = 6) -> str:
    """Generate a random short slug."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# --------------------------------
# Startup Event (initialize DB)
# --------------------------------
@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()
    print(f"✅ Database initialized at: {DB_PATH}")
    print(f"📂 Working directory: {os.getcwd()}")


# --------------------------------
# Home Page (index.html)
# --------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


# --------------------------------
# Admin Dashboard (View All Links)
# --------------------------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """View all affiliate links."""
    links = db.query(Link).order_by(Link.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "links": links, "total_links": len(links)}
    )


# --------------------------------
# Add New Link (Form POST)
# --------------------------------
@app.post("/links", response_class=RedirectResponse)
def create_link(
    title: str = Form(...),
    url: str = Form(...),
    slug: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new affiliate link entry."""
    if not slug:
        slug = generate_slug()

    # Ensure unique slug
    existing = db.query(Link).filter(Link.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    new_link = Link(title=title.strip(), url=url.strip(), slug=slug.strip())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    print(f"✅ Added new link: {new_link.title} (slug={new_link.slug})")
    return RedirectResponse(url="/admin", status_code=303)


# --------------------------------
# API: Fetch All Links (JSON)
# --------------------------------
@app.get("/links")
def get_all_links(db: Session = Depends(get_db)):
    """Return all links as JSON."""
    links = db.query(Link).order_by(Link.created_at.desc()).all()
    return [
        {
            "id": link.id,
            "title": link.title,
            "url": link.url,
            "slug": link.slug,
            "created_at": link.created_at.isoformat(),
            "clicks": len(link.clicks)
        }
        for link in links
    ]


# --------------------------------
# API: Delete a Link
# --------------------------------
@app.delete("/links/{link_id}")
def delete_link(link_id: int, db: Session = Depends(get_db)):
    """Delete a link by its ID."""
    link = db.query(Link).filter(Link.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(link)
    db.commit()
    print(f"🗑 Deleted link: ID={link_id}")
    return {"message": "Link deleted successfully"}


# --------------------------------
# Redirect + Click Tracking
# --------------------------------
@app.get("/{slug}")
def redirect_slug(slug: str, request: Request, db: Session = Depends(get_db)):
    """Redirect user and log a click."""
    link = db.query(Link).filter(Link.slug == slug).first()
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")

    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    click = Click(link_id=link.id, ip=ip)
    db.add(click)
    db.commit()

    print(f"➡️ Redirect: {slug} → {link.url} (from {ip})")
    return RedirectResponse(url=str(link.url))
