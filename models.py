from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# -------------------------
# DATABASE SETUP
# -------------------------
engine = create_engine("sqlite:///autoparts.db", echo=True)
Session = sessionmaker(bind=engine)

# Dependency for FastAPI
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

# Base class for models
Base = declarative_base()

# -------------------------
# CATEGORY TABLE
# -------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)

    # One category -> many spare parts
    spare_parts = relationship("SparePart", back_populates="category")


# -------------------------
# SPAREPART TABLE
# -------------------------
class SparePart(Base):
    __tablename__ = "spareparts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.now)

    # Relationship back to category
    category = relationship("Category", back_populates="spare_parts")

    # Spare part can have many sales
    sales = relationship("Sale", back_populates="spare_part")


# -------------------------
# SALE TABLE
# -------------------------
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    spare_part_id = Column(Integer, ForeignKey("spareparts.id"))
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship to spare part
    spare_part = relationship("SparePart", back_populates="sales")


# -------------------------
# CREATE TABLES
# -------------------------
Base.metadata.create_all(bind=engine)
