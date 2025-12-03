from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import get_db, Category, SparePart, Sale

app = FastAPI()

# Allow all CORS requests (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
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
    return {"message": "Category created successfully"}

@app.get("/category")
def get_categories(db=Depends(get_db)):
    return db.query(Category).all()

# DELETE route to remove a category
@app.delete("/category/{category_id}")
def delete_category(category_id: int, db=Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return {"message": f"Category ID {category_id} does not exist"}
    
    # Optional: prevent deletion if there are spare parts linked
    linked_parts = db.query(SparePart).filter(SparePart.category_id == category_id).all()
    if linked_parts:
        return {"message": f"Cannot delete Category ID {category_id} because it has spare parts linked"}

    db.delete(category)
    db.commit()
    return {"message": f"Category ID {category_id} deleted successfully"}


# -------------------------
# SPARE PART ROUTES
# -------------------------
class SparePartSchema(BaseModel):
    name: str
    price: int
    stock: int
    category_id: int

@app.post("/sparepart")
def create_spare_part(part: SparePartSchema, db=Depends(get_db)):
    new_part = SparePart(
        name=part.name,
        price=part.price,
        stock=part.stock,
        category_id=part.category_id
    )
    db.add(new_part)
    db.commit()
    return {"message": "Spare part added successfully"}

@app.get("/sparepart")
def get_spare_parts(db=Depends(get_db)):
    return db.query(SparePart).all()

# PATCH route to update category of a spare part
@app.patch("/sparepart/{sparepart_id}/category")
def update_spare_part_category(sparepart_id: int, new_category_id: int, db=Depends(get_db)):
    part = db.query(SparePart).filter(SparePart.id == sparepart_id).first()
    if not part:
        raise HTTPException(status_code=404, detail=f"Spare part ID {sparepart_id} not found")
    
    category = db.query(Category).filter(Category.id == new_category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category ID {new_category_id} not found")
    
    part.category_id = new_category_id
    db.commit()
    
    return {"message": f"Spare part ID {sparepart_id} updated to Category ID {new_category_id}"}


# -------------------------
# SALE ROUTES
# -------------------------
class SaleSchema(BaseModel):
    spare_part_id: int
    quantity: int

@app.post("/sale")
def create_sale(sale: SaleSchema, db=Depends(get_db)):
    new_sale = Sale(
        spare_part_id=sale.spare_part_id,
        quantity=sale.quantity
    )
    db.add(new_sale)
    db.commit()
    return {"message": "Sale recorded successfully"}

@app.get("/sale")
def get_sales(db=Depends(get_db)):
    return db.query(Sale).all()
