from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import get_db, Category, SparePart, Sale

app = FastAPI()

# Allow all CORS requests (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Root Route
# -------------------------
@app.get("/")
def home():
    return {"message": "Ismail Auto Spares API is running 🚗"}

# -------------------------
# CATEGORY ROUTES
# -------------------------
class CategorySchema(BaseModel):
    name: str

@app.post("/category")
def create_category(category: CategorySchema, db=Depends(get_db)):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        return {"message": "Category already exists"}
    new_cat = Category(name=category.name)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat  # return the created category with ID

@app.get("/categories")  # <-- changed to match frontend
def get_categories(db=Depends(get_db)):
    return db.query(Category).all()

# -------------------------
# SPARE PART ROUTES
# -------------------------
class SparePartSchema(BaseModel):
    name: str
    price: int
    stock: int
    category_id: int

@app.post("/part")  # <-- changed to match frontend
def create_spare_part(part: SparePartSchema, db=Depends(get_db)):
    new_part = SparePart(
        name=part.name,
        price=part.price,
        stock=part.stock,
        category_id=part.category_id
    )
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    return new_part

@app.get("/parts")  # <-- changed to match frontend
def get_spare_parts(db=Depends(get_db)):
    parts = db.query(SparePart).all()
    # Include category name in response for frontend
    result = []
    for p in parts:
        result.append({
            "id": p.id,
            "name": p.name,
            "category": p.category.name if p.category else "Unknown"
        })
    return result

# -------------------------
# SALE ROUTES
# -------------------------
class SaleSchema(BaseModel):
    part_id: int  # match frontend
    qty: int      # match frontend

@app.post("/sale")
def create_sale(sale: SaleSchema, db=Depends(get_db)):
    new_sale = Sale(
        spare_part_id=sale.part_id,
        quantity=sale.qty
    )
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale

@app.get("/sales")  # <-- changed to match frontend
def get_sales(db=Depends(get_db)):
    sales = db.query(Sale).all()
    result = []
    for s in sales:
        result.append({
            "id": s.id,
            "part_id": s.spare_part_id,
            "qty": s.quantity
        })
    return result
