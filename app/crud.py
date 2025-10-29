import random
import string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from .db import SessionLocal, Link, Click


# =========================================================
# Utility: Safe Slug Generator
# =========================================================
def _make_slug(text: str) -> str:
    """Generate a clean slug from text or fallback to random."""
    s = ''.join(c for c in (text or "") if c.isalnum()).lower()
    if len(s) < 3:
        s += ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return s[:60]


# =========================================================
# CRUD: Get All Links
# =========================================================
def get_all_links():
    """Return all links with click counts."""
    db = SessionLocal()
    try:
        rows = db.query(Link).options(joinedload(Link.clicks)).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "url": r.url,
                "slug": r.slug,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "clicks": len(r.clicks),
            }
            for r in rows
        ]
    finally:
        db.close()


# =========================================================
# CRUD: Get Link by Slug
# =========================================================
def get_link_by_slug(slug: str):
    """Return one link dictionary by its slug."""
    db = SessionLocal()
    try:
        r = db.query(Link).filter(Link.slug == slug).first()
        if not r:
            return None
        return {
            "id": r.id,
            "title": r.title,
            "url": r.url,
            "slug": r.slug,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
    finally:
        db.close()


# =========================================================
# CRUD: Create Link
# =========================================================
def create_link(title: str, url: str, slug: str = None):
    """Create and return a new link, ensuring slug uniqueness."""
    db = SessionLocal()
    try:
        if not slug:
            slug = _make_slug(title)

        # Ensure slug uniqueness
        existing = db.query(Link).filter(Link.slug == slug).first()
        if existing:
            slug += "-" + ''.join(random.choices(string.digits, k=3))

        obj = Link(title=title.strip(), url=url.strip(), slug=slug.strip())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "id": obj.id,
            "title": obj.title,
            "url": obj.url,
            "slug": obj.slug,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
        }

    except IntegrityError:
        db.rollback()
        slug = _make_slug(title) + "-" + ''.join(random.choices(string.digits, k=4))
        obj = Link(title=title, url=url, slug=slug)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return {
            "id": obj.id,
            "title": obj.title,
            "url": obj.url,
            "slug": obj.slug,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
        }
    finally:
        db.close()


# =========================================================
# CRUD: Update Link
# =========================================================
def update_link(link_id: int, title: str, url: str, slug: str = None):
    """Update a link’s details."""
    db = SessionLocal()
    try:
        obj = db.query(Link).filter(Link.id == link_id).first()
        if not obj:
            return None

        obj.title = title.strip()
        obj.url = url.strip()
        if slug:
            obj.slug = slug.strip()

        db.commit()
        db.refresh(obj)
        return {
            "id": obj.id,
            "title": obj.title,
            "url": obj.url,
            "slug": obj.slug,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
        }
    finally:
        db.close()


# =========================================================
# CRUD: Delete Link
# =========================================================
def delete_link(link_id: int):
    """Delete a link (and cascade clicks)."""
    db = SessionLocal()
    try:
        obj = db.query(Link).filter(Link.id == link_id).first()
        if not obj:
            return False

        db.delete(obj)
        db.commit()
        return True
    finally:
        db.close()


# =========================================================
# LOG: Record Click
# =========================================================
def log_click(link_id: int, ip: str):
    """Log a click on a link."""
    db = SessionLocal()
    try:
        click = Click(link_id=link_id, ip=ip)
        db.add(click)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Click logging failed: {e}")
    finally:
        db.close()
