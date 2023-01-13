from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    birth_date = Column(Date)
    sexe = Column(String)
    image = Column(String)
    disabled = Column(Boolean)

    wardrobe = relationship("Clothes", back_populates="owner")
    event = relationship("Events", back_populates="owner")

    
class Clothes(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image = Column(String)
    weather = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("category.id"))

    owner = relationship("User", back_populates="wardrobe")
    category = relationship("Category", back_populates="items")


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="event")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    items = relationship("Clothes", back_populates="category")

