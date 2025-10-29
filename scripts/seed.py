# Simple seed script to add a few example links
from app import db, crud
db.init_db()
examples = [
    ("Example Product 1", "https://example.com/product1"),
    ("Example Product 2", "https://example.com/product2"),
    ("Learn FastAPI", "https://fastapi.tiangolo.com/")
]
for t,u in examples:
    print("Creating", t)
    crud.create_link(t,u)
print("Seed complete")
