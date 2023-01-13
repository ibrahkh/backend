from fastapi import APIRouter, Depends
from typing import List
import schemas, models, oauth2
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import and_

router = APIRouter(prefix="/categories", tags=["categories"])


#CRUD functions 


def get_category_list(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


#END CRUD functions 



@router.post("/", response_model=schemas.Category)
def Create_category(
    category: schemas.CategoryCreate, db: Session = Depends(get_db)
):
    return create_category(db=db, category=category)


@router.get("/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = get_category_list(db, skip=skip, limit=limit)
    return categories

@router.get("/{categorie_id}", response_model=List[schemas.ShowItems])
def read_one_categories(category_id: int,skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_active_user)):
    categories = db.query(models.Category).filter(and_(models.Category.id==category_id)).offset(skip).limit(limit).all()
    return categories